import io
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from services.duckdb_service import DuckDBService, duckdb_service


class TestDuckDBService:
    """Test DuckDB service functionality"""

    def test_sql_validation_safe_queries(self):
        """Test SQL validation with safe queries"""
        service = DuckDBService()

        safe_queries = [
            "SELECT * FROM data",
            "SELECT name, age FROM data WHERE age > 18",
            "SELECT COUNT(*) FROM data",
            "SELECT category, SUM(amount) FROM data GROUP BY category",
            "SELECT * FROM data ORDER BY name LIMIT 10",
        ]

        for query in safe_queries:
            is_valid, error = service.validate_sql_query(query)
            assert is_valid, f"Query should be valid: {query}, Error: {error}"
            assert error is None

    def test_sql_validation_dangerous_queries(self):
        """Test SQL validation with dangerous queries"""
        service = DuckDBService()

        dangerous_queries = [
            "DROP TABLE data",
            "DELETE FROM data",
            "INSERT INTO data VALUES (1, 'test')",
            "UPDATE data SET name = 'test'",
            "CREATE TABLE new_table AS SELECT * FROM data",
            "ALTER TABLE data ADD COLUMN new_col TEXT",
        ]

        for query in dangerous_queries:
            is_valid, error = service.validate_sql_query(query)
            assert not is_valid, f"Query should be invalid: {query}"
            assert error is not None
            assert "not allowed" in error

    def test_sql_validation_injection_patterns(self):
        """Test SQL validation with injection patterns"""
        service = DuckDBService()

        injection_queries = [
            "SELECT * FROM data; DROP TABLE users",
            "SELECT * FROM data -- comment",
            "SELECT * FROM data /* comment */",
        ]

        for query in injection_queries:
            is_valid, error = service.validate_sql_query(query)
            assert not is_valid, f"Query should be invalid: {query}"
            assert error is not None

    def test_sql_validation_syntax_errors(self):
        """Test SQL validation with syntax errors"""
        service = DuckDBService()

        invalid_syntax = [
            "SELEC * FROM data",  # Typo
            "SELECT * FORM data",  # Typo
            "SELECT * FROM",  # Incomplete
            "SELECT COUNT( FROM data",  # Incomplete function
        ]

        for query in invalid_syntax:
            is_valid, error = service.validate_sql_query(query)
            assert not is_valid, f"Query should have syntax error: {query}"
            assert error is not None
            assert "syntax error" in error.lower()

    def test_query_info_analysis(self):
        """Test query analysis for metadata"""
        service = DuckDBService()

        # Test aggregated query
        info = service.get_query_info(
            "SELECT category, SUM(amount) FROM data GROUP BY category"
        )
        assert info["is_aggregated"] is True
        assert info["has_grouping"] is True
        assert info["suggested_chart_type"] == "bar"

        # Test simple select
        info = service.get_query_info("SELECT * FROM data")
        assert info["is_aggregated"] is False
        assert info["has_grouping"] is False
        assert info["suggested_chart_type"] is None

        # Test filtered query
        info = service.get_query_info("SELECT * FROM data WHERE age > 18")
        assert info["has_filtering"] is True

        # Test ordered query
        info = service.get_query_info("SELECT * FROM data ORDER BY name")
        assert info["has_order"] is True

    def test_dataframe_to_json_serializable(self):
        """Test DataFrame conversion to JSON-serializable format"""
        service = DuckDBService()

        # Create test DataFrame with various data types
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "score": [95.5, 87.2, None],  # Include None value
                "active": [True, False, True],
                "created_at": pd.to_datetime(
                    ["2024-01-01", "2024-01-02", "2024-01-03"]
                ),
            }
        )

        result = service._dataframe_to_json_serializable(df)

        assert len(result) == 3
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Alice"
        assert result[0]["score"] == 95.5
        assert result[0]["active"] is True
        assert isinstance(result[0]["created_at"], str)  # Should be ISO format

        # Check None handling
        assert result[2]["score"] is None

    @patch("services.duckdb_service.duckdb.connect")
    def test_execute_sql_on_dataframe(self, mock_connect):
        """Test SQL execution on DataFrame"""
        service = DuckDBService()

        # Mock DuckDB connection and result
        mock_conn = Mock()
        mock_result_df = pd.DataFrame(
            {"category": ["A", "B", "C"], "total": [100, 200, 150]}
        )

        mock_execute = Mock()
        mock_execute.fetchdf.return_value = mock_result_df
        mock_conn.execute.return_value = mock_execute
        mock_connect.return_value = mock_conn

        # Test DataFrame
        test_df = pd.DataFrame(
            {"category": ["A", "A", "B", "B", "C"], "amount": [50, 50, 100, 100, 150]}
        )

        result = service._execute_sql_on_dataframe(
            "SELECT category, SUM(amount) as total FROM data GROUP BY category", test_df
        )

        # Verify DuckDB interactions
        mock_connect.assert_called_once_with(":memory:")
        mock_conn.register.assert_called_once_with("data", test_df)
        mock_conn.execute.assert_called_once()
        mock_conn.close.assert_called_once()

        # Verify result
        assert len(result) == 3
        assert result[0]["category"] == "A"
        assert result[0]["total"] == 100

    @patch("services.duckdb_service.storage_service")
    def test_load_csv_data_success(self, mock_storage):
        """Test successful CSV data loading"""
        service = DuckDBService()

        # Mock CSV data
        csv_content = "name,age,city\nAlice,25,NYC\nBob,30,LA"
        csv_bytes = csv_content.encode("utf-8")
        mock_storage.download_file.return_value = csv_bytes

        project = {"id": "test-project", "csv_path": "test/path/data.csv"}

        result_df = service._load_csv_data(project)

        assert result_df is not None
        assert len(result_df) == 2
        assert list(result_df.columns) == ["name", "age", "city"]
        assert result_df.iloc[0]["name"] == "Alice"

        mock_storage.download_file.assert_called_once_with("test/path/data.csv")

    @patch("services.duckdb_service.storage_service")
    def test_load_csv_data_missing_file(self, mock_storage):
        """Test CSV data loading with missing file"""
        service = DuckDBService()

        mock_storage.download_file.return_value = None

        project = {"id": "test-project", "csv_path": "test/missing/data.csv"}

        result_df = service._load_csv_data(project)

        assert result_df is None

    def test_load_csv_data_no_path(self):
        """Test CSV data loading with no CSV path"""
        service = DuckDBService()

        project = {
            "id": "test-project"
            # No csv_path
        }

        result_df = service._load_csv_data(project)

        assert result_df is None

    @patch("services.duckdb_service.storage_service")
    @patch.object(DuckDBService, "_load_csv_data")
    @patch.object(DuckDBService, "_execute_sql_on_dataframe")
    def test_execute_query_success(self, mock_execute_sql, mock_load_csv, mock_storage):
        """Test successful query execution"""
        service = DuckDBService()

        # Use valid UUIDs for testing
        project_id = "12345678-1234-5678-9012-123456789012"
        user_id = "87654321-4321-8765-2109-876543210987"

        # Mock project service
        mock_project = {"id": project_id, "csv_path": "test/data.csv"}
        service.project_service = Mock()
        service.project_service.check_project_ownership.return_value = True
        service.project_service.get_project_by_id.return_value = mock_project

        # Mock CSV loading
        test_df = pd.DataFrame({"name": ["Alice"], "age": [25]})
        mock_load_csv.return_value = test_df

        # Mock SQL execution
        mock_result = [{"name": "Alice", "age": 25}]
        mock_execute_sql.return_value = mock_result

        result_data, execution_time, row_count = service.execute_query(
            "SELECT * FROM data", project_id, user_id
        )

        assert result_data == mock_result
        assert execution_time > 0
        assert row_count == 1

        # Verify method calls with UUID objects
        from uuid import UUID
        service.project_service.check_project_ownership.assert_called_once_with(
            UUID(project_id), UUID(user_id)
        )
        service.project_service.get_project_by_id.assert_called_once_with(UUID(project_id))
        mock_load_csv.assert_called_once_with(mock_project)
        mock_execute_sql.assert_called_once_with("SELECT * FROM data", test_df)

    def test_execute_query_project_not_found(self):
        """Test query execution with project not found"""
        service = DuckDBService()

        # Mock project service returning None
        service.project_service = Mock()
        service.project_service.get_project_by_id.return_value = None

        with pytest.raises(Exception) as exc_info:
            service.execute_query("SELECT * FROM data", "invalid-project", "test-user")

        assert "Project not found" in str(exc_info.value)

    @patch.object(DuckDBService, "_load_csv_data")
    def test_execute_query_csv_not_available(self, mock_load_csv):
        """Test query execution with CSV data not available"""
        service = DuckDBService()

        # Use valid UUIDs for testing
        project_id = "12345678-1234-5678-9012-123456789012"
        user_id = "87654321-4321-8765-2109-876543210987"

        # Mock project service
        mock_project = {"id": project_id}
        service.project_service = Mock()
        service.project_service.check_project_ownership.return_value = True
        service.project_service.get_project_by_id.return_value = mock_project

        # Mock CSV loading failure
        mock_load_csv.return_value = None

        with pytest.raises(ValueError) as exc_info:
            service.execute_query("SELECT * FROM data", project_id, user_id)

        assert "CSV data not available" in str(exc_info.value)


def test_duckdb_service_singleton():
    """Test that duckdb_service is properly initialized"""
    assert duckdb_service is not None
    assert isinstance(duckdb_service, DuckDBService)
