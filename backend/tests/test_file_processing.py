from io import StringIO
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from tasks.file_processing import process_csv_file


class TestFileProcessing:
    """Test Celery file processing tasks"""

    @patch("tasks.file_processing.storage_service")
    @patch("tasks.file_processing.get_project_service")
    @patch.object(process_csv_file, "update_state", autospec=True)
    def test_process_csv_file_success(
        self, mock_update_state, mock_project_service, mock_storage_service
    ):
        """Test successful CSV file processing"""
        # Mock project service
        mock_service = Mock()
        mock_project_service.return_value = mock_service

        # Mock storage service
        csv_content = """id,name,email,age
1,John Doe,john@example.com,30
2,Jane Smith,jane@example.com,25
3,Bob Johnson,bob@example.com,35"""

        mock_storage_service.download_file.return_value = csv_content.encode("utf-8")

        # Call the task function directly (not through Celery wrapper)
        result = process_csv_file.run(
            "00000000-0000-0000-0000-000000000001",
            "00000000-0000-0000-0000-000000000002",
        )

        # Verify storage service was called
        mock_storage_service.download_file.assert_called_once_with(
            "00000000-0000-0000-0000-000000000002/00000000-0000-0000-0000-000000000001/data.csv"
        )

        # Verify project service was called
        mock_service.update_project_status.assert_called()
        mock_service.update_project_metadata.assert_called()

        # Verify result
        assert result["project_id"] == "00000000-0000-0000-0000-000000000001"
        assert result["status"] == "completed"
        assert result["row_count"] == 3
        assert result["column_count"] == 4

        # Verify column metadata
        columns_metadata = result["columns_metadata"]
        assert len(columns_metadata) == 4

        # Check that columns are detected
        column_names = [col["name"] for col in columns_metadata]
        assert "id" in column_names
        assert "name" in column_names
        assert "email" in column_names
        assert "age" in column_names

    @patch("tasks.file_processing.storage_service")
    @patch("tasks.file_processing.get_project_service")
    @patch.object(process_csv_file, "update_state", autospec=True)
    def test_process_csv_file_download_failure(
        self, mock_update_state, mock_project_service, mock_storage_service
    ):
        """Test CSV processing when file download fails"""
        # Mock project service
        mock_service = Mock()
        mock_project_service.return_value = mock_service

        # Mock storage service to return None (download failure)
        mock_storage_service.download_file.return_value = None

        # Call the task and expect exception
        with pytest.raises(Exception, match="Failed to download file from storage"):
            process_csv_file.run(
                "00000000-0000-0000-0000-000000000001",
                "00000000-0000-0000-0000-000000000002",
            )

    @patch("tasks.file_processing.storage_service")
    @patch("tasks.file_processing.get_project_service")
    @patch.object(process_csv_file, "update_state", autospec=True)
    @patch("tasks.file_processing.pd.read_csv")
    def test_process_csv_file_parse_failure(
        self,
        mock_pandas_read_csv,
        mock_update_state,
        mock_project_service,
        mock_storage_service,
    ):
        """Test CSV processing when file parsing fails"""
        # Mock project service
        mock_service = Mock()
        mock_project_service.return_value = mock_service

        # Mock storage service to return valid content
        mock_storage_service.download_file.return_value = b"valid,csv,content"

        # Mock pandas to raise an exception
        mock_pandas_read_csv.side_effect = Exception("CSV parsing failed")

        # Call the task and expect exception
        with pytest.raises(Exception, match="Failed to parse CSV"):
            process_csv_file.run(
                "00000000-0000-0000-0000-000000000001",
                "00000000-0000-0000-0000-000000000002",
            )

    @patch("tasks.file_processing.storage_service")
    @patch("tasks.file_processing.get_project_service")
    @patch.object(process_csv_file, "update_state", autospec=True)
    def test_process_csv_file_error_handling(
        self, mock_update_state, mock_project_service, mock_storage_service
    ):
        """Test error handling in CSV processing"""
        # Mock project service to raise exception
        mock_service = Mock()
        mock_service.update_project_status.side_effect = Exception("Database error")
        mock_project_service.return_value = mock_service

        # Mock storage service
        csv_content = """id,name
1,John Doe"""
        mock_storage_service.download_file.return_value = csv_content.encode("utf-8")

        # Call the task and expect exception
        with pytest.raises(Exception, match="Database error"):
            process_csv_file.run(
                "00000000-0000-0000-0000-000000000001",
                "00000000-0000-0000-0000-000000000002",
            )
