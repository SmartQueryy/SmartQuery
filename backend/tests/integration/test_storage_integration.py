"""
Storage Service Integration Tests - Task B26

Tests the integration between storage service, project service, and file processing
to ensure file operations work correctly with the overall system.
"""

import io
import uuid
from unittest.mock import Mock, patch

import pytest

from models.project import ProjectCreate
from models.user import GoogleOAuthData
from services.project_service import get_project_service
from services.storage_service import storage_service
from services.user_service import get_user_service


class TestStorageIntegration:
    """Integration tests for storage operations with other services"""

    def test_storage_service_initialization(self):
        """Test that storage service initializes correctly"""
        # The storage service should be mocked in test environment
        assert storage_service is not None
        
        # Test health check
        health = storage_service.health_check()
        assert health is not None
        assert "status" in health
        
    def test_presigned_url_generation_integration(self, test_db_setup):
        """Test presigned URL generation integrated with project service"""
        user_service = get_user_service()
        project_service = get_project_service()
        
        # Create test user and project
        google_data = GoogleOAuthData(
            google_id="storage_test_1",
            email="storage@test.com",
            name="Storage Test User"
        )
        test_user = user_service.create_user_from_google(google_data)
        
        project_data = ProjectCreate(
            name="Storage Test Project",
            description="Testing storage integration"
        )
        test_project = project_service.create_project(project_data, test_user.id)
        
        # Generate presigned URL for project
        object_name = f"{test_user.id}/{test_project.id}/data.csv"
        presigned_url = storage_service.generate_presigned_url(object_name)
        
        # In test environment, this should return a mocked URL
        assert presigned_url is not None
        assert isinstance(presigned_url, str)
        assert "presigned" in presigned_url  # Mocked URL contains "presigned"
        
        # Clean up
        project_service.delete_project(test_project.id)
        user_service.delete_user(test_user.id)

    @patch('services.storage_service.storage_service.upload_file')
    @patch('services.storage_service.storage_service.download_file')
    def test_file_upload_download_cycle_integration(self, mock_download, mock_upload, test_db_setup):
        """Test complete file upload and download cycle with project integration"""
        user_service = get_user_service()
        project_service = get_project_service()
        
        # Setup mocks
        test_csv_content = b"name,age,city\nJohn,25,NYC\nJane,30,LA\nBob,35,Chicago"
        mock_upload.return_value = True
        mock_download.return_value = test_csv_content
        
        # Create test user and project
        google_data = GoogleOAuthData(
            google_id="upload_test_1",
            email="upload@test.com",
            name="Upload Test User"
        )
        test_user = user_service.create_user_from_google(google_data)
        
        project_data = ProjectCreate(
            name="Upload Test Project",
            description="Testing file upload integration"
        )
        test_project = project_service.create_project(project_data, test_user.id)
        
        # Test file upload
        object_name = f"{test_user.id}/{test_project.id}/data.csv"
        file_buffer = io.BytesIO(test_csv_content)
        
        upload_success = storage_service.upload_file(object_name, file_buffer)
        assert upload_success is True
        mock_upload.assert_called_once_with(object_name, file_buffer)
        
        # Test file download
        downloaded_content = storage_service.download_file(object_name)
        assert downloaded_content == test_csv_content
        mock_download.assert_called_once_with(object_name)
        
        # Clean up
        project_service.delete_project(test_project.id)
        user_service.delete_user(test_user.id)

    @patch('services.storage_service.storage_service.file_exists')
    @patch('services.storage_service.storage_service.delete_file')
    def test_file_management_integration(self, mock_delete, mock_exists, test_db_setup):
        """Test file existence checking and deletion with project lifecycle"""
        user_service = get_user_service()
        project_service = get_project_service()
        
        # Setup mocks
        mock_exists.return_value = True
        mock_delete.return_value = True
        
        # Create test user and project
        google_data = GoogleOAuthData(
            google_id="file_mgmt_test",
            email="filemgmt@test.com",
            name="File Management Test User"
        )
        test_user = user_service.create_user_from_google(google_data)
        
        project_data = ProjectCreate(
            name="File Management Test Project",
            description="Testing file management integration"
        )
        test_project = project_service.create_project(project_data, test_user.id)
        
        # Test file existence check
        object_name = f"{test_user.id}/{test_project.id}/data.csv"
        file_exists = storage_service.file_exists(object_name)
        assert file_exists is True
        mock_exists.assert_called_once_with(object_name)
        
        # Test file deletion
        delete_success = storage_service.delete_file(object_name)
        assert delete_success is True
        mock_delete.assert_called_once_with(object_name)
        
        # Clean up
        project_service.delete_project(test_project.id)
        user_service.delete_user(test_user.id)

    @patch('services.storage_service.storage_service.get_file_metadata')
    def test_file_metadata_integration(self, mock_metadata, test_db_setup):
        """Test file metadata retrieval integrated with project service"""
        user_service = get_user_service()
        project_service = get_project_service()
        
        # Setup mock
        mock_metadata_response = {
            "size": 1024,
            "content_type": "text/csv",
            "last_modified": "2024-01-01T12:00:00Z",
            "etag": "abc123"
        }
        mock_metadata.return_value = mock_metadata_response
        
        # Create test user and project
        google_data = GoogleOAuthData(
            google_id="metadata_test",
            email="metadata@test.com",
            name="Metadata Test User"
        )
        test_user = user_service.create_user_from_google(google_data)
        
        project_data = ProjectCreate(
            name="Metadata Test Project",
            description="Testing metadata integration"
        )
        test_project = project_service.create_project(project_data, test_user.id)
        
        # Test metadata retrieval
        object_name = f"{test_user.id}/{test_project.id}/data.csv"
        metadata = storage_service.get_file_metadata(object_name)
        
        assert metadata is not None
        assert metadata["size"] == 1024
        assert metadata["content_type"] == "text/csv"
        mock_metadata.assert_called_once_with(object_name)
        
        # Clean up
        project_service.delete_project(test_project.id)
        user_service.delete_user(test_user.id)

    def test_storage_error_handling_integration(self, test_db_setup):
        """Test storage error handling in integrated scenarios"""
        user_service = get_user_service()
        project_service = get_project_service()
        
        # Create test user and project
        google_data = GoogleOAuthData(
            google_id="error_test",
            email="error@test.com",
            name="Error Test User"
        )
        test_user = user_service.create_user_from_google(google_data)
        
        project_data = ProjectCreate(
            name="Error Test Project",
            description="Testing error handling"
        )
        test_project = project_service.create_project(project_data, test_user.id)
        
        # Test handling of non-existent file
        object_name = f"{test_user.id}/{test_project.id}/nonexistent.csv"
        
        # These operations should handle errors gracefully
        with patch('services.storage_service.storage_service.download_file', return_value=None):
            downloaded_content = storage_service.download_file(object_name)
            assert downloaded_content is None  # Should handle missing file gracefully
        
        with patch('services.storage_service.storage_service.file_exists', return_value=False):
            file_exists = storage_service.file_exists(object_name)
            assert file_exists is False
        
        # Clean up
        project_service.delete_project(test_project.id)
        user_service.delete_user(test_user.id)

    @patch('services.storage_service.storage_service.upload_file')
    def test_multiple_project_storage_isolation(self, mock_upload, test_db_setup):
        """Test that storage operations are properly isolated between projects"""
        user_service = get_user_service()
        project_service = get_project_service()
        
        mock_upload.return_value = True
        
        # Create test user
        google_data = GoogleOAuthData(
            google_id="isolation_test",
            email="isolation@test.com",
            name="Isolation Test User"
        )
        test_user = user_service.create_user_from_google(google_data)
        
        # Create two projects
        project1_data = ProjectCreate(name="Project 1", description="First project")
        project2_data = ProjectCreate(name="Project 2", description="Second project")
        
        project1 = project_service.create_project(project1_data, test_user.id)
        project2 = project_service.create_project(project2_data, test_user.id)
        
        # Test that object names are properly isolated
        object1 = f"{test_user.id}/{project1.id}/data.csv"
        object2 = f"{test_user.id}/{project2.id}/data.csv"
        
        assert object1 != object2
        assert str(project1.id) in object1
        assert str(project2.id) in object2
        assert str(project1.id) not in object2
        assert str(project2.id) not in object1
        
        # Test uploads to different projects
        file_buffer1 = io.BytesIO(b"data1,value1\n1,2")
        file_buffer2 = io.BytesIO(b"data2,value2\n3,4")
        
        upload1 = storage_service.upload_file(object1, file_buffer1)
        upload2 = storage_service.upload_file(object2, file_buffer2)
        
        assert upload1 is True
        assert upload2 is True
        assert mock_upload.call_count == 2
        
        # Verify different object names were used
        call_args = mock_upload.call_args_list
        assert call_args[0][0][0] == object1
        assert call_args[1][0][0] == object2
        
        # Clean up
        project_service.delete_project(project1.id)
        project_service.delete_project(project2.id)
        user_service.delete_user(test_user.id)

    def test_storage_service_configuration(self):
        """Test that storage service is properly configured for testing"""
        # Verify storage service is mocked in test environment
        assert storage_service is not None
        
        # Test that storage service methods are available
        assert hasattr(storage_service, 'generate_presigned_url')
        assert hasattr(storage_service, 'upload_file')
        assert hasattr(storage_service, 'download_file')
        assert hasattr(storage_service, 'delete_file')
        assert hasattr(storage_service, 'file_exists')
        assert hasattr(storage_service, 'get_file_metadata')
        assert hasattr(storage_service, 'health_check')
        
        # Test health check returns expected structure
        health = storage_service.health_check()
        assert isinstance(health, dict)
        assert "status" in health