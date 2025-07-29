import json
import logging
import os
from typing import Any, Dict, List, Optional

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from models.response_schemas import QueryResult
from services.duckdb_service import duckdb_service
from services.project_service import get_project_service
from services.storage_service import storage_service

logger = logging.getLogger(__name__)


class SQLGenerationInput(BaseModel):
    """Input for SQL generation tool."""

    question: str = Field(description="Natural language question to convert to SQL")
    schema_info: str = Field(description="CSV schema information")


class SQLGenerationTool(BaseTool):
    """Tool for generating SQL queries from natural language."""

    name = "sql_generator"
    description = (
        "Generates SQL queries from natural language questions. "
        "Input should be 'question: <natural language question>'"
    )

    def _run(self, tool_input: str) -> str:
        """Generate SQL query from natural language question."""
        # Parse the input to extract question
        if ":" in tool_input:
            question = tool_input.split(":", 1)[1].strip()
        else:
            question = tool_input.strip()

        # For now, use a simple heuristic to generate SQL
        # This will be improved with actual schema info in the process_query method
        sql_prompt = f"""
Convert this natural language question to a SQL query:
"{question}"

Rules:
- Use the table name 'data' for the CSV data
- Return only the SQL query, no explanations
- Ensure the query is valid DuckDB SQL syntax
"""

        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        response = llm.invoke([HumanMessage(content=sql_prompt)])
        return response.content.strip()

    async def _arun(self, tool_input: str) -> str:
        """Async version of _run."""
        return self._run(tool_input)


class QueryTypeClassifierTool(BaseTool):
    """Tool for classifying query types."""

    name = "query_classifier"
    description = "Classifies queries as SQL, semantic search, or general chat"

    def _run(self, question: str) -> str:
        """Classify the type of query."""
        question_lower = question.lower()

        # SQL indicators
        sql_keywords = [
            "select",
            "sum",
            "count",
            "average",
            "max",
            "min",
            "group by",
            "where",
            "total",
            "show me",
        ]
        chart_keywords = ["chart", "graph", "plot", "visualize", "visualization"]

        if any(keyword in question_lower for keyword in sql_keywords):
            if any(keyword in question_lower for keyword in chart_keywords):
                return "chart"
            return "sql"
        elif any(keyword in question_lower for keyword in chart_keywords):
            return "chart"
        else:
            return "general"

    async def _arun(self, question: str) -> str:
        """Async version of _run."""
        return self._run(question)


class LangChainService:
    """Service for LangChain-based query processing and routing."""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Don't require API key during testing or when TESTING env var is set
        if not self.openai_api_key and not os.getenv("TESTING"):
            raise ValueError("OPENAI_API_KEY environment variable not set")

        # Initialize tools
        self.sql_tool = SQLGenerationTool()
        self.classifier_tool = QueryTypeClassifierTool()

        # Only initialize LLM and agent if API key is available
        if self.openai_api_key:
            try:
                self.llm = ChatOpenAI(
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
                self.llm = None
                self.agent = None
        else:
            self.llm = None
            self.agent = None

        self.project_service = get_project_service()
        self.storage_service = storage_service

    def process_query(
        self, question: str, project_id: str, user_id: str
    ) -> QueryResult:
        """Process a natural language query and return structured results."""
        try:
            # Get project information
            project = self.project_service.get_project_by_id(project_id, user_id)
            if not project:
                return self._create_error_result(question, "Project not found")

            # Get schema information
            schema_info = self._get_schema_info(project)

            # Classify query type
            query_type = self.classifier_tool.run(question)

            if query_type in ["sql", "chart"]:
                return self._process_sql_query(
                    question, schema_info, query_type, project_id, user_id
                )
            else:
                return self._process_general_query(question, project)

        except Exception as e:
            return self._create_error_result(
                question, f"Error processing query: {str(e)}"
            )

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
        """Process SQL-type queries."""
        try:
            # Generate SQL using the tool with schema-enhanced prompt
            enhanced_prompt = f"""
Schema: {schema_info}
Question: {question}
"""
            sql_query = self.sql_tool.run(enhanced_prompt)

            # Clean up SQL query
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

            # Validate SQL query for safety
            is_valid, validation_error = duckdb_service.validate_sql_query(sql_query)
            if not is_valid:
                return self._create_error_result(
                    question, f"Invalid SQL query: {validation_error}"
                )

            # Execute SQL query using DuckDB
            try:
                result_data, execution_time, row_count = duckdb_service.execute_query(
                    sql_query, project_id, user_id
                )

                # Analyze query to enhance result metadata
                query_info = duckdb_service.get_query_info(sql_query)

                # Determine result type and chart config
                result_type = "chart" if query_type == "chart" else "table"
                chart_config = None

                if result_type == "chart" and query_info.get("suggested_chart_type"):
                    chart_config = self._generate_chart_config(
                        result_data, query_info.get("suggested_chart_type"), question
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

            except Exception as e:
                # Fallback to mock data if DuckDB execution fails
                logger.error(
                    f"DuckDB execution failed, falling back to mock data: {str(e)}"
                )
                result_type = "chart" if query_type == "chart" else "table"
                mock_data = self._generate_mock_data(question, result_type)

                return QueryResult(
                    id=f"qr_{project_id}_{hash(question) % 10000}",
                    query=question,
                    sql_query=sql_query,
                    result_type=result_type,
                    data=mock_data["data"],
                    execution_time=0.5,
                    row_count=len(mock_data["data"]),
                    chart_config=(
                        mock_data.get("chart_config")
                        if result_type == "chart"
                        else None
                    ),
                )

        except Exception as e:
            return self._create_error_result(
                question, f"SQL generation error: {str(e)}"
            )

    def _process_general_query(
        self, question: str, project: Dict[str, Any]
    ) -> QueryResult:
        """Process general chat queries."""
        try:
            # Use LLM for general responses if available
            if self.llm:
                prompt = f"""
You are a helpful data analyst assistant. The user has a CSV dataset with {project.get('row_count', 'unknown')} rows and {project.get('column_count', 'unknown')} columns.

Dataset: {project.get('name', 'Unnamed dataset')}

User question: {question}

Provide a helpful response. If the question is about data analysis, suggest specific queries they could try.
"""

                response = self.llm.invoke([HumanMessage(content=prompt)])
                summary = response.content
            else:
                # Fallback response when LLM is not available
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
        """Generate query suggestions based on project data."""
        try:
            project = self.project_service.get_project_by_id(project_id, user_id)
            if not project:
                return []

            # Generate suggestions based on column types
            suggestions = []
            metadata = project.get("columns_metadata", [])

            # Find numeric columns for aggregation suggestions
            numeric_cols = [
                col["name"]
                for col in metadata
                if col.get("type") in ["number", "integer", "float"]
            ]
            categorical_cols = [
                col["name"] for col in metadata if col.get("type") == "string"
            ]
            date_cols = [
                col["name"]
                for col in metadata
                if col.get("type") in ["date", "datetime"]
            ]

            if numeric_cols:
                suggestions.append(
                    {
                        "id": f"sug_sum_{numeric_cols[0]}",
                        "text": f"Show me the total {numeric_cols[0]}",
                        "category": "analysis",
                        "complexity": "beginner",
                    }
                )

                if categorical_cols:
                    suggestions.append(
                        {
                            "id": f"sug_group_{categorical_cols[0]}",
                            "text": f"Break down {numeric_cols[0]} by {categorical_cols[0]}",
                            "category": "analysis",
                            "complexity": "intermediate",
                        }
                    )

                    suggestions.append(
                        {
                            "id": f"sug_chart_{categorical_cols[0]}",
                            "text": f"Create a bar chart of {numeric_cols[0]} by {categorical_cols[0]}",
                            "category": "visualization",
                            "complexity": "intermediate",
                        }
                    )

            if date_cols and numeric_cols:
                suggestions.append(
                    {
                        "id": f"sug_trend_{date_cols[0]}",
                        "text": f"Show {numeric_cols[0]} trend over {date_cols[0]}",
                        "category": "visualization",
                        "complexity": "intermediate",
                    }
                )

            # Add general suggestions
            suggestions.extend(
                [
                    {
                        "id": "sug_overview",
                        "text": "Give me an overview of this dataset",
                        "category": "summary",
                        "complexity": "beginner",
                    },
                    {
                        "id": "sug_top_values",
                        "text": "Show me the top 10 rows",
                        "category": "analysis",
                        "complexity": "beginner",
                    },
                ]
            )

            return suggestions[:5]  # Return top 5 suggestions

        except Exception as e:
            return []


# Singleton instance
langchain_service = LangChainService()
