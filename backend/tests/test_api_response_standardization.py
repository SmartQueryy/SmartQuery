"""
Test API Response Standardization (Task B24)

Tests to ensure all API endpoints return consistent ApiResponse format
and that error responses are properly standardized.
"""

import pytest
import json
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app
from models.response_schemas import ApiResponse


class TestAPIResponseStandardization:
    """Test suite for API response standardization"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_root_endpoint_response_format(self, client):
        """Test root endpoint returns standardized ApiResponse format"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        # Validate ApiResponse structure
        assert "success" in data
        assert "data" in data
        assert "error" in data or data.get("error") is None
        assert "message" in data or data.get("message") is None

        # Validate successful response
        assert data["success"] is True
        assert data["data"] is not None
        assert "message" in data["data"]
        assert "status" in data["data"]

    def test_health_endpoint_response_format(self, client):
        """Test health endpoint returns standardized ApiResponse format"""
        response = client.get("/health/")

        assert response.status_code == 200
        data = response.json()

        # Validate ApiResponse structure
        assert "success" in data
        assert "data" in data
        assert data["success"] is True
        assert data["data"] is not None

        # Validate HealthStatus structure
        health_data = data["data"]
        assert "status" in health_data
        assert "service" in health_data
        assert "version" in health_data
        assert "timestamp" in health_data
        assert "checks" in health_data
        assert "details" in health_data

        # Validate checks structure
        checks = health_data["checks"]
        assert "database" in checks
        assert "redis" in checks
        assert "storage" in checks
        assert "llm_service" in checks

    def test_health_metrics_endpoint_response_format(self, client):
        """Test health metrics endpoint returns standardized ApiResponse format"""
        response = client.get("/health/metrics")

        assert response.status_code == 200
        data = response.json()

        # Validate ApiResponse structure
        assert "success" in data
        assert "data" in data
        assert data["success"] is True
        assert data["data"] is not None

        # Validate PerformanceMetrics structure
        metrics_data = data["data"]
        assert "timestamp" in metrics_data
        assert "summary" in metrics_data
        assert "operations" in metrics_data
        assert "slowest_operations" in metrics_data
        assert "bottlenecks" in metrics_data
        assert "performance_alerts" in metrics_data

    def test_auth_endpoint_error_response_format(self, client):
        """Test auth endpoint errors return standardized ApiResponse format"""
        # Test invalid request (should trigger error middleware)
        response = client.post("/auth/google", json={})

        # Should be 422 (validation error) or another error code
        assert response.status_code in [400, 422]
        data = response.json()

        # Validate standardized error response
        assert "success" in data
        assert "error" in data
        assert "message" in data
        assert data["success"] is False
        assert data["error"] is not None

    def test_project_endpoint_error_response_format(self, client):
        """Test project endpoint errors return standardized ApiResponse format"""
        # Test accessing projects without authentication
        response = client.get("/projects")

        # Should be 401 (unauthorized)
        assert response.status_code == 401
        data = response.json()

        # Validate standardized error response
        assert "success" in data
        assert "error" in data
        assert "message" in data
        assert data["success"] is False
        assert data["error"] is not None

    def test_chat_endpoint_error_response_format(self, client):
        """Test chat endpoint errors return standardized ApiResponse format"""
        # Test accessing chat without authentication
        fake_project_id = "12345678-1234-1234-1234-123456789012"
        response = client.post(
            f"/chat/{fake_project_id}/message", json={"message": "test"}
        )

        # Should be 401 (unauthorized)
        assert response.status_code == 401
        data = response.json()

        # Validate standardized error response
        assert "success" in data
        assert "error" in data
        assert "message" in data
        assert data["success"] is False
        assert data["error"] is not None

    def test_invalid_endpoint_error_response_format(self, client):
        """Test invalid endpoint returns standardized error response"""
        response = client.get("/invalid/endpoint")

        # Should be 404 (not found)
        assert response.status_code == 404
        data = response.json()

        # Validate standardized error response
        assert "success" in data
        assert "error" in data
        assert "message" in data
        assert data["success"] is False
        assert data["error"] is not None

    def test_all_successful_responses_have_consistent_structure(self, client):
        """Test that all successful responses follow the same structure"""

        # Test endpoints that should work without auth
        endpoints_to_test = ["/", "/health/", "/health/metrics"]

        for endpoint in endpoints_to_test:
            response = client.get(endpoint)

            # Skip if endpoint returns error (focus on successful responses)
            if response.status_code >= 400:
                continue

            data = response.json()

            # Every successful response should have this structure
            assert "success" in data, f"Missing 'success' field in {endpoint}"
            assert "data" in data, f"Missing 'data' field in {endpoint}"
            assert data["success"] is True, f"'success' should be True for {endpoint}"
            assert data["data"] is not None, f"'data' should not be None for {endpoint}"

            # Optional fields should be properly typed if present
            if "error" in data and data["error"] is not None:
                assert isinstance(
                    data["error"], str
                ), f"'error' should be string in {endpoint}"
            if "message" in data and data["message"] is not None:
                assert isinstance(
                    data["message"], str
                ), f"'message' should be string in {endpoint}"

    def test_api_response_model_serialization(self):
        """Test ApiResponse model can be properly serialized"""

        # Test successful response
        success_response = ApiResponse(success=True, data={"test": "value"})
        serialized = success_response.model_dump()

        assert serialized["success"] is True
        assert serialized["data"] == {"test": "value"}
        assert serialized["error"] is None
        assert serialized["message"] is None

        # Test error response
        error_response = ApiResponse(success=False, error="Test error", data=None)
        serialized = error_response.model_dump()

        assert serialized["success"] is False
        assert serialized["error"] == "Test error"
        assert serialized["data"] is None
        assert serialized["message"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
