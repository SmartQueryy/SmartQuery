import uuid
from datetime import datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# Test JWT token for authentication
JWT_SECRET = "mock_secret_key_for_development"
ALGORITHM = "HS256"


def create_test_token(user_id: str = "user_001") -> str:
    """Create test JWT token"""
    to_encode = {"sub": user_id}
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


def test_google_login():
    """Test Google OAuth login endpoint"""
    response = client.post(
        "/auth/google", json={"google_token": "mock_google_token_123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "user" in data["data"]
    assert data["data"]["user"]["email"] == "john.doe@example.com"


def test_get_current_user():
    """Test get current user endpoint"""
    token = create_test_token()
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == "user_001"


def test_get_projects():
    """Test get projects endpoint"""
    token = create_test_token()
    response = client.get(
        "/projects?page=1&limit=10", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]
    assert "total" in data["data"]
    assert len(data["data"]["items"]) >= 0


def test_create_project():
    """Test create project endpoint"""
    token = create_test_token()
    response = client.post(
        "/projects",
        json={"name": "Test Project", "description": "Test description"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["project"]["name"] == "Test Project"
    assert "upload_url" in data["data"]


def test_get_project():
    """Test get single project endpoint"""
    token = create_test_token()
    response = client.get(
        "/projects/project_001", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == "project_001"
    assert data["data"]["name"] == "Sales Data Analysis"


def test_csv_preview():
    """Test CSV preview endpoint"""
    token = create_test_token()
    response = client.get(
        "/chat/project_001/preview", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "columns" in data["data"]
    assert "sample_data" in data["data"]
    assert len(data["data"]["columns"]) > 0


def test_send_message():
    """Test send chat message endpoint"""
    token = create_test_token()
    response = client.post(
        "/chat/project_001/message",
        json={"message": "Show me total sales by product"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data["data"]
    assert "result" in data["data"]
    assert data["data"]["result"]["result_type"] in ["table", "chart", "summary"]


def test_query_suggestions():
    """Test query suggestions endpoint"""
    token = create_test_token()
    response = client.get(
        "/chat/project_001/suggestions", headers={"Authorization": f"Bearer {token}"}
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


def test_logout():
    """Test logout endpoint"""
    token = create_test_token()
    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["message"] == "Logged out successfully"


def test_refresh_token():
    """Test refresh token endpoint"""
    response = client.post(
        "/auth/refresh", json={"refresh_token": "valid_refresh_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


def test_project_status():
    """Test project status endpoint"""
    token = create_test_token()
    response = client.get(
        "/projects/project_001/status", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "status" in data["data"]
    assert "progress" in data["data"]


def test_get_upload_url():
    """Test get upload URL endpoint"""
    token = create_test_token()
    response = client.get(
        "/projects/project_001/upload-url", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "upload_url" in data["data"]


def test_get_messages():
    """Test get chat messages endpoint"""
    token = create_test_token()
    response = client.get(
        "/chat/project_001/messages", headers={"Authorization": f"Bearer {token}"}
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


def test_project_not_found():
    """Test project not found error"""
    token = create_test_token()
    response = client.get(
        "/projects/nonexistent_project", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


def test_chart_query_response():
    """Test that chart queries return appropriate response"""
    token = create_test_token()
    response = client.post(
        "/chat/project_001/message",
        json={"message": "Create a chart showing sales by category"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["result"]["result_type"] == "chart"
    assert "chart_config" in data["data"]["result"]
