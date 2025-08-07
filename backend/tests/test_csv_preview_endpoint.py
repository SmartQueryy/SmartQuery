import uuid
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch
import pytest
from fastapi.testclient import TestClient

from main import app
from middleware.auth_middleware import verify_token
from models.project import ProjectCreate, ProjectStatusEnum
from models.user import GoogleOAuthData, UserInDB
from services.auth_service import AuthService
from services.project_service import get_project_service
from services.user_service import get_user_service

client = TestClient(app)

# Initialize services for testing
auth_service = AuthService()
project_service = get_project_service()
user_service = get_user_service()


def mock_verify_token():
    """Mock verify_token that returns test user UUID as string"""
    return "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def sample_user():
    """Sample user for testing"""
    test_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    return UserInDB(
        id=test_user_id,
        email="test@example.com",
        name="Test User",
        avatar_url="https://example.com/avatar.jpg",
        google_id="google_123",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def test_access_token(sample_user):
    """Create a valid access token for testing"""
    return auth_service.create_access_token(str(sample_user.id), sample_user.email)


@pytest.fixture
def test_user_in_db(sample_user):
    """Ensure test user exists in database"""
    try:
        user_service.create_user_from_google(
            google_data=GoogleOAuthData(
                google_id=sample_user.google_id,
                email=sample_user.email,
                name=sample_user.name,
                avatar_url=sample_user.avatar_url,
            )
        )
    except Exception:
        pass
    return sample_user


@pytest.fixture
def test_project_with_csv(test_user_in_db):
    """Create a test project with CSV data"""
    project_data = ProjectCreate(
        name="CSV Test Dataset", description="Test project with CSV file"
    )
    project = project_service.create_project(project_data, test_user_in_db.id)

    # Mock project with CSV path
    project.csv_path = "test/sample_data.csv"
    project.row_count = 1000
    project.column_count = 4
    project.columns_metadata = [
        {
            "name": "name",
            "type": "string",
            "sample_values": ["Alice", "Bob", "Charlie"],
        },
        {"name": "age", "type": "number", "sample_values": [25, 30, 35]},
        {
            "name": "city",
            "type": "string",
            "sample_values": ["New York", "Los Angeles", "Chicago"],
        },
        {"name": "salary", "type": "number", "sample_values": [75000, 85000, 90000]},
    ]

    return project


class TestCSVPreviewEndpoint:
    """Test CSV preview endpoint - Task B18"""

    def test_csv_preview_from_storage(
        self,
        test_client,
        test_access_token,
        test_user_in_db,
        test_project_with_csv,
    ):
        """Test CSV preview endpoint loading from storage"""
        app.dependency_overrides[verify_token] = mock_verify_token

        # Mock CSV data
        sample_csv = """name,age,city,salary
Alice,25,New York,75000
Bob,30,Los Angeles,85000
Charlie,35,Chicago,90000
Diana,28,Houston,80000
Eve,32,Phoenix,77000"""

        with patch("services.storage_service.storage_service") as mock_storage:
            mock_storage.download_file.return_value = sample_csv.encode("utf-8")

            try:
                response = test_client.get(
                    f"/chat/{test_project_with_csv.id}/preview",
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True

                preview = data["data"]
                assert preview["columns"] == ["name", "age", "city", "salary"]
                assert len(preview["sample_data"]) == 5
                assert preview["total_rows"] == 5
                assert preview["data_types"]["name"] == "string"
                assert preview["data_types"]["age"] == "number"
                assert preview["data_types"]["salary"] == "number"

                # Check sample data
                assert preview["sample_data"][0] == ["Alice", 25, "New York", 75000]
                assert preview["sample_data"][1] == ["Bob", 30, "Los Angeles", 85000]

            finally:
                app.dependency_overrides.clear()

    def test_csv_preview_fallback_to_metadata(
        self,
        test_client,
        test_access_token,
        test_user_in_db,
        test_project_with_csv,
    ):
        """Test CSV preview endpoint falling back to metadata when storage fails"""
        app.dependency_overrides[verify_token] = mock_verify_token

        # Mock project with metadata
        mock_project = Mock()
        mock_project.csv_path = "test/sample.csv"
        mock_project.row_count = 1000
        mock_project.columns_metadata = [
            {
                "name": "name",
                "type": "string",
                "sample_values": ["Alice", "Bob", "Charlie"],
            },
            {"name": "age", "type": "number", "sample_values": [25, 30, 35]},
            {
                "name": "city",
                "type": "string",
                "sample_values": ["New York", "Los Angeles", "Chicago"],
            },
            {
                "name": "salary",
                "type": "number",
                "sample_values": [75000, 85000, 90000],
            },
        ]

        with (
            patch("services.storage_service.storage_service") as mock_storage,
            patch("api.chat.project_service") as mock_project_service,
        ):

            # Mock storage failure
            mock_storage.download_file.return_value = None

            # Mock project service
            mock_project_service.check_project_ownership.return_value = True
            mock_project_service.get_project_by_id.return_value = mock_project

            try:
                response = test_client.get(
                    f"/chat/{test_project_with_csv.id}/preview",
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True

                preview = data["data"]
                assert preview["columns"] == ["name", "age", "city", "salary"]
                assert len(preview["sample_data"]) == 5
                assert preview["total_rows"] == 1000  # From project metadata

                # Should use sample values from metadata
                assert preview["sample_data"][0] == ["Alice", 25, "New York", 75000]

            finally:
                app.dependency_overrides.clear()

    def test_csv_preview_no_csv_path(
        self,
        test_client,
        test_access_token,
        test_user_in_db,
        test_project_with_csv,
    ):
        """Test CSV preview endpoint when project has no CSV path"""
        app.dependency_overrides[verify_token] = mock_verify_token

        # Remove CSV path from project
        test_project_with_csv.csv_path = None

        try:
            response = test_client.get(
                f"/chat/{test_project_with_csv.id}/preview",
                headers={"Authorization": f"Bearer {test_access_token}"},
            )

            assert response.status_code == 404
            data = response.json()
            assert "CSV preview not available" in data["error"]

        finally:
            app.dependency_overrides.clear()

    def test_csv_preview_data_type_detection(
        self,
        test_client,
        test_access_token,
        test_user_in_db,
        test_project_with_csv,
    ):
        """Test data type detection in CSV preview"""
        app.dependency_overrides[verify_token] = mock_verify_token

        # CSV with various data types
        sample_csv = """id,name,active,price,created_date,rating
1,Product A,True,19.99,2024-01-01,4.5
2,Product B,False,29.99,2024-01-02,3.8
3,Product C,True,39.99,2024-01-03,4.2"""

        with patch("services.storage_service.storage_service") as mock_storage:
            mock_storage.download_file.return_value = sample_csv.encode("utf-8")

            try:
                response = test_client.get(
                    f"/chat/{test_project_with_csv.id}/preview",
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()
                preview = data["data"]

                # Verify data type detection
                assert preview["data_types"]["id"] == "number"
                assert preview["data_types"]["name"] == "string"
                assert preview["data_types"]["active"] == "boolean"
                assert preview["data_types"]["price"] == "number"
                assert preview["data_types"]["rating"] == "number"

            finally:
                app.dependency_overrides.clear()

    def test_csv_preview_project_not_found(
        self,
        test_client,
        test_access_token,
        test_user_in_db,
    ):
        """Test CSV preview endpoint with non-existent project"""
        app.dependency_overrides[verify_token] = mock_verify_token

        fake_project_id = "12345678-1234-5678-9012-123456789012"

        try:
            response = test_client.get(
                f"/chat/{fake_project_id}/preview",
                headers={"Authorization": f"Bearer {test_access_token}"},
            )

            assert response.status_code == 404
            data = response.json()
            assert "Project not found" in data["error"]

        finally:
            app.dependency_overrides.clear()

    def test_csv_preview_invalid_project_id(
        self,
        test_client,
        test_access_token,
        test_user_in_db,
    ):
        """Test CSV preview endpoint with invalid project ID format"""
        app.dependency_overrides[verify_token] = mock_verify_token

        invalid_project_id = "invalid-uuid"

        try:
            response = test_client.get(
                f"/chat/{invalid_project_id}/preview",
                headers={"Authorization": f"Bearer {test_access_token}"},
            )

            assert response.status_code == 400
            data = response.json()
            assert "Invalid project ID" in data["error"]

        finally:
            app.dependency_overrides.clear()
