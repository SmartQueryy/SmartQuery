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


def test_google_login(test_client, sample_user):
    """Test Google OAuth login endpoint with development mode"""
    mock_access_token = "mock_access_token"
    mock_refresh_token = "mock_refresh_token"
    
    with patch('api.auth.auth_service.login_with_google', return_value=(sample_user, mock_access_token, mock_refresh_token, False)):
        response = test_client.post(
            "/auth/google", json={"google_token": "mock_google_token_123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "user" in data["data"]
        assert data["data"]["user"]["email"] == "test@example.com"


def test_get_current_user(test_client, sample_user, test_access_token):
    """Test get current user endpoint"""
    with patch('middleware.auth_middleware.auth_service.get_current_user', return_value=sample_user):
        response = test_client.get("/auth/me", headers={"Authorization": f"Bearer {test_access_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "test@example.com"


def test_get_projects(test_client, test_access_token):
    """Test get projects endpoint"""
    with patch('api.projects.verify_token'):
        response = test_client.get(
            "/projects?page=1&limit=10", headers={"Authorization": f"Bearer {test_access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert len(data["data"]["items"]) >= 0


def test_create_project(test_client, test_access_token):
    """Test create project endpoint"""
    with patch('api.projects.verify_token'):
        response = test_client.post(
            "/projects",
            json={"name": "Test Project", "description": "Test description"},
            headers={"Authorization": f"Bearer {test_access_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["project"]["name"] == "Test Project"
        assert "upload_url" in data["data"]


def test_get_project(test_client, test_access_token):
    """Test get single project endpoint"""
    with patch('api.projects.verify_token'):
        response = test_client.get(
            "/projects/project_001", headers={"Authorization": f"Bearer {test_access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "project_001"
        assert data["data"]["name"] == "Sales Data Analysis"


def test_csv_preview(test_client, test_access_token):
    """Test CSV preview endpoint"""
    with patch('api.chat.verify_token'):
        response = test_client.get(
            "/chat/project_001/preview", headers={"Authorization": f"Bearer {test_access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "columns" in data["data"]
        assert "sample_data" in data["data"]
        assert len(data["data"]["columns"]) > 0


def test_send_message(test_client, test_access_token):
    """Test send chat message endpoint"""
    with patch('api.chat.verify_token'):
        response = test_client.post(
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


def test_query_suggestions(test_client, test_access_token):
    """Test query suggestions endpoint"""
    with patch('api.chat.verify_token'):
        response = test_client.get(
            "/chat/project_001/suggestions", headers={"Authorization": f"Bearer {test_access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
        assert all("text" in suggestion for suggestion in data["data"])


def test_unauthorized_access(test_client):
    """Test that endpoints require authentication"""
    response = test_client.get("/projects")
    assert response.status_code == 403


def test_invalid_token(test_client):
    """Test invalid token handling"""
    response = test_client.get(
        "/projects", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_logout(test_client, sample_user, test_access_token):
    """Test logout endpoint"""
    with patch('middleware.auth_middleware.auth_service.get_current_user', return_value=sample_user):
        response = test_client.post("/auth/logout", headers={"Authorization": f"Bearer {test_access_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["message"] == "Logged out successfully"


def test_refresh_token(test_client, sample_user):
    """Test refresh token endpoint"""
    mock_refresh_token = "mock_refresh_token"
    mock_new_access_token = "new_access_token"
    with patch('api.auth.auth_service.refresh_access_token', return_value=(mock_new_access_token, sample_user)):
        response = test_client.post(
            "/auth/refresh", json={"refresh_token": mock_refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]


def test_project_status(test_client, test_access_token):
    """Test project status endpoint"""
    with patch('api.projects.verify_token'):
        response = test_client.get(
            "/projects/project_001/status", headers={"Authorization": f"Bearer {test_access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "status" in data["data"]
        assert "progress" in data["data"]


def test_get_upload_url(test_client, test_access_token):
    """Test get upload URL endpoint"""
    with patch('api.projects.verify_token'):
        response = test_client.post(
            "/projects/project_001/upload-url",
            json={"filename": "new_data.csv", "content_type": "text/csv"},
            headers={"Authorization": f"Bearer {test_access_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "upload_url" in data["data"]
        assert "object_path" in data["data"]


def test_get_messages(test_client, test_access_token):
    """Test get chat messages endpoint"""
    with patch('api.chat.verify_token'):
        response = test_client.get(
            "/chat/project_001/messages", headers={"Authorization": f"Bearer {test_access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "items" in data["data"]
        assert len(data["data"]["items"]) >= 0


def test_invalid_google_token(test_client):
    """Test invalid Google token"""
    with patch('api.auth.auth_service.verify_google_token', side_effect=ValueError("Invalid Token")):
        response = test_client.post("/auth/google", json={"google_token": "invalid_token"})
        assert response.status_code == 401


def test_project_not_found(test_client, test_access_token):
    """Test project not found error"""
    with patch('api.projects.verify_token'):
        response = test_client.get(
            "/projects/nonexistent_project", headers={"Authorization": f"Bearer {test_access_token}"}
        )
        assert response.status_code == 404


def test_chart_query_response(test_client, test_access_token):
    """Test chart query response type"""
    with patch('api.chat.verify_token'):
        response = test_client.post(
            "/chat/project_001/message",
            json={"message": "show me a chart"},
            headers={"Authorization": f"Bearer {test_access_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["result"]["result_type"] == "chart"
        assert "chart_config" in data["data"]["result"]
