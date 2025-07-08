import os
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import jwt
import pytest
from google.auth.transport import requests
from google.oauth2 import id_token

from models.user import GoogleOAuthData, UserInDB
from services.auth_service import AuthService, TokenData


class TestAuthService:
    """Test suite for AuthService"""

    @pytest.fixture
    def auth_service(self):
        """Auth service instance for testing"""
        return AuthService()

    @pytest.fixture
    def sample_user(self):
        """Sample user for testing"""
        return UserInDB(
            id=uuid.uuid4(),
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
    def google_oauth_data(self):
        """Sample Google OAuth data"""
        return GoogleOAuthData(
            google_id="google_123",
            email="test@example.com",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg",
            email_verified=True,
        )

    def test_create_access_token(self, auth_service):
        """Test access token creation"""
        user_id = "test_user_123"
        email = "test@example.com"

        token = auth_service.create_access_token(user_id, email)

        # Verify token can be decoded
        payload = jwt.decode(
            token, auth_service.jwt_secret, algorithms=[auth_service.algorithm]
        )
        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert payload["type"] == "access"

    def test_create_refresh_token(self, auth_service):
        """Test refresh token creation"""
        user_id = "test_user_123"
        email = "test@example.com"

        token = auth_service.create_refresh_token(user_id, email)

        # Verify token can be decoded
        payload = jwt.decode(
            token, auth_service.jwt_secret, algorithms=[auth_service.algorithm]
        )
        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert payload["type"] == "refresh"

    def test_verify_access_token_success(self, auth_service):
        """Test successful access token verification"""
        user_id = "test_user_123"
        email = "test@example.com"

        token = auth_service.create_access_token(user_id, email)
        token_data = auth_service.verify_token(token, "access")

        assert isinstance(token_data, TokenData)
        assert token_data.user_id == user_id
        assert token_data.email == email

    def test_verify_refresh_token_success(self, auth_service):
        """Test successful refresh token verification"""
        user_id = "test_user_123"
        email = "test@example.com"

        token = auth_service.create_refresh_token(user_id, email)
        token_data = auth_service.verify_token(token, "refresh")

        assert isinstance(token_data, TokenData)
        assert token_data.user_id == user_id
        assert token_data.email == email

    def test_verify_invalid_token(self, auth_service):
        """Test invalid token verification"""
        with pytest.raises(jwt.InvalidTokenError):
            auth_service.verify_token("invalid_token")

    def test_verify_wrong_token_type(self, auth_service):
        """Test verifying token with wrong type"""
        user_id = "test_user_123"
        email = "test@example.com"

        access_token = auth_service.create_access_token(user_id, email)

        with pytest.raises(jwt.InvalidTokenError, match="Invalid token type"):
            auth_service.verify_token(access_token, "refresh")

    def test_verify_expired_token(self, auth_service):
        """Test expired token verification"""
        user_id = "test_user_123"
        email = "test@example.com"

        # Create token that expires immediately
        past_time = datetime.utcnow() - timedelta(hours=1)
        to_encode = {"sub": user_id, "email": email, "exp": past_time, "type": "access"}
        expired_token = jwt.encode(
            to_encode, auth_service.jwt_secret, algorithm=auth_service.algorithm
        )

        with pytest.raises(jwt.InvalidTokenError, match="Token has expired"):
            auth_service.verify_token(expired_token)

    @patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_verify_google_token_mock_development(self, auth_service):
        """Test Google token verification with mock token in development"""
        mock_token = "mock_google_token_123"

        # Mock the google_client_id for this test
        with patch.object(auth_service, "google_client_id", "mock_client_id"):
            google_data = auth_service.verify_google_token(mock_token)

            assert isinstance(google_data, GoogleOAuthData)
            assert google_data.google_id == "mock_google_123"
            assert google_data.email == "test@example.com"
            assert google_data.email_verified is True

    def test_verify_google_token_no_client_id(self, auth_service):
        """Test Google token verification without client ID configured"""
        with patch.object(auth_service, "google_client_id", None):
            with pytest.raises(ValueError, match="Google Client ID not configured"):
                auth_service.verify_google_token("real_google_token")

    @patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_verify_google_token_production_no_config(self, auth_service):
        """Test Google token verification in production without proper config"""
        with patch.object(auth_service, "google_client_id", None):
            with patch.object(auth_service, "environment", "production"):
                with pytest.raises(
                    ValueError,
                    match="Google OAuth is not properly configured for production",
                ):
                    auth_service.verify_google_token("real_google_token")

    def test_verify_google_token_empty_token(self, auth_service):
        """Test Google token verification with empty token"""
        with pytest.raises(ValueError, match="Google token cannot be empty"):
            auth_service.verify_google_token("")

        with pytest.raises(ValueError, match="Google token cannot be empty"):
            auth_service.verify_google_token("   ")

    @patch.dict(os.environ, {"ENVIRONMENT": "development", "ENABLE_MOCK_AUTH": "false"})
    def test_verify_google_token_mock_disabled(self, auth_service):
        """Test mock token when mock auth is disabled"""
        with patch.object(auth_service, "enable_mock_auth", False):
            with patch.object(auth_service, "google_client_id", "mock_client_id"):
                # Should not use mock token when disabled
                with pytest.raises(ValueError):
                    auth_service.verify_google_token("mock_google_token_123")

    @patch('services.auth_service.id_token')
    def test_verify_production_google_token_success(self, mock_id_token, auth_service):
        """Test successful verification of a production Google token"""
        mock_id_token.verify_oauth2_token.return_value = {
            "sub": "google123",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/avatar.jpg",
            "email_verified": True
        }
        
        with patch.object(auth_service, 'google_client_id', 'test_client_id'):
            google_data = auth_service.verify_google_token("valid_token")
            
            assert google_data.google_id == "google123"
            assert google_data.email == "test@example.com"


    @patch('services.auth_service.id_token')
    def test_verify_production_google_token_unverified_email(self, mock_id_token, auth_service):
        """Test that an unverified email from Google raises a ValueError"""
        mock_id_token.verify_oauth2_token.return_value = {
            "sub": "google123",
            "email": "test@example.com",
            "name": "Test User",
            "email_verified": False  # Email is not verified
        }
        
        with patch.object(auth_service, 'google_client_id', 'test_client_id'):
            with pytest.raises(ValueError, match="Email not verified by Google"):
                auth_service.verify_google_token("unverified_email_token")

    def test_validate_google_client_configuration_development(self, auth_service):
        """Test Google client configuration validation in development"""
        with patch.object(auth_service, "environment", "development"):
            with patch.object(auth_service, "google_client_id", "test_id"):
                with patch.object(auth_service, "google_client_secret", "test_secret"):
                    config = auth_service.validate_google_client_configuration()

                    assert config["google_client_id_configured"] is True
                    assert config["google_client_secret_configured"] is True
                    assert config["environment"] == "development"
                    assert config["production_ready"] is True

    def test_validate_google_client_configuration_production_ready(self, auth_service):
        """Test Google client configuration validation for production-ready setup"""
        with patch.object(auth_service, "environment", "production"):
            with patch.object(auth_service, "google_client_id", "prod_client_id"):
                with patch.object(
                    auth_service, "google_client_secret", "prod_client_secret"
                ):
                    config = auth_service.validate_google_client_configuration()

                    assert config["production_ready"] is True
                    assert config["environment"] == "production"

    def test_validate_google_client_configuration_production_not_ready(
        self, auth_service
    ):
        """Test Google client configuration validation for incomplete production setup"""
        with patch.object(auth_service, "environment", "production"):
            with patch.object(auth_service, "google_client_id", None):
                with patch.object(auth_service, "google_client_secret", None):
                    config = auth_service.validate_google_client_configuration()

                    assert config["production_ready"] is False
                    assert "issues" in config
                    assert (
                        "Google OAuth credentials not configured for production"
                        in config["issues"]
                    )

    def test_enhanced_health_check_healthy(self, auth_service, sample_user):
        """Test enhanced health check when everything is healthy"""
        mock_user_health = {"status": "healthy", "message": "User service operational"}

        with patch.object(
            auth_service.user_service, "health_check", return_value=mock_user_health
        ):
            with patch.object(auth_service, "google_client_id", "test_client_id"):
                health = auth_service.health_check()

                assert health["status"] == "healthy"
                assert health["jwt_working"] is True
                assert health["user_service"]["status"] == "healthy"
                assert health["google_oauth"]["google_client_id_configured"] is True
                assert health["environment"] == auth_service.environment

    def test_enhanced_health_check_unhealthy_user_service(self, auth_service):
        """Test enhanced health check when user service is unhealthy"""
        with patch.object(
            auth_service.user_service,
            "health_check",
            side_effect=Exception("DB connection failed"),
        ):
            health = auth_service.health_check()

            assert health["status"] == "unhealthy"
            assert health["jwt_working"] is True  # JWT should still work
            assert health["user_service"]["status"] == "unhealthy"

    def test_mock_token_user_id_extraction(self, auth_service):
        """Test that mock tokens can extract different user IDs"""
        with patch.dict(
            os.environ, {"ENVIRONMENT": "development", "ENABLE_MOCK_AUTH": "true"}
        ):
            with patch.object(auth_service, "google_client_id", "mock_client_id"):
                # Test different mock token formats
                google_data1 = auth_service.verify_google_token("mock_google_token_456")
                assert google_data1.google_id == "mock_google_456"

                google_data2 = auth_service.verify_google_token("mock_google_token")
                assert google_data2.google_id == "mock_google_123"  # default

    def test_login_with_google_success(
        self, auth_service, google_oauth_data, sample_user
    ):
        """Test successful Google login"""
        with patch.object(
            auth_service, "verify_google_token", return_value=google_oauth_data
        ):
            with patch.object(
                auth_service.user_service,
                "create_or_update_from_google_oauth",
                return_value=(sample_user, True),
            ):
                with patch.object(
                    auth_service.user_service,
                    "update_last_sign_in",
                    return_value=sample_user,
                ):

                    user, access_token, refresh_token, is_new = (
                        auth_service.login_with_google("mock_token")
                    )

                    assert user == sample_user
                    assert isinstance(access_token, str)
                    assert isinstance(refresh_token, str)
                    assert is_new is True

    def test_refresh_access_token_success(self, auth_service, sample_user):
        """Test successful access token refresh"""
        # Create refresh token
        refresh_token = auth_service.create_refresh_token(
            str(sample_user.id), sample_user.email
        )

        with patch.object(
            auth_service.user_service, "get_user_by_email", return_value=sample_user
        ):
            new_access_token, user = auth_service.refresh_access_token(refresh_token)

            assert isinstance(new_access_token, str)
            assert user == sample_user

    def test_refresh_access_token_user_not_found(self, auth_service):
        """Test refresh token with non-existent user"""
        refresh_token = auth_service.create_refresh_token(
            "nonexistent_user", "nonexistent@example.com"
        )

        with patch.object(
            auth_service.user_service, "get_user_by_email", return_value=None
        ):
            with pytest.raises(jwt.InvalidTokenError, match="User not found"):
                auth_service.refresh_access_token(refresh_token)

    def test_refresh_access_token_inactive_user(self, auth_service, sample_user):
        """Test refresh token with inactive user"""
        sample_user.is_active = False
        refresh_token = auth_service.create_refresh_token(
            str(sample_user.id), sample_user.email
        )

        with patch.object(
            auth_service.user_service, "get_user_by_email", return_value=sample_user
        ):
            with pytest.raises(
                jwt.InvalidTokenError, match="User account is deactivated"
            ):
                auth_service.refresh_access_token(refresh_token)

    def test_get_current_user_success(self, auth_service, sample_user):
        """Test successful current user retrieval"""
        access_token = auth_service.create_access_token(
            str(sample_user.id), sample_user.email
        )

        with patch.object(
            auth_service.user_service, "get_user_by_email", return_value=sample_user
        ):
            user = auth_service.get_current_user(access_token)

            assert user == sample_user

    def test_get_current_user_not_found(self, auth_service, sample_user):
        """Test current user retrieval with non-existent user"""
        access_token = auth_service.create_access_token(
            str(sample_user.id), sample_user.email
        )

        with patch.object(
            auth_service.user_service, "get_user_by_email", return_value=None
        ):
            with pytest.raises(jwt.InvalidTokenError, match="User not found"):
                auth_service.get_current_user(access_token)

    def test_get_current_user_inactive(self, auth_service, sample_user):
        """Test current user retrieval with inactive user"""
        sample_user.is_active = False
        access_token = auth_service.create_access_token(
            str(sample_user.id), sample_user.email
        )

        with patch.object(
            auth_service.user_service, "get_user_by_email", return_value=sample_user
        ):
            with pytest.raises(
                jwt.InvalidTokenError, match="User account is deactivated"
            ):
                auth_service.get_current_user(access_token)

    def test_revoke_user_tokens(self, auth_service):
        """Test token revocation (placeholder implementation)"""
        result = auth_service.revoke_user_tokens("test_user_123")
        assert result is True
