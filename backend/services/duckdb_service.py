import io
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import duckdb
import pandas as pd

from services.project_service import get_project_service
from services.storage_service import storage_service

logger = logging.getLogger(__name__)


class DuckDBService:
    """Service for executing SQL queries on CSV data using DuckDB."""

    def __init__(self):
        self.project_service = get_project_service()
        self.storage_service = storage_service

    def execute_query(
        self, sql_query: str, project_id: str, user_id: str
    ) -> Tuple[List[Dict[str, Any]], float, int]:
        """
        Execute SQL query on project's CSV data using DuckDB.

        Args:
            sql_query: SQL query to execute
            project_id: Project ID containing the CSV data
            user_id: User ID for authorization

        Returns:
            Tuple of (result_data, execution_time, row_count)

        Raises:
            ValueError: If project not found or invalid query
            Exception: If query execution fails
        """
        start_time = datetime.now()

        try:
            # Validate project ID format
            try:
                project_uuid = uuid.UUID(project_id)
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                raise ValueError("Project not found")
            
            # Check project ownership
            if not self.project_service.check_project_ownership(project_uuid, user_uuid):
                raise ValueError("Project not found or access denied")
            
            # Get project information
            project = self.project_service.get_project_by_id(project_uuid)
            if not project:
                raise ValueError("Project not found")

            # Get CSV data from storage
            csv_data = self._load_csv_data(project)
            if csv_data is None:
                raise ValueError("CSV data not available")

            # Execute query using DuckDB
            result_data = self._execute_sql_on_dataframe(sql_query, csv_data)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            row_count = len(result_data)

            logger.info(
                f"Successfully executed query for project {project_id}: {row_count} rows in {execution_time:.3f}s"
            )

            return result_data, execution_time, row_count

        except ValueError as e:
            # Re-raise ValueError with original message for test compatibility
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Query execution failed for project {project_id}: {str(e)}")
            raise e
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Query execution failed for project {project_id}: {str(e)}")
            raise Exception(f"Query execution failed: {str(e)}")

    def _load_csv_data(self, project) -> Optional[pd.DataFrame]:
        """Load CSV data from storage into a pandas DataFrame."""
        try:
            # Get CSV file path from project (handle both object and dict)
            if hasattr(project, 'csv_path'):
                csv_path = project.csv_path
                project_id = project.id
            else:
                csv_path = project.get('csv_path')
                project_id = project.get('id')
                
            if not csv_path:
                logger.error(f"No CSV path found for project {project_id}")
                return None

            # Download CSV data from storage
            csv_bytes = self.storage_service.download_file(csv_path)
            if csv_bytes is None:
                logger.error(f"Failed to download CSV file: {csv_path}")
                return None

            # Convert bytes to DataFrame
            csv_buffer = io.BytesIO(csv_bytes)
            df = pd.read_csv(csv_buffer)

            logger.info(f"Loaded CSV data: {len(df)} rows, {len(df.columns)} columns")
            return df

        except Exception as e:
            logger.error(f"Error loading CSV data: {str(e)}")
            return None

    def _execute_sql_on_dataframe(
        self, sql_query: str, df: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """Execute SQL query on DataFrame using DuckDB."""
        try:
            # Create DuckDB connection
            conn = duckdb.connect(":memory:")

            # Register DataFrame as a table named 'data'
            conn.register("data", df)

            # Execute the query
            result = conn.execute(sql_query).fetchdf()

            # Convert result to list of dictionaries
            result_data = self._dataframe_to_json_serializable(result)

            # Close connection
            conn.close()

            return result_data

        except Exception as e:
            logger.error(f"DuckDB query execution failed: {str(e)}")
            raise Exception(f"SQL execution error: {str(e)}")

    def _dataframe_to_json_serializable(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DataFrame to JSON-serializable list of dictionaries."""
        try:
            # Replace NaN values with None (JSON null)
            df_clean = df.where(pd.notnull(df), None)

            # Convert to list of dictionaries
            result_data = df_clean.to_dict("records")

            # Ensure all values are JSON serializable
            serializable_data = []
            for row in result_data:
                serializable_row = {}
                for key, value in row.items():
                    if pd.isna(value):
                        serializable_row[key] = None
                    elif isinstance(value, (pd.Timestamp, datetime)):
                        serializable_row[key] = value.isoformat()
                    elif isinstance(value, (pd.Int64Dtype, pd.Float64Dtype)):
                        serializable_row[key] = None if pd.isna(value) else value
                    else:
                        serializable_row[key] = value
                serializable_data.append(serializable_row)

            return serializable_data

        except Exception as e:
            logger.error(f"Error converting DataFrame to JSON: {str(e)}")
            raise Exception(f"Data serialization error: {str(e)}")

    def validate_sql_query(self, sql_query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL query for safety and syntax.

        Args:
            sql_query: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Basic security checks
            dangerous_keywords = [
                "DROP",
                "DELETE",
                "INSERT",
                "UPDATE",
                "ALTER",
                "CREATE",
                "TRUNCATE",
                "REPLACE",
                "MERGE",
                "COPY",
                "ATTACH",
                "DETACH",
            ]

            sql_upper = sql_query.upper()
            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    return False, f"Dangerous operation '{keyword}' not allowed"

            # Check for basic SQL injection patterns
            injection_patterns = [";", "--", "/*", "*/", "xp_", "sp_"]
            for pattern in injection_patterns:
                if pattern in sql_query.lower():
                    return False, f"Potentially unsafe pattern '{pattern}' detected"

            # Validate syntax using DuckDB (dry run)
            try:
                conn = duckdb.connect(":memory:")
                # Create a dummy table for syntax validation with common columns
                conn.execute("CREATE TABLE data AS SELECT 1 as id, 'test' as name, 25 as age, 'category' as category, 100.0 as amount")
                # Prepare the query (this validates syntax without executing)
                conn.execute(f"EXPLAIN {sql_query}")
                conn.close()

            except Exception as e:
                return False, f"SQL syntax error: {str(e)}"

            return True, None

        except Exception as e:
            return False, f"Query validation error: {str(e)}"

    def get_query_info(self, sql_query: str) -> Dict[str, Any]:
        """
        Analyze SQL query to determine result characteristics.

        Args:
            sql_query: SQL query to analyze

        Returns:
            Dictionary with query analysis information
        """
        try:
            sql_lower = sql_query.lower()

            # Determine if query returns aggregated results
            is_aggregated = any(
                keyword in sql_lower
                for keyword in ["sum(", "count(", "avg(", "max(", "min(", "group by"]
            )

            # Determine if query has ordering
            has_order = "order by" in sql_lower

            # Determine if query has grouping
            has_grouping = "group by" in sql_lower

            # Determine if query has filtering
            has_filtering = "where" in sql_lower

            # Suggest visualization type based on query structure
            suggested_chart_type = None
            if has_grouping and is_aggregated:
                if "count(" in sql_lower or "sum(" in sql_lower:
                    suggested_chart_type = "bar"
                elif "avg(" in sql_lower:
                    suggested_chart_type = "line"

            return {
                "is_aggregated": is_aggregated,
                "has_order": has_order,
                "has_grouping": has_grouping,
                "has_filtering": has_filtering,
                "suggested_chart_type": suggested_chart_type,
            }

        except Exception as e:
            logger.error(f"Error analyzing query: {str(e)}")
            return {
                "is_aggregated": False,
                "has_order": False,
                "has_grouping": False,
                "has_filtering": False,
                "suggested_chart_type": None,
            }


# Singleton instance
duckdb_service = DuckDBService()
