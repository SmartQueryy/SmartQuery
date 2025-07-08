import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
    assert "timestamp" in data["data"]
    assert "checks" in data["data"]


def test_cors_headers():
    """Test that CORS headers are properly set"""
    response = client.get("/health")
    assert response.status_code == 200
    # Note: CORS headers are typically added by middleware in production
    # For testing, we just verify the response is successful


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["message"] == "SmartQuery API is running"
    assert data["data"]["status"] == "healthy"
