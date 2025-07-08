"""
Integration tests for authentication system
Tests the complete auth flow including endpoints, middleware, and services
"""

import json
import uuid
from datetime import datetime
from unittest.mock import patch, Mock

import pytest
from fastapi.testclient import TestClient

from main import app
from models.user import UserInDB, GoogleOAuthData
from services.auth_service import AuthService

# Test client
client = TestClient(app)

# Auth service for token generation
auth_service = AuthService()


class TestAuthIntegration:
    """Integration tests for authentication endpoints and middleware"""

    @pytest.fixture
    def sample_user(self):
        """Sample user for testing"""
        return UserInDB(
            id=uuid.UUID("12345678-1234-5678-9012-123456789abc"),
            email="integration@example.com",
            name="Integration Test User",
            avatar_url="https://example.com/avatar.jpg",
            google_id="google_integration_123",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.fixture
    def google_oauth_data(self):
        """Sample Google OAuth data"""
        return GoogleOAuthData(
            google_id="google_integration_123",
            email="integration@example.com",
            name="Integration Test User",
            avatar_url="https://example.com/avatar.jpg",
            email_verified=True,
        )

    @pytest.fixture
    def valid_access_token(self, sample_user):
        """Create a valid access token for testing"""
        return auth_service.create_access_token(str(sample_user.id), sample_user.email)

    @pytest.fixture
    def valid_refresh_token(self, sample_user):
        """Create a valid refresh token for testing"""
        return auth_service.create_refresh_token(str(sample_user.id), sample_user.email)

    @pytest.fixture
    def expired_token(self, sample_user):
        """Create an expired token for testing"""
        import jwt
        from datetime import timedelta

        # Create token that expired 1 hour ago
        past_time = datetime.utcnow() - timedelta(hours=1)
        payload = {
            "sub": str(sample_user.id),
            "email": sample_user.email,
            "exp": past_time,
            "type": "access",
        }
        return jwt.encode(
            payload, auth_service.jwt_secret, algorithm=auth_service.algorithm
        )

    def test_google_oauth_login_success(self, sample_user, google_oauth_data):
        """Test successful Google OAuth login flow"""
        with patch(
            "api.auth.auth_service.verify_google_token", return_value=google_oauth_data
        ):
            with patch(
                "api.auth.auth_service.user_service.create_or_update_from_google_oauth",
                return_value=(sample_user, True),
            ):
                with patch(
                    "api.auth.auth_service.user_service.update_last_sign_in",
                    return_value=sample_user,
                ):

                    response = client.post(
                        "/auth/google", json={"google_token": "mock_google_token_123"}
                    )

                    assert response.status_code == 200
                    data = response.json()

                    # Verify response structure matches frontend expectations
                    assert data["success"] is True
                    assert "data" in data
                    assert "message" in data

                    auth_data = data["data"]
                    assert "user" in auth_data
                    assert "access_token" in auth_data
                    assert "refresh_token" in auth_data
                    assert "expires_in" in auth_data

                    # Verify user data structure
                    user_data = auth_data["user"]
                    assert user_data["id"] == str(sample_user.id)
                    assert user_data["email"] == sample_user.email
                    assert user_data["name"] == sample_user.name
                    assert user_data["avatar_url"] == sample_user.avatar_url
                    assert "created_at" in user_data
                    assert "last_sign_in_at" in user_data

                    # Verify token format
                    assert isinstance(auth_data["access_token"], str)
                    assert isinstance(auth_data["refresh_token"], str)
                    assert isinstance(auth_data["expires_in"], int)

    def test_google_oauth_login_invalid_token(self):
        """Test Google OAuth login with invalid token"""
        response = client.post(
            "/auth/google", json={"google_token": "invalid_token_123"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid Google token" in data["detail"]

    def test_google_oauth_login_empty_token(self):
        """Test Google OAuth login with empty token"""
        response = client.post("/auth/google", json={"google_token": ""})

        assert response.status_code == 400
        data = response.json()
        assert "Google token is required" in data["detail"]

    def test_get_current_user_success(self, sample_user, valid_access_token):
        """Test getting current user with valid token"""
        with patch(
            "middleware.auth_middleware.auth_service.get_current_user",
            return_value=sample_user,
        ):

            response = client.get(
                "/auth/me", headers={"Authorization": f"Bearer {valid_access_token}"}
            )

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert data["success"] is True
            assert "data" in data

            user_data = data["data"]
            assert user_data["id"] == str(sample_user.id)
            assert user_data["email"] == sample_user.email
            assert user_data["name"] == sample_user.name

    def test_get_current_user_no_token(self):
        """Test getting current user without token"""
        response = client.get("/auth/me")

        assert (
            response.status_code == 403
        )  # FastAPI returns 403 for missing auth header

    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        response = client.get(
            "/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid or expired token" in data["detail"]

    def test_get_current_user_expired_token(self, expired_token):
        """Test getting current user with expired token"""
        response = client.get(
            "/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid or expired token" in data["detail"]

    def test_refresh_token_success(self, sample_user, valid_refresh_token):
        """Test successful token refresh"""
        with patch(
            "api.auth.auth_service.refresh_access_token",
            return_value=(valid_refresh_token, sample_user),
        ):

            response = client.post(
                "/auth/refresh", json={"refresh_token": valid_refresh_token}
            )

            assert response.status_code == 200
            data = response.json()

            # Verify response structure matches frontend expectations
            assert data["success"] is True
            assert "data" in data
            assert "message" in data

            auth_data = data["data"]
            assert "user" in auth_data
            assert "access_token" in auth_data
            assert "refresh_token" in auth_data
            assert "expires_in" in auth_data

    def test_refresh_token_invalid(self):
        """Test token refresh with invalid refresh token"""
        response = client.post(
            "/auth/refresh", json={"refresh_token": "invalid_refresh_token"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid or expired refresh token" in data["detail"]

    def test_refresh_token_empty(self):
        """Test token refresh with empty refresh token"""
        response = client.post("/auth/refresh", json={"refresh_token": ""})

        assert response.status_code == 400
        data = response.json()
        assert "Refresh token is required" in data["detail"]

    def test_logout_success(self, sample_user, valid_access_token):
        """Test successful logout"""
        with patch(
            "middleware.auth_middleware.auth_service.get_current_user",
            return_value=sample_user,
        ):

            response = client.post(
                "/auth/logout",
                headers={"Authorization": f"Bearer {valid_access_token}"},
            )

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert data["success"] is True
            assert "data" in data
            assert "message" in data
            assert data["data"]["message"] == "Logged out successfully"

    def test_logout_no_token(self):
        """Test logout without token"""
        response = client.post("/auth/logout")

        assert (
            response.status_code == 403
        )  # FastAPI returns 403 for missing auth header

    def test_logout_invalid_token(self):
        """Test logout with invalid token"""
        response = client.post(
            "/auth/logout", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid or expired token" in data["detail"]

    def test_auth_health_check(self):
        """Test authentication service health check"""
        with patch("api.auth.auth_service.health_check") as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "jwt_working": True,
                "google_oauth": {"google_client_id_configured": True},
                "user_service": {"status": "healthy"},
            }

            response = client.get("/auth/health")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert "data" in data
            assert "message" in data
            assert data["data"]["status"] == "healthy"

    def test_auth_health_check_unhealthy(self):
        """Test authentication service health check when unhealthy"""
        with patch("api.auth.auth_service.health_check") as mock_health:
            mock_health.return_value = {
                "status": "unhealthy",
                "jwt_working": False,
                "error": "JWT service error",
            }

            response = client.get("/auth/health")

            assert response.status_code == 503
            data = response.json()
            assert "Authentication service is unhealthy" in data["detail"]


class TestAuthMiddlewareIntegration:
    """Test middleware integration with protected endpoints"""

    @pytest.fixture
    def sample_user(self):
        """Sample user for testing"""
        return UserInDB(
            id=uuid.UUID("12345678-1234-5678-9012-123456789abc"),
            email="middleware@example.com",
            name="Middleware Test User",
            avatar_url="https://example.com/avatar.jpg",
            google_id="google_middleware_123",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.fixture
    def valid_access_token(self, sample_user):
        """Create a valid access token for testing"""
        return auth_service.create_access_token(str(sample_user.id), sample_user.email)

    def test_middleware_authentication_success(self, sample_user, valid_access_token):
        """Test that middleware properly authenticates valid tokens"""
        with patch(
            "middleware.auth_middleware.auth_service.get_current_user",
            return_value=sample_user,
        ):

            # Test with a protected endpoint (auth/me uses the middleware)
            response = client.get(
                "/auth/me", headers={"Authorization": f"Bearer {valid_access_token}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_middleware_authentication_failure(self):
        """Test that middleware properly rejects invalid tokens"""
        response = client.get(
            "/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid or expired token" in data["detail"]

    def test_middleware_no_authorization_header(self):
        """Test that middleware handles missing authorization header"""
        response = client.get("/auth/me")

        assert (
            response.status_code == 403
        )  # FastAPI security returns 403 for missing header

    def test_middleware_malformed_authorization_header(self):
        """Test that middleware handles malformed authorization header"""
        response = client.get(
            "/auth/me", headers={"Authorization": "InvalidFormat token123"}
        )

        assert response.status_code == 403  # FastAPI security validation

    def test_middleware_bearer_token_extraction(self, sample_user, valid_access_token):
        """Test that middleware properly extracts Bearer tokens"""
        with patch(
            "middleware.auth_middleware.auth_service.get_current_user",
            return_value=sample_user,
        ):

            response = client.get(
                "/auth/me", headers={"Authorization": f"Bearer {valid_access_token}"}
            )

            assert response.status_code == 200


class TestAPIResponseFormat:
    """Test that API responses match frontend expectations"""

    def test_success_response_format(self, sample_user):
        """Test that success responses have the expected format"""
        with patch("api.auth.auth_service.login_with_google") as mock_login:
            mock_login.return_value = (
                sample_user,
                "access_token",
                "refresh_token",
                True,
            )

            response = client.post(
                "/auth/google", json={"google_token": "mock_google_token_123"}
            )

            assert response.status_code == 200
            data = response.json()

            # Check required fields for frontend API client
            required_fields = ["success", "data", "message"]
            for field in required_fields:
                assert field in data

            assert data["success"] is True
            assert isinstance(data["data"], dict)
            assert isinstance(data["message"], str)

    def test_error_response_format(self):
        """Test that error responses have the expected format"""
        response = client.post("/auth/google", json={"google_token": "invalid_token"})

        assert response.status_code == 401
        data = response.json()

        # FastAPI error format
        assert "detail" in data
        assert isinstance(data["detail"], str)

    def test_user_data_format(self, sample_user):
        """Test that user data format matches frontend expectations"""
        with patch("api.auth.auth_service.login_with_google") as mock_login:
            mock_login.return_value = (
                sample_user,
                "access_token",
                "refresh_token",
                True,
            )

            response = client.post(
                "/auth/google", json={"google_token": "mock_google_token_123"}
            )

            assert response.status_code == 200
            data = response.json()

            user_data = data["data"]["user"]

            # Check required user fields for frontend
            required_user_fields = ["id", "email", "name", "avatar_url", "created_at"]
            for field in required_user_fields:
                assert field in user_data

            # Check data types
            assert isinstance(user_data["id"], str)
            assert isinstance(user_data["email"], str)
            assert isinstance(user_data["name"], str)
            assert user_data["avatar_url"] is None or isinstance(
                user_data["avatar_url"], str
            )
            assert isinstance(user_data["created_at"], str)

    def test_token_data_format(self, sample_user):
        """Test that token data format matches frontend expectations"""
        with patch("api.auth.auth_service.login_with_google") as mock_login:
            mock_login.return_value = (
                sample_user,
                "test_access_token",
                "test_refresh_token",
                True,
            )

            response = client.post(
                "/auth/google", json={"google_token": "mock_google_token_123"}
            )

            assert response.status_code == 200
            data = response.json()

            auth_data = data["data"]

            # Check required auth fields for frontend
            required_auth_fields = ["access_token", "refresh_token", "expires_in"]
            for field in required_auth_fields:
                assert field in auth_data

            # Check data types
            assert isinstance(auth_data["access_token"], str)
            assert isinstance(auth_data["refresh_token"], str)
            assert isinstance(auth_data["expires_in"], int)


class TestErrorHandling:
    """Test comprehensive error handling scenarios"""

    def test_google_oauth_service_error(self):
        """Test handling of Google OAuth service errors"""
        with patch(
            "api.auth.auth_service.verify_google_token",
            side_effect=Exception("Google service unavailable"),
        ):

            response = client.post(
                "/auth/google", json={"google_token": "mock_google_token_123"}
            )

            assert response.status_code == 500
            data = response.json()
            assert "Authentication failed" in data["detail"]

    def test_database_error_handling(self, sample_user):
        """Test handling of database errors during authentication"""
        google_oauth_data = GoogleOAuthData(
            google_id="google_123",
            email="test@example.com",
            name="Test User",
            email_verified=True,
        )

        with patch(
            "api.auth.auth_service.verify_google_token", return_value=google_oauth_data
        ):
            with patch(
                "api.auth.auth_service.user_service.create_or_update_from_google_oauth",
                side_effect=Exception("Database connection failed"),
            ):

                response = client.post(
                    "/auth/google", json={"google_token": "mock_google_token_123"}
                )

                assert response.status_code == 500
                data = response.json()
                assert "Authentication failed" in data["detail"]

    def test_jwt_service_error_handling(self):
        """Test handling of JWT service errors"""
        with patch(
            "middleware.auth_middleware.auth_service.verify_token",
            side_effect=Exception("JWT service error"),
        ):

            response = client.get(
                "/auth/me", headers={"Authorization": "Bearer some_token"}
            )

            assert response.status_code == 500
            data = response.json()
            assert "Authentication service error" in data["detail"]
