import uuid
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import jwt

from middleware.auth_middleware import (
    AuthMiddleware,
    get_current_user,
    get_current_user_optional,
    verify_token,
    require_auth,
    require_active_user,
    require_verified_user,
    extract_user_context,
    RateLimitMiddleware,
)
from models.user import UserInDB
from services.auth_service import AuthService


class TestAuthMiddleware:
    """Test suite for AuthMiddleware"""

    @pytest.fixture
    def auth_middleware(self):
        """AuthMiddleware instance for testing"""
        return AuthMiddleware()

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
    def inactive_user(self):
        """Inactive user for testing"""
        return UserInDB(
            id=uuid.uuid4(),
            email="inactive@example.com",
            name="Inactive User",
            avatar_url="https://example.com/avatar.jpg",
            google_id="google_456",
            is_active=False,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.fixture
    def unverified_user(self):
        """Unverified user for testing"""
        return UserInDB(
            id=uuid.uuid4(),
            email="unverified@example.com",
            name="Unverified User",
            avatar_url="https://example.com/avatar.jpg",
            google_id="google_789",
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.fixture
    def valid_credentials(self):
        """Valid HTTPAuthorizationCredentials for testing"""
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

    @pytest.fixture
    def invalid_credentials(self):
        """Invalid HTTPAuthorizationCredentials for testing"""
        return HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid_token"
        )

    @pytest.mark.asyncio
    async def test_get_current_user_optional_success(
        self, auth_middleware, sample_user, valid_credentials
    ):
        """Test optional user retrieval with valid token"""
        with patch.object(
            auth_middleware.auth_service, "get_current_user", return_value=sample_user
        ):
            user = await auth_middleware.get_current_user_optional(valid_credentials)
            assert user == sample_user

    @pytest.mark.asyncio
    async def test_get_current_user_optional_no_credentials(self, auth_middleware):
        """Test optional user retrieval with no credentials"""
        user = await auth_middleware.get_current_user_optional(None)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_current_user_optional_invalid_token(
        self, auth_middleware, invalid_credentials
    ):
        """Test optional user retrieval with invalid token"""
        with patch.object(
            auth_middleware.auth_service,
            "get_current_user",
            side_effect=jwt.InvalidTokenError("Invalid token"),
        ):
            user = await auth_middleware.get_current_user_optional(invalid_credentials)
            assert user is None

    @pytest.mark.asyncio
    async def test_get_current_user_required_success(
        self, auth_middleware, sample_user, valid_credentials
    ):
        """Test required user retrieval with valid token"""
        with patch.object(
            auth_middleware.auth_service, "get_current_user", return_value=sample_user
        ):
            user = await auth_middleware.get_current_user_required(valid_credentials)
            assert user == sample_user

    @pytest.mark.asyncio
    async def test_get_current_user_required_no_credentials(self, auth_middleware):
        """Test required user retrieval with no credentials"""
        with pytest.raises(HTTPException) as exc_info:
            await auth_middleware.get_current_user_required(None)
        assert exc_info.value.status_code == 401
        assert "Authentication required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_required_invalid_token(
        self, auth_middleware, invalid_credentials
    ):
        """Test required user retrieval with invalid token"""
        with patch.object(
            auth_middleware.auth_service,
            "get_current_user",
            side_effect=jwt.InvalidTokenError("Invalid token"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await auth_middleware.get_current_user_required(invalid_credentials)
            assert exc_info.value.status_code == 401
            assert "Invalid or expired token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_token_only_success(self, auth_middleware, valid_credentials):
        """Test token verification returning user ID"""
        mock_token_data = Mock()
        mock_token_data.user_id = "test_user_123"

        with patch.object(
            auth_middleware.auth_service, "verify_token", return_value=mock_token_data
        ):
            user_id = await auth_middleware.verify_token_only(valid_credentials)
            assert user_id == "test_user_123"

    @pytest.mark.asyncio
    async def test_verify_token_only_no_credentials(self, auth_middleware):
        """Test token verification with no credentials"""
        with pytest.raises(HTTPException) as exc_info:
            await auth_middleware.verify_token_only(None)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_token_only_invalid_token(
        self, auth_middleware, invalid_credentials
    ):
        """Test token verification with invalid token"""
        with patch.object(
            auth_middleware.auth_service,
            "verify_token",
            side_effect=jwt.InvalidTokenError("Invalid token"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await auth_middleware.verify_token_only(invalid_credentials)
            assert exc_info.value.status_code == 401


class TestAuthDependencies:
    """Test auth dependency functions"""

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

    @pytest.mark.asyncio
    async def test_get_current_user_dependency_success(self, sample_user):
        """Test get_current_user dependency with valid credentials"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )

        with patch("middleware.auth_middleware.auth_middleware") as mock_middleware:
            mock_middleware.get_current_user_required = AsyncMock(
                return_value=sample_user
            )
            user = await get_current_user(credentials)
            assert user == sample_user

    @pytest.mark.asyncio
    async def test_get_current_user_optional_dependency(self, sample_user):
        """Test get_current_user_optional dependency"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )

        with patch("middleware.auth_middleware.auth_middleware") as mock_middleware:
            mock_middleware.get_current_user_optional = AsyncMock(
                return_value=sample_user
            )
            user = await get_current_user_optional(credentials)
            assert user == sample_user

    @pytest.mark.asyncio
    async def test_verify_token_dependency(self):
        """Test verify_token dependency"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )

        with patch("middleware.auth_middleware.auth_middleware") as mock_middleware:
            mock_middleware.verify_token_only = AsyncMock(return_value="user_123")
            user_id = await verify_token(credentials)
            assert user_id == "user_123"


class TestAuthDecorators:
    """Test authentication decorators"""

    @pytest.fixture
    def sample_user(self):
        """Sample active user for testing"""
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
    def inactive_user(self):
        """Inactive user for testing"""
        return UserInDB(
            id=uuid.uuid4(),
            email="inactive@example.com",
            name="Inactive User",
            avatar_url="https://example.com/avatar.jpg",
            google_id="google_456",
            is_active=False,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.fixture
    def unverified_user(self):
        """Unverified user for testing"""
        return UserInDB(
            id=uuid.uuid4(),
            email="unverified@example.com",
            name="Unverified User",
            avatar_url="https://example.com/avatar.jpg",
            google_id="google_789",
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.mark.asyncio
    async def test_require_auth_decorator_success(self, sample_user):
        """Test require_auth decorator with authenticated user"""

        @require_auth
        async def protected_function(current_user=None):
            return {"user": current_user.email}

        result = await protected_function(current_user=sample_user)
        assert result["user"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_require_auth_decorator_no_user(self):
        """Test require_auth decorator without user"""

        @require_auth
        async def protected_function():
            return {"success": True}

        with pytest.raises(HTTPException) as exc_info:
            await protected_function()
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_require_active_user_decorator_success(self, sample_user):
        """Test require_active_user decorator with active user"""

        @require_active_user
        async def protected_function(current_user=None):
            return {"user": current_user.email}

        result = await protected_function(current_user=sample_user)
        assert result["user"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_require_active_user_decorator_inactive(self, inactive_user):
        """Test require_active_user decorator with inactive user"""

        @require_active_user
        async def protected_function(current_user=None):
            return {"user": current_user.email}

        with pytest.raises(HTTPException) as exc_info:
            await protected_function(current_user=inactive_user)
        assert exc_info.value.status_code == 403
        assert "Account is deactivated" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_verified_user_decorator_success(self, sample_user):
        """Test require_verified_user decorator with verified user"""

        @require_verified_user
        async def protected_function(current_user=None):
            return {"user": current_user.email}

        result = await protected_function(current_user=sample_user)
        assert result["user"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_require_verified_user_decorator_unverified(self, unverified_user):
        """Test require_verified_user decorator with unverified user"""

        @require_verified_user
        async def protected_function(current_user=None):
            return {"user": current_user.email}

        with pytest.raises(HTTPException) as exc_info:
            await protected_function(current_user=unverified_user)
        assert exc_info.value.status_code == 403
        assert "Email verification required" in exc_info.value.detail


class TestContextExtraction:
    """Test user context extraction"""

    @pytest.mark.asyncio
    async def test_extract_user_context_authenticated(self):
        """Test extracting user context with valid token"""
        mock_request = Mock()
        mock_request.url.path = "/api/projects"
        mock_request.method = "GET"
        mock_request.headers = {"authorization": "Bearer valid_token"}

        mock_token_data = Mock()
        mock_token_data.user_id = "user_123"
        mock_token_data.email = "test@example.com"

        with patch("middleware.auth_middleware.auth_service") as mock_auth_service:
            mock_auth_service.verify_token.return_value = mock_token_data

            context = await extract_user_context(mock_request)

            assert context["user_id"] == "user_123"
            assert context["email"] == "test@example.com"
            assert context["is_authenticated"] is True
            assert context["request_path"] == "/api/projects"
            assert context["request_method"] == "GET"

    @pytest.mark.asyncio
    async def test_extract_user_context_no_auth(self):
        """Test extracting user context without authentication"""
        mock_request = Mock()
        mock_request.url.path = "/api/public"
        mock_request.method = "GET"
        mock_request.headers = {}

        context = await extract_user_context(mock_request)

        assert context["user_id"] is None
        assert context["email"] is None
        assert context["is_authenticated"] is False
        assert context["request_path"] == "/api/public"
        assert context["request_method"] == "GET"

    @pytest.mark.asyncio
    async def test_extract_user_context_invalid_token(self):
        """Test extracting user context with invalid token"""
        mock_request = Mock()
        mock_request.url.path = "/api/projects"
        mock_request.method = "GET"
        mock_request.headers = {"authorization": "Bearer invalid_token"}

        with patch("middleware.auth_middleware.auth_service") as mock_auth_service:
            mock_auth_service.verify_token.side_effect = jwt.InvalidTokenError(
                "Invalid token"
            )

            context = await extract_user_context(mock_request)

            assert context["user_id"] is None
            assert context["email"] is None
            assert context["is_authenticated"] is False


class TestRateLimitMiddleware:
    """Test rate limiting middleware"""

    @pytest.fixture
    def rate_limiter(self):
        """RateLimitMiddleware instance for testing"""
        return RateLimitMiddleware(requests_per_minute=60)

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

    @pytest.mark.asyncio
    async def test_check_rate_limit_success(self, rate_limiter):
        """Test rate limit check for user"""
        result = await rate_limiter.check_rate_limit("user_123")
        assert result is True  # Placeholder implementation always returns True

    @pytest.mark.asyncio
    async def test_apply_rate_limit_with_user(self, rate_limiter, sample_user):
        """Test applying rate limit with authenticated user"""
        result = await rate_limiter.apply_rate_limit(sample_user)
        assert result is True

    @pytest.mark.asyncio
    async def test_apply_rate_limit_without_user(self, rate_limiter):
        """Test applying rate limit without user (anonymous)"""
        result = await rate_limiter.apply_rate_limit(None)
        assert result is True
