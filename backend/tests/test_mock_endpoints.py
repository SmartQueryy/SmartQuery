import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from models.user import GoogleOAuthData, UserInDB
from services.auth_service import AuthService

client = TestClient(app)

# Initialize auth service for testing
auth_service = AuthService()


@pytest.fixture(autouse=True)
def mock_database_operations():
    """Automatically mock database operations for all tests"""
    with (
        patch(
            "api.auth.auth_service.user_service.get_user_by_email"
        ) as mock_get_by_email,
        patch("api.auth.auth_service.user_service.get_user_by_id") as mock_get_by_id,
        patch(
            "api.auth.auth_service.user_service.create_or_update_from_google_oauth"
        ) as mock_oauth,
        patch("api.auth.auth_service.user_service.update_last_sign_in") as mock_sign_in,
        patch("api.projects.MOCK_PROJECTS") as mock_projects,
        patch("api.chat.MOCK_CHAT_MESSAGES") as mock_chat,
    ):

        # Default mock user - use UUID that we'll also patch in MOCK_PROJECTS
        test_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        test_user_id_str = str(test_user_id)

        default_user = UserInDB(
            id=test_user_id,
            email="test@example.com",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg",
            google_id="mock_google_123",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Mock projects data with our test user ID
        mock_projects_data = {
            "project_001": {
                "id": "project_001",
                "user_id": test_user_id_str,
                "name": "Sales Data Analysis",
                "description": "Monthly sales data from Q4 2024",
                "csv_filename": "sales_data.csv",
                "csv_path": f"{test_user_id_str}/project_001/sales_data.csv",
                "row_count": 1000,
                "column_count": 8,
                "columns_metadata": [
                    {
                        "name": "date",
                        "type": "date",
                        "nullable": False,
                        "sample_values": ["2024-01-01", "2024-01-02", "2024-01-03"],
                        "unique_count": 365,
                    },
                    {
                        "name": "product_name",
                        "type": "string",
                        "nullable": False,
                        "sample_values": ["Product A", "Product B", "Product C"],
                        "unique_count": 50,
                    },
                ],
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T10:30:00Z",
                "status": "ready",
            }
        }
        mock_projects.clear()
        mock_projects.update(mock_projects_data)

        # Initialize empty chat messages
        mock_chat.clear()

        mock_get_by_email.return_value = default_user
        mock_get_by_id.return_value = default_user
        mock_oauth.return_value = (default_user, True)
        mock_sign_in.return_value = default_user

        yield {
            "get_by_email": mock_get_by_email,
            "get_by_id": mock_get_by_id,
            "oauth": mock_oauth,
            "sign_in": mock_sign_in,
            "default_user": default_user,
            "test_user_id": test_user_id_str,
        }


@pytest.fixture
def sample_user():
    """Sample user for testing - uses UUID that matches our mock project ownership"""
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


def test_google_login():
    """Test Google OAuth login endpoint with development mode"""
    with patch.dict("os.environ", {"ENVIRONMENT": "development"}):
        with patch("api.auth.auth_service.google_client_id", "mock_client_id"):
            response = client.post(
                "/auth/google", json={"google_token": "mock_google_token_123"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "access_token" in data["data"]
            assert "user" in data["data"]
            assert data["data"]["user"]["email"] == "test@example.com"


def test_get_current_user(sample_user, test_access_token):
    """Test get current user endpoint"""
    response = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {test_access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "test@example.com"


def test_get_projects(sample_user, test_access_token):
    """Test get projects endpoint"""
    response = client.get(
        "/projects?page=1&limit=10",
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]
    assert "total" in data["data"]
    assert len(data["data"]["items"]) >= 0


def test_create_project(sample_user, test_access_token):
    """Test create project endpoint"""
    response = client.post(
        "/projects",
        json={"name": "Test Project", "description": "Test description"},
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["project"]["name"] == "Test Project"
    assert "upload_url" in data["data"]


def test_get_project(sample_user, test_access_token):
    """Test get single project endpoint"""
    response = client.get(
        "/projects/project_001",
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == "project_001"
    assert data["data"]["name"] == "Sales Data Analysis"


def test_csv_preview(sample_user, test_access_token):
    """Test CSV preview endpoint"""
    response = client.get(
        "/chat/project_001/preview",
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "columns" in data["data"]
    assert "sample_data" in data["data"]
    assert len(data["data"]["columns"]) > 0


def test_send_message(sample_user, test_access_token):
    """Test send chat message endpoint"""
    response = client.post(
        "/chat/project_001/message",
        json={"message": "Show me total sales by product"},
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data["data"]
    assert "result" in data["data"]
    assert data["data"]["result"]["result_type"] in ["table", "chart", "summary"]


def test_query_suggestions(sample_user, test_access_token):
    """Test query suggestions endpoint"""
    response = client.get(
        "/chat/project_001/suggestions",
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0
    assert all("text" in suggestion for suggestion in data["data"])


def test_unauthorized_access():
    """Test that endpoints require authentication"""
    response = client.get("/projects")
    assert response.status_code == 403


def test_invalid_token():
    """Test invalid token handling"""
    response = client.get(
        "/projects", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_logout(sample_user, test_access_token):
    """Test logout endpoint"""
    response = client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {test_access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["message"] == "Logged out successfully"


def test_refresh_token(sample_user):
    """Test refresh token endpoint"""
    test_refresh_token = auth_service.create_refresh_token(
        str(sample_user.id), sample_user.email
    )
    response = client.post("/auth/refresh", json={"refresh_token": test_refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


def test_project_status(sample_user, test_access_token):
    """Test project status endpoint"""
    response = client.get(
        "/projects/project_001/status",
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "status" in data["data"]
    assert "progress" in data["data"]


def test_get_upload_url(sample_user, test_access_token):
    """Test get upload URL endpoint"""
    response = client.get(
        "/projects/project_001/upload-url",
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "upload_url" in data["data"]


def test_get_messages(sample_user, test_access_token):
    """Test get chat messages endpoint"""
    response = client.get(
        "/chat/project_001/messages",
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]
    assert "total" in data["data"]


def test_invalid_google_token():
    """Test invalid Google token"""
    response = client.post("/auth/google", json={"google_token": "invalid_token"})
    assert response.status_code == 401


def test_project_not_found(sample_user, test_access_token):
    """Test project not found error"""
    response = client.get(
        "/projects/nonexistent_project",
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 404


def test_chart_query_response(sample_user, test_access_token):
    """Test that chart queries return appropriate response"""
    response = client.post(
        "/chat/project_001/message",
        json={"message": "Create a chart showing sales by category"},
        headers={"Authorization": f"Bearer {test_access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["result"]["result_type"] == "chart"
    assert "chart_config" in data["data"]["result"]
