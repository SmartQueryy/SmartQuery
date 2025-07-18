import pytest
import pandas as pd
from unittest.mock import Mock, patch
from io import StringIO

from tasks.file_processing import process_csv_file


class TestFileProcessing:
    """Test Celery file processing tasks"""

    @patch('tasks.file_processing.storage_service')
    @patch('tasks.file_processing.get_project_service')
    @patch.object(process_csv_file, 'update_state', autospec=True)
    def test_process_csv_file_success(self, mock_update_state, mock_project_service, mock_storage_service):
        """Test successful CSV file processing"""
        # Mock project service
        mock_service = Mock()
        mock_project_service.return_value = mock_service
        
        # Mock storage service
        csv_content = """id,name,email,age
1,John Doe,john@example.com,30
2,Jane Smith,jane@example.com,25
3,Bob Johnson,bob@example.com,35"""
        
        mock_storage_service.download_file.return_value = csv_content.encode('utf-8')
        
        # Call the task function directly (not through Celery wrapper)
        result = process_csv_file.run("test-project-id", "test-user-id")
        
        # Verify storage service was called
        mock_storage_service.download_file.assert_called_once_with("test-user-id/test-project-id/data.csv")
        
        # Verify project service was called
        mock_service.update_project_status.assert_called()
        mock_service.update_project_metadata.assert_called()
        
        # Verify result
        assert result["project_id"] == "test-project-id"
        assert result["status"] == "completed"
        assert result["row_count"] == 3
        assert result["column_count"] == 4
        
        # Verify column metadata
        columns_metadata = result["columns_metadata"]
        assert len(columns_metadata) == 4
        
        # Check specific columns
        id_col = next(col for col in columns_metadata if col["name"] == "id")
        assert id_col["type"] == "number"
        assert id_col["nullable"] is False
        
        name_col = next(col for col in columns_metadata if col["name"] == "name")
        assert name_col["type"] == "string"
        assert name_col["nullable"] is False
        
        age_col = next(col for col in columns_metadata if col["name"] == "age")
        assert age_col["type"] == "number"
        assert age_col["nullable"] is False

    @patch('tasks.file_processing.storage_service')
    @patch('tasks.file_processing.get_project_service')
    @patch.object(process_csv_file, 'update_state', autospec=True)
    def test_process_csv_file_download_failure(self, mock_update_state, mock_project_service, mock_storage_service):
        """Test CSV processing when file download fails"""
        # Mock project service
        mock_service = Mock()
        mock_project_service.return_value = mock_service
        
        # Mock storage service to return None (download failure)
        mock_storage_service.download_file.return_value = None
        
        # Call the task and expect exception
        with pytest.raises(Exception, match="Failed to download file from storage"):
            process_csv_file.run("test-project-id", "test-user-id")

    @patch('tasks.file_processing.storage_service')
    @patch('tasks.file_processing.get_project_service')
    @patch.object(process_csv_file, 'update_state', autospec=True)
    def test_process_csv_file_parse_failure(self, mock_update_state, mock_project_service, mock_storage_service):
        """Test CSV processing when file parsing fails"""
        # Mock project service
        mock_service = Mock()
        mock_project_service.return_value = mock_service
        
        # Mock storage service to return invalid CSV
        mock_storage_service.download_file.return_value = b"invalid,csv,content"
        
        # Call the task and expect exception
        with pytest.raises(Exception, match="Failed to parse CSV"):
            process_csv_file.run("test-project-id", "test-user-id")

    @patch('tasks.file_processing.storage_service')
    @patch('tasks.file_processing.get_project_service')
    @patch.object(process_csv_file, 'update_state', autospec=True)
    def test_process_csv_file_with_null_values(self, mock_update_state, mock_project_service, mock_storage_service):
        """Test CSV processing with null values"""
        # Mock project service
        mock_service = Mock()
        mock_project_service.return_value = mock_service
        
        # Mock storage service with CSV containing null values
        csv_content = """id,name,email,age
1,John Doe,john@example.com,30
2,Jane Smith,,25
3,Bob Johnson,bob@example.com,"""
        
        mock_storage_service.download_file.return_value = csv_content.encode('utf-8')
        
        # Call the task function directly (not through Celery wrapper)
        result = process_csv_file.run("test-project-id", "test-user-id")
        
        # Verify result
        assert result["row_count"] == 3
        assert result["column_count"] == 4
        
        # Check that nullable columns are detected
        columns_metadata = result["columns_metadata"]
        email_col = next(col for col in columns_metadata if col["name"] == "email")
        age_col = next(col for col in columns_metadata if col["name"] == "age")
        
        # Both should be nullable due to empty values
        assert email_col["nullable"] is True
        assert age_col["nullable"] is True

    @patch('tasks.file_processing.storage_service')
    @patch('tasks.file_processing.get_project_service')
    @patch.object(process_csv_file, 'update_state', autospec=True)
    def test_process_csv_file_error_handling(self, mock_update_state, mock_project_service, mock_storage_service):
        """Test error handling in CSV processing"""
        # Mock project service to raise exception
        mock_service = Mock()
        mock_service.update_project_status.side_effect = Exception("Database error")
        mock_project_service.return_value = mock_service
        
        # Mock storage service
        csv_content = """id,name
1,John Doe"""
        mock_storage_service.download_file.return_value = csv_content.encode('utf-8')
        
        # Call the task and expect exception
        with pytest.raises(Exception, match="Database error"):
            process_csv_file.run("test-project-id", "test-user-id") 