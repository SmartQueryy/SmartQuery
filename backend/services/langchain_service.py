import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from models.response_schemas import QueryResult
from middleware.monitoring import track_performance
from services.duckdb_service import duckdb_service
from services.embeddings_service import get_embeddings_service
from services.suggestions_service import get_suggestions_service
from services.project_service import get_project_service
from services.storage_service import storage_service

logger = logging.getLogger(__name__)


class SQLGenerationInput(BaseModel):
    """Input for SQL generation tool."""

    question: str = Field(description="Natural language question to convert to SQL")
    schema_info: str = Field(description="CSV schema information")


class SQLGenerationTool(BaseTool):
    """Enhanced tool for generating sophisticated SQL queries from natural language."""

    name = "sql_generator"
    description = (
        "Generates optimized SQL queries from natural language questions with schema awareness. "
        "Input format: 'Schema: <schema_info>\nQuestion: <natural language question>'"
    )

    def _run(self, tool_input: str) -> str:
        """Generate SQL query with enhanced prompting and schema awareness."""
        # Parse input to extract schema and question
        lines = tool_input.strip().split("\n")
        schema_info = ""
        question = ""

        for line in lines:
            if line.startswith("Schema:"):
                schema_info = line.replace("Schema:", "").strip()
            elif line.startswith("Question:"):
                question = line.replace("Question:", "").strip()

        # Fallback parsing for legacy format
        if not question and ":" in tool_input:
            question = tool_input.split(":", 1)[1].strip()
        elif not question:
            question = tool_input.strip()

        # Enhanced SQL generation prompt with better instructions
        sql_prompt = f"""
You are an expert SQL analyst. Convert this natural language question to a precise DuckDB SQL query.

DATABASE SCHEMA:
{schema_info if schema_info else "Table: data (columns will be inferred from context)"}

QUESTION: {question}

INSTRUCTIONS:
1. Use table name 'data' for the CSV data
2. Generate only the SQL query - no explanations or markdown
3. Use proper DuckDB syntax and functions
4. For aggregations, include appropriate GROUP BY clauses
5. Use LIMIT for "top N" queries (default LIMIT 10 for large results)
6. Handle case-insensitive column matching when possible
7. Use appropriate date/time functions for temporal queries
8. For statistical queries, use DuckDB's statistical functions
9. Ensure the query is executable and returns meaningful results

SQL QUERY:"""

        try:
            llm = ChatOpenAI(
                temperature=0, model="gpt-4o-mini"
            )  # Use more capable model
            response = llm.invoke([HumanMessage(content=sql_prompt)])
            sql_query = response.content.strip()

            # Clean up common formatting issues
            sql_query = sql_query.replace("```sql", "").replace("```", "")
            sql_query = sql_query.replace("SQL QUERY:", "").strip()

            return sql_query
        except Exception as e:
            # Fallback to simpler model
            llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
            response = llm.invoke([HumanMessage(content=sql_prompt)])
            return response.content.strip().replace("```sql", "").replace("```", "")

    async def _arun(self, tool_input: str) -> str:
        """Async version of _run."""
        return self._run(tool_input)


class QueryTypeClassifierTool(BaseTool):
    """Enhanced tool for classifying query types with better accuracy."""

    name = "query_classifier"
    description = "Classifies queries as SQL, semantic search, chart, or general chat with high accuracy"

    def _run(self, question: str) -> str:
        """Classify the type of query using enhanced logic."""
        question_lower = question.lower()

        # Enhanced keyword classification with weights
        aggregation_keywords = [
            "sum",
            "total",
            "count",
            "average",
            "mean",
            "avg",
            "maximum",
            "max",
            "minimum",
            "min",
            "group by",
            "group",
            "aggregate",
            "statistics",
            "stats",
        ]

        filtering_keywords = [
            "where",
            "filter",
            "display",
            "find",
            "get",
            "select",
            "rows",
            "records",
            "data",
            "entries",
            "values",
        ]

        chart_keywords = [
            "chart",
            "graph",
            "plot",
            "visualize",
            "visualization",
            "draw",
            "create chart",
            "show chart",
            "bar chart",
            "line chart",
            "pie chart",
            "histogram",
            "scatter",
            "trend",
            "distribution",
        ]

        analytical_keywords = [
            "analyze",
            "analysis",
            "compare",
            "comparison",
            "correlation",
            "relationship",
            "pattern",
            "trend",
            "insight",
            "breakdown",
        ]

        conversational_keywords = [
            "what is",
            "tell me",
            "explain",
            "describe",
            "how",
            "why",
            "help",
            "about",
            "overview",
            "summary",
            "understand",
        ]

        # "show me" is special - it can be either SQL or general depending on context
        show_me_sql_patterns = [
            "total",
            "sum",
            "count",
            "average",
            "max",
            "min",
            "data",
            "rows",
        ]

        # Calculate scores for each category
        sql_score = 0
        chart_score = 0
        general_score = 0

        # Check for SQL indicators
        if any(keyword in question_lower for keyword in aggregation_keywords):
            sql_score += 3
        if any(keyword in question_lower for keyword in filtering_keywords):
            sql_score += 2
        if any(keyword in question_lower for keyword in analytical_keywords):
            sql_score += 1

        # Special handling for "show me" patterns with data operations
        if "show me" in question_lower:
            if any(keyword in question_lower for keyword in show_me_sql_patterns):
                sql_score += 2  # "show me total", "show me count" etc.
                # Don't add to general score for these data-specific queries

        # Check for chart indicators
        if any(keyword in question_lower for keyword in chart_keywords):
            chart_score += 4
        if (
            any(keyword in question_lower for keyword in aggregation_keywords)
            and chart_score > 0
        ):
            chart_score += 2

        # Check for general/conversational indicators
        has_show_me_sql = "show me" in question_lower and any(
            keyword in question_lower for keyword in show_me_sql_patterns
        )

        if any(keyword in question_lower for keyword in conversational_keywords):
            general_score += 3  # Increased weight for conversational keywords
        if len(question.split()) > 10:  # Longer questions tend to be conversational
            general_score += 1
        if "understand" in question_lower or "explain" in question_lower:
            general_score += 2  # Strong indicators for general queries

        # Don't give general points for "show me" if it's used with SQL patterns
        if not has_show_me_sql and "show me" in question_lower:
            general_score += 1

        # Decision logic with improved accuracy
        if chart_score >= 4:
            return "chart"
        elif sql_score >= 4:  # Strong SQL indicators
            return "sql"
        elif general_score >= 4:  # Strong general indicators
            return "general"
        elif sql_score >= 2 and any(
            keyword in question_lower for keyword in aggregation_keywords
        ):
            return "sql"
        elif "?" in question and general_score > 0:
            return "general"
        else:
            # Default based on which has higher score
            if sql_score > general_score:
                return "sql"
            elif general_score > sql_score:
                return "general"
            return "sql" if sql_score > 0 else "general"

    async def _arun(self, question: str) -> str:
        """Async version of _run."""
        return self._run(question)


class QueryComplexityAnalyzer:
    """Analyzes query complexity to determine optimal processing approach."""

    @staticmethod
    def analyze_complexity(question: str, schema_info: str = "") -> Dict[str, Any]:
        """Analyze query complexity and return processing recommendations."""
        question_lower = question.lower()

        complexity_score = 0
        requires_joins = False
        requires_aggregation = False
        requires_filtering = False
        estimated_result_size = "small"

        # Check for complex operations
        if any(word in question_lower for word in ["join", "merge", "combine"]):
            complexity_score += 3
            requires_joins = True

        if any(
            word in question_lower
            for word in ["group", "aggregate", "sum", "count", "average"]
        ):
            complexity_score += 2
            requires_aggregation = True

        if any(word in question_lower for word in ["where", "filter", "condition"]):
            complexity_score += 1
            requires_filtering = True

        # Estimate result size
        if any(word in question_lower for word in ["all", "everything", "entire"]):
            estimated_result_size = "large"
        elif any(word in question_lower for word in ["top", "first", "limit"]):
            estimated_result_size = "small"
        else:
            estimated_result_size = "medium"

        # Determine complexity level
        if complexity_score >= 5:
            complexity_level = "high"
        elif complexity_score >= 2:
            complexity_level = "medium"
        else:
            complexity_level = "low"

        return {
            "complexity_level": complexity_level,
            "complexity_score": complexity_score,
            "requires_joins": requires_joins,
            "requires_aggregation": requires_aggregation,
            "requires_filtering": requires_filtering,
            "estimated_result_size": estimated_result_size,
            "processing_time_estimate": (
                "fast"
                if complexity_score < 3
                else "medium" if complexity_score < 6 else "slow"
            ),
        }


class LangChainService:
    """Enhanced service for sophisticated LangChain-based query processing and routing."""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Don't require API key during testing or when TESTING env var is set
        if not self.openai_api_key and not os.getenv("TESTING"):
            raise ValueError("OPENAI_API_KEY environment variable not set")

        # Initialize enhanced tools
        self.sql_tool = SQLGenerationTool()
        self.classifier_tool = QueryTypeClassifierTool()
        self.complexity_analyzer = QueryComplexityAnalyzer()

        # Only initialize LLM and agent if API key is available
        if self.openai_api_key:
            try:
                # Use more capable model for better results
                self.llm = ChatOpenAI(
                    temperature=0,
                    model="gpt-4o-mini",  # Upgraded model
                    openai_api_key=self.openai_api_key,
                )

                # Fallback LLM for when main model fails
                self.fallback_llm = ChatOpenAI(
                    temperature=0,
                    model="gpt-3.5-turbo",
                    openai_api_key=self.openai_api_key,
                )

                self.tools = [self.sql_tool, self.classifier_tool]
                self.agent = initialize_agent(
                    self.tools,
                    self.llm,
                    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                    verbose=False,
                    max_iterations=3,
                )
            except Exception as e:
                # Fallback for testing or when OpenAI is not available
                logger.warning(f"Failed to initialize LLM: {str(e)}")
                self.llm = None
                self.fallback_llm = None
                self.agent = None
        else:
            self.llm = None
            self.fallback_llm = None
            self.agent = None

        self.project_service = get_project_service()
        self.storage_service = storage_service

    @track_performance("langchain_query_processing")
    def process_query(
        self, question: str, project_id: str, user_id: str
    ) -> QueryResult:
        """Process a natural language query and return structured results."""
        try:
            # Load real project data
            try:
                project_uuid = uuid.UUID(project_id)
                user_uuid = uuid.UUID(user_id)

                # Check project ownership
                if not self.project_service.check_project_ownership(
                    project_uuid, user_uuid
                ):
                    return self._create_error_result(
                        question, "Project not found or access denied"
                    )

                # Get project information
                project_obj = self.project_service.get_project_by_id(project_uuid)
                if not project_obj:
                    return self._create_error_result(question, "Project not found")

                # Convert project object to dict for compatibility
                project = {
                    "id": str(project_obj.id),
                    "name": project_obj.name,
                    "row_count": project_obj.row_count,
                    "column_count": project_obj.column_count,
                    "columns_metadata": project_obj.columns_metadata or [],
                }

            except ValueError:
                return self._create_error_result(question, "Invalid project ID format")
            except Exception as e:
                # Fallback to mock project data if real data loading fails
                logger.warning(f"Failed to load project data, using mock: {str(e)}")
                project = {
                    "id": project_id,
                    "name": "Sample Dataset",
                    "row_count": 1000,
                    "column_count": 8,
                    "columns_metadata": [
                        {
                            "name": "date",
                            "type": "date",
                            "sample_values": ["2024-01-01", "2024-01-02"],
                        },
                        {
                            "name": "product_name",
                            "type": "string",
                            "sample_values": ["Product A", "Product B"],
                        },
                        {
                            "name": "sales_amount",
                            "type": "number",
                            "sample_values": [1500.0, 2300.5],
                        },
                        {
                            "name": "category",
                            "type": "string",
                            "sample_values": ["Electronics", "Clothing"],
                        },
                    ],
                }

            # Get enhanced schema information
            schema_info = self._get_enhanced_schema_info(project)

            # Generate embeddings for the project if not already done
            self._ensure_project_embeddings(project_id, user_id)

            # Analyze query complexity
            complexity_analysis = self.complexity_analyzer.analyze_complexity(
                question, schema_info
            )
            logger.info(f"Query complexity analysis: {complexity_analysis}")

            # Enhanced query classification with context
            query_type = self._classify_query_with_context(
                question, schema_info, complexity_analysis
            )
            logger.info(f"Query classified as: {query_type}")

            # Route to appropriate processor based on type and complexity
            if query_type in ["sql", "chart"]:
                return self._process_sql_query_enhanced(
                    question,
                    schema_info,
                    query_type,
                    project_id,
                    user_id,
                    complexity_analysis,
                )
            else:
                return self._process_general_query_enhanced(
                    question, project, project_id, user_id, complexity_analysis
                )

        except Exception as e:
            return self._create_error_result(
                question, f"Error processing query: {str(e)}"
            )

    def _get_enhanced_schema_info(self, project: Dict[str, Any]) -> str:
        """Extract enhanced schema information with statistics and patterns."""
        if not project.get("columns_metadata"):
            return "No schema information available"

        schema_lines = ["CSV Schema with Analysis:"]
        schema_lines.append(
            f"Dataset: {project.get('name', 'Unknown')} ({project.get('row_count', 0)} rows, {project.get('column_count', 0)} columns)"
        )
        schema_lines.append("")

        numeric_cols = []
        categorical_cols = []
        date_cols = []

        for col in project["columns_metadata"]:
            col_type = col.get("type", "unknown")
            col_name = col["name"]

            # Categorize columns for better SQL generation
            if col_type in ["number", "integer", "float", "decimal"]:
                numeric_cols.append(col_name)
            elif col_type in ["string", "text", "category"]:
                categorical_cols.append(col_name)
            elif col_type in ["date", "datetime", "timestamp"]:
                date_cols.append(col_name)

            col_info = f"- {col_name} ({col_type})"
            if col.get("sample_values"):
                sample_vals = col["sample_values"][:3]
                col_info += f" - Examples: {sample_vals}"
            schema_lines.append(col_info)

        # Add column type summary for better query generation
        schema_lines.append("")
        schema_lines.append("Column Types Summary:")
        if numeric_cols:
            schema_lines.append(f"- Numeric columns: {', '.join(numeric_cols)}")
        if categorical_cols:
            schema_lines.append(f"- Categorical columns: {', '.join(categorical_cols)}")
        if date_cols:
            schema_lines.append(f"- Date columns: {', '.join(date_cols)}")

        return "\n".join(schema_lines)

    def _classify_query_with_context(
        self, question: str, schema_info: str, complexity_analysis: Dict[str, Any]
    ) -> str:
        """Enhanced query classification using context and complexity analysis."""
        # Start with basic classification
        base_type = self.classifier_tool.run(question)

        # Enhance classification based on complexity and context
        if complexity_analysis.get("requires_aggregation") and base_type != "chart":
            # If aggregation is needed but not explicitly a chart, default to SQL
            return "sql"
        elif (
            complexity_analysis.get("complexity_level") == "high"
            and base_type == "general"
        ):
            # High complexity general queries might benefit from structured processing
            return "sql"
        elif "trend" in question.lower() or "over time" in question.lower():
            # Time-based queries are good candidates for charts
            return "chart"

        return base_type

    def _process_sql_query_enhanced(
        self,
        question: str,
        schema_info: str,
        query_type: str,
        project_id: str,
        user_id: str,
        complexity_analysis: Dict[str, Any],
    ) -> QueryResult:
        """Enhanced SQL query processing with better error handling and optimization."""
        try:
            # Use enhanced prompt format for better SQL generation
            enhanced_prompt = f"Schema: {schema_info}\nQuestion: {question}"

            # Try main LLM first, fallback to secondary if needed
            sql_query = None
            try:
                sql_query = self.sql_tool.run(enhanced_prompt)
            except Exception as e:
                logger.warning(f"Main SQL generation failed: {str(e)}, trying fallback")
                if self.fallback_llm:
                    # Use simpler prompt for fallback
                    simple_prompt = f"Convert to SQL (table name 'data'): {question}"
                    response = self.fallback_llm.invoke(
                        [HumanMessage(content=simple_prompt)]
                    )
                    sql_query = response.content.strip()

            if not sql_query:
                return self._create_error_result(
                    question, "Failed to generate SQL query"
                )

            # Clean up SQL query
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

            # Add complexity-based optimizations
            if complexity_analysis.get("estimated_result_size") == "large":
                if "LIMIT" not in sql_query.upper():
                    sql_query += " LIMIT 1000"  # Prevent huge result sets

            logger.info(f"Generated SQL query: {sql_query}")

            # Validate SQL query before execution
            is_valid, error_msg = duckdb_service.validate_sql_query(sql_query)
            if not is_valid:
                return self._create_error_result(
                    question, f"Invalid SQL query: {error_msg}"
                )

            # Execute SQL query using DuckDB service
            try:
                result_data, execution_time, row_count = duckdb_service.execute_query(
                    sql_query, project_id, user_id
                )

                # Determine result type and generate chart config if needed
                result_type = "chart" if query_type == "chart" else "table"
                chart_config = None

                if result_type == "chart" and result_data:
                    # Generate enhanced chart configuration
                    query_info = duckdb_service.get_query_info(sql_query)
                    suggested_chart_type = query_info.get("suggested_chart_type", "bar")
                    chart_config = self._generate_enhanced_chart_config(
                        result_data, suggested_chart_type, question, complexity_analysis
                    )

                return QueryResult(
                    id=f"qr_{project_id}_{hash(question) % 10000}",
                    query=question,
                    sql_query=sql_query,
                    result_type=result_type,
                    data=result_data,
                    execution_time=execution_time,
                    row_count=row_count,
                    chart_config=chart_config,
                )

            except Exception as db_error:
                return self._create_error_result(
                    question, f"Query execution failed: {str(db_error)}"
                )

        except Exception as e:
            return self._create_error_result(
                question, f"Enhanced SQL processing error: {str(e)}"
            )

    def _process_general_query_enhanced(
        self,
        question: str,
        project: Dict[str, Any],
        project_id: str,
        user_id: str,
        complexity_analysis: Dict[str, Any],
    ) -> QueryResult:
        """Enhanced general query processing with better context and semantic search."""
        try:
            # Perform semantic search with enhanced parameters
            embeddings_service = get_embeddings_service()

            # Adjust search parameters based on complexity
            top_k = 5 if complexity_analysis.get("complexity_level") == "high" else 3
            semantic_results = embeddings_service.semantic_search(
                project_id, user_id, question, top_k=top_k
            )

            # Build enhanced context from semantic search results
            context_parts = []
            if semantic_results:
                context_parts.append("Relevant information from your dataset:")
                for i, result in enumerate(semantic_results, 1):
                    context_parts.append(
                        f"{i}. {result['text']} (relevance: {result['similarity']:.2f})"
                    )

            # Use enhanced LLM processing if available
            if self.llm:
                context_str = "\n".join(context_parts) if context_parts else ""

                # Enhanced prompt with better instructions
                prompt = f"""
You are an expert data analyst assistant. The user has a CSV dataset with the following characteristics:

Dataset: {project.get('name', 'Unnamed dataset')}
Rows: {project.get('row_count', 'unknown')}
Columns: {project.get('column_count', 'unknown')}
Query Complexity: {complexity_analysis.get('complexity_level', 'unknown')}

{context_str}

User question: {question}

Provide a comprehensive and helpful response that:
1. Addresses the user's specific question
2. Uses the relevant dataset information provided above
3. Suggests specific actionable insights or queries they could try
4. Explains any patterns or relationships you notice in the data
5. Recommends visualization approaches if applicable

Keep your response conversational but informative.
"""

                try:
                    response = self.llm.invoke([HumanMessage(content=prompt)])
                    summary = response.content
                except Exception as e:
                    logger.warning(f"Main LLM failed for general query: {str(e)}")
                    if self.fallback_llm:
                        response = self.fallback_llm.invoke(
                            [HumanMessage(content=prompt)]
                        )
                        summary = response.content
                    else:
                        raise e
            else:
                # Enhanced fallback response
                if semantic_results:
                    relevant_info = semantic_results[0]["text"]
                    summary = f"Based on your dataset analysis, I found this relevant information: {relevant_info}. Your dataset '{project.get('name', 'your data')}' contains {project.get('row_count', 'unknown')} rows and {project.get('column_count', 'unknown')} columns. I can help you analyze patterns, create visualizations, or answer specific questions about your data."
                else:
                    summary = f"I can help you analyze your dataset '{project.get('name', 'your data')}' with {project.get('row_count', 'unknown')} rows and {project.get('column_count', 'unknown')} columns. Try asking specific questions about trends, patterns, or requesting visualizations of your data!"

            return QueryResult(
                id=f"qr_general_{hash(question) % 10000}",
                query=question,
                result_type="summary",
                summary=summary,
                execution_time=0.3,
                row_count=0,
            )

        except Exception as e:
            return self._create_error_result(
                question, f"Enhanced general query error: {str(e)}"
            )

    def _generate_enhanced_chart_config(
        self,
        result_data: List[Dict[str, Any]],
        chart_type: str,
        question: str,
        complexity_analysis: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Generate enhanced chart configuration with better logic."""
        try:
            if not result_data:
                return None

            # Get column names from first row
            columns = list(result_data[0].keys())
            if len(columns) < 2:
                return None

            # Enhanced axis determination logic
            x_axis = columns[0]
            y_axis = columns[1]

            # Smarter column assignment based on data types and names
            for col in columns:
                col_lower = col.lower()
                # Look for better x-axis candidates (categorical or date columns)
                if any(
                    keyword in col_lower
                    for keyword in [
                        "name",
                        "category",
                        "type",
                        "date",
                        "time",
                        "month",
                        "year",
                    ]
                ):
                    x_axis = col
                    break

            for col in columns:
                col_lower = col.lower()
                # Look for better y-axis candidates (numeric columns)
                if any(
                    keyword in col_lower
                    for keyword in [
                        "count",
                        "sum",
                        "total",
                        "amount",
                        "value",
                        "avg",
                        "average",
                    ]
                ):
                    y_axis = col
                    break

            # Enhanced chart type selection based on data characteristics
            if complexity_analysis.get("requires_aggregation") and chart_type == "bar":
                # Keep bar chart for aggregated data
                pass
            elif len(result_data) > 20 and any(
                "date" in col.lower() or "time" in col.lower() for col in columns
            ):
                chart_type = "line"  # Line charts for time series with many points
            elif len(result_data) <= 5:
                chart_type = "pie"  # Pie charts for small categorical data

            # Enhanced title generation
            title = (
                question.replace("Create a", "")
                .replace("Show me a", "")
                .replace("chart", "")
                .strip()
            )
            if not title or len(title) < 3:
                title = f"{chart_type.title()} Chart of {y_axis} by {x_axis}"

            return {
                "type": chart_type,
                "x_axis": x_axis,
                "y_axis": y_axis,
                "title": title.title(),
                "data_points": len(result_data),
                "complexity": complexity_analysis.get("complexity_level", "unknown"),
            }

        except Exception as e:
            logger.error(f"Error generating enhanced chart config: {str(e)}")
            return None

    def _get_schema_info(self, project: Dict[str, Any]) -> str:
        """Extract schema information from project metadata."""
        if not project.get("columns_metadata"):
            return "No schema information available"

        schema_lines = ["CSV Schema:"]
        for col in project["columns_metadata"]:
            col_info = f"- {col['name']} ({col.get('type', 'unknown')})"
            if col.get("sample_values"):
                sample_vals = col["sample_values"][:3]  # First 3 sample values
                col_info += f" - Examples: {sample_vals}"
            schema_lines.append(col_info)

        return "\n".join(schema_lines)

    def _process_sql_query(
        self,
        question: str,
        schema_info: str,
        query_type: str,
        project_id: str,
        user_id: str,
    ) -> QueryResult:
        """Process SQL-type queries using DuckDB."""
        try:
            # Generate SQL using the tool with schema-enhanced prompt
            enhanced_prompt = f"""
Schema: {schema_info}
Question: {question}
"""
            sql_query = self.sql_tool.run(enhanced_prompt)

            # Clean up SQL query
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

            # Validate SQL query before execution
            is_valid, error_msg = duckdb_service.validate_sql_query(sql_query)
            if not is_valid:
                return self._create_error_result(
                    question, f"Invalid SQL query: {error_msg}"
                )

            # Execute SQL query using DuckDB service
            try:
                result_data, execution_time, row_count = duckdb_service.execute_query(
                    sql_query, project_id, user_id
                )

                # Determine result type and generate chart config if needed
                result_type = "chart" if query_type == "chart" else "table"
                chart_config = None

                if result_type == "chart" and result_data:
                    # Generate chart configuration based on query analysis
                    query_info = duckdb_service.get_query_info(sql_query)
                    suggested_chart_type = query_info.get("suggested_chart_type", "bar")
                    chart_config = self._generate_chart_config(
                        result_data, suggested_chart_type, question
                    )

                return QueryResult(
                    id=f"qr_{project_id}_{hash(question) % 10000}",
                    query=question,
                    sql_query=sql_query,
                    result_type=result_type,
                    data=result_data,
                    execution_time=execution_time,
                    row_count=row_count,
                    chart_config=chart_config,
                )

            except Exception as db_error:
                # If DuckDB execution fails, return error result
                return self._create_error_result(
                    question, f"Query execution failed: {str(db_error)}"
                )

        except Exception as e:
            return self._create_error_result(
                question, f"SQL generation error: {str(e)}"
            )

    def _process_general_query(
        self, question: str, project: Dict[str, Any], project_id: str, user_id: str
    ) -> QueryResult:
        """Process general chat queries with semantic search enhancement."""
        try:
            # Perform semantic search to find relevant context
            embeddings_service = get_embeddings_service()
            semantic_results = embeddings_service.semantic_search(
                project_id, user_id, question, top_k=3
            )

            # Build context from semantic search results
            context_parts = []
            if semantic_results:
                context_parts.append("Relevant information from your dataset:")
                for result in semantic_results:
                    context_parts.append(
                        f"- {result['text']} (similarity: {result['similarity']:.2f})"
                    )

            # Use LLM for general responses if available
            if self.llm:
                context_str = "\n".join(context_parts) if context_parts else ""

                prompt = f"""
You are a helpful data analyst assistant. The user has a CSV dataset with {project.get('row_count', 'unknown')} rows and {project.get('column_count', 'unknown')} columns.

Dataset: {project.get('name', 'Unnamed dataset')}

{context_str}

User question: {question}

Provide a helpful response using the relevant dataset information above. If the question is about data analysis, suggest specific queries they could try based on the available columns and data.
"""

                response = self.llm.invoke([HumanMessage(content=prompt)])
                summary = response.content
            else:
                # Fallback response when LLM is not available
                if semantic_results:
                    relevant_info = semantic_results[0]["text"]
                    summary = f"Based on your dataset, I found this relevant information: {relevant_info}. I can help you analyze your dataset '{project.get('name', 'your data')}' with {project.get('row_count', 'unknown')} rows and {project.get('column_count', 'unknown')} columns."
                else:
                    summary = f"I can help you analyze your dataset '{project.get('name', 'your data')}' with {project.get('row_count', 'unknown')} rows and {project.get('column_count', 'unknown')} columns. Try asking specific questions about your data!"

            return QueryResult(
                id=f"qr_general_{hash(question) % 10000}",
                query=question,
                result_type="summary",
                summary=summary,
                execution_time=0.3,
                row_count=0,
            )

        except Exception as e:
            return self._create_error_result(question, f"General query error: {str(e)}")

    def _generate_mock_data(self, question: str, result_type: str) -> Dict[str, Any]:
        """Generate mock data for testing purposes."""
        question_lower = question.lower()

        if "sales" in question_lower and result_type == "chart":
            return {
                "data": [
                    {"category": "Electronics", "total_sales": 45000.50},
                    {"category": "Clothing", "total_sales": 32300.25},
                    {"category": "Home", "total_sales": 28900.75},
                    {"category": "Sports", "total_sales": 15450.00},
                ],
                "chart_config": {
                    "type": "bar",
                    "x_axis": "category",
                    "y_axis": "total_sales",
                    "title": "Sales by Category",
                },
            }
        elif "total" in question_lower or "sum" in question_lower:
            return {
                "data": [
                    {"product_name": "Product A", "total_sales": 15000.50},
                    {"product_name": "Product B", "total_sales": 12300.25},
                    {"product_name": "Product C", "total_sales": 9890.75},
                ]
            }
        else:
            return {
                "data": [
                    {"date": "2024-01-01", "value": 1500.00},
                    {"date": "2024-01-02", "value": 2300.50},
                    {"date": "2024-01-03", "value": 1890.25},
                ]
            }

    def _generate_chart_config(
        self, result_data: List[Dict[str, Any]], chart_type: str, question: str
    ) -> Optional[Dict[str, Any]]:
        """Generate chart configuration based on result data and chart type."""
        try:
            if not result_data:
                return None

            # Get column names from first row
            columns = list(result_data[0].keys())
            if len(columns) < 2:
                return None

            # Determine x and y axes based on data types and column names
            x_axis = columns[0]  # First column as x-axis
            y_axis = columns[1]  # Second column as y-axis

            # Look for more meaningful column names
            for col in columns:
                col_lower = col.lower()
                if any(
                    keyword in col_lower
                    for keyword in ["name", "category", "type", "date"]
                ):
                    x_axis = col
                    break

            for col in columns:
                col_lower = col.lower()
                if any(
                    keyword in col_lower
                    for keyword in ["count", "sum", "total", "amount", "value"]
                ):
                    y_axis = col
                    break

            # Generate title from question
            title = (
                question.replace("Create a", "")
                .replace("Show me a", "")
                .replace("chart", "")
                .strip()
            )
            if not title:
                title = f"{chart_type.title()} Chart"

            return {
                "type": chart_type,
                "x_axis": x_axis,
                "y_axis": y_axis,
                "title": title.title(),
            }

        except Exception as e:
            logger.error(f"Error generating chart config: {str(e)}")
            return None

    def _create_error_result(self, question: str, error_message: str) -> QueryResult:
        """Create an error result."""
        return QueryResult(
            id=f"qr_error_{hash(question) % 10000}",
            query=question,
            result_type="error",
            error=error_message,
            execution_time=0.0,
            row_count=0,
        )

    def generate_suggestions(
        self, project_id: str, user_id: str
    ) -> List[Dict[str, Any]]:
        """Generate query suggestions using the dedicated suggestions service."""
        try:
            suggestions_service = get_suggestions_service()
            return suggestions_service.generate_suggestions(project_id, user_id)
        except Exception as e:
            logger.error(f"Error generating suggestions via service: {str(e)}")
            return []

    def _ensure_project_embeddings(self, project_id: str, user_id: str):
        """Ensure embeddings exist for a project, generate if needed"""
        try:
            # Check if embeddings already exist
            embeddings_service = get_embeddings_service()
            stats = embeddings_service.get_embedding_stats(project_id, user_id)

            if stats.get("embedding_count", 0) == 0:
                # Generate embeddings if they don't exist
                logger.info(f"Generating embeddings for project {project_id}")
                success = embeddings_service.generate_project_embeddings(
                    project_id, user_id
                )
                if success:
                    logger.info(
                        f"Successfully generated embeddings for project {project_id}"
                    )
                else:
                    logger.warning(
                        f"Failed to generate embeddings for project {project_id}"
                    )
            else:
                logger.debug(
                    f"Embeddings already exist for project {project_id} ({stats['embedding_count']} embeddings)"
                )

        except Exception as e:
            logger.error(f"Error ensuring project embeddings: {str(e)}")


# Singleton instance
langchain_service = LangChainService()
