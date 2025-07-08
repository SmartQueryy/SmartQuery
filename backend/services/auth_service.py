import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import jwt
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests
from google.oauth2 import id_token
from pydantic import BaseModel

from models.user import GoogleOAuthData, UserInDB
from services.user_service import get_user_service

# Initialize user service
user_service = get_user_service()
logger = logging.getLogger(__name__)


class TokenData(BaseModel):
    """Token data model"""

    user_id: str
    email: str
    exp: datetime


class AuthService:
    """Authentication service for JWT and Google OAuth"""

    def __init__(self):
        self.user_service = user_service
        self.jwt_secret = os.getenv(
            "JWT_SECRET", "development_secret_key_change_in_production"
        )
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        )
        self.refresh_token_expire_days = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30")
        )
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.enable_mock_auth = os.getenv("ENABLE_MOCK_AUTH", "true").lower() == "true"

        # Log configuration status
        logger.info(f"AuthService initialized - Environment: {self.environment}")
        logger.info(f"Google OAuth configured: {bool(self.google_client_id)}")
        logger.info(f"Mock auth enabled: {self.enable_mock_auth}")

    def create_access_token(self, user_id: str, email: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        }
        return jwt.encode(to_encode, self.jwt_secret, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str, email: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }
        return jwt.encode(to_encode, self.jwt_secret, algorithm=self.algorithm)

    def verify_token(self, token: str, token_type: str = "access") -> TokenData:
        """Verify JWT token and return token data"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") != token_type:
                raise jwt.InvalidTokenError("Invalid token type")

            # Check expiration
            exp_timestamp = payload.get("exp")
            if (
                exp_timestamp
                and datetime.utcfromtimestamp(exp_timestamp) < datetime.utcnow()
            ):
                raise jwt.InvalidTokenError("Token has expired")

            return TokenData(
                user_id=payload.get("sub"),
                email=payload.get("email"),
                exp=(
                    datetime.utcfromtimestamp(exp_timestamp)
                    if exp_timestamp
                    else datetime.utcnow()
                ),
            )
        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")

    def verify_google_token(self, google_token: str) -> GoogleOAuthData:
        """
        Verify Google OAuth token and extract user data
        Enhanced with better error handling and validation
        """
        try:
            # Validate inputs
            if not google_token or not google_token.strip():
                raise ValueError("Google token cannot be empty")

            google_token = google_token.strip()

            # Check if Google Client ID is configured
            if not self.google_client_id:
                if self.environment == "production":
                    raise ValueError(
                        "Google OAuth is not properly configured for production"
                    )
                logger.warning(
                    "Google Client ID not configured - using development mode"
                )

            # Handle development/testing mode with mock tokens
            if self._is_mock_token(google_token):
                return self._handle_mock_token(google_token)

            # Production Google OAuth verification
            return self._verify_production_google_token(google_token)

        except GoogleAuthError as e:
            logger.error(f"Google Auth error: {str(e)}")
            raise ValueError(f"Google authentication failed: {str(e)}")
        except ValueError as e:
            logger.error(f"Google token validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Google token verification: {str(e)}")
            raise ValueError(f"Authentication failed: {str(e)}")

    def _is_mock_token(self, token: str) -> bool:
        """Check if token is a mock token for development"""
        return (
            self.enable_mock_auth
            and self.environment == "development"
            and token.startswith("mock_google_token")
        )

    def _handle_mock_token(self, token: str) -> GoogleOAuthData:
        """Handle mock tokens for development"""
        if not self.enable_mock_auth:
            raise ValueError("Mock authentication is disabled")

        logger.info("Using mock Google token for development")

        # Extract user info from mock token if available
        mock_user_id = token.replace("mock_google_token_", "").replace(
            "mock_google_token", "123"
        )

        return GoogleOAuthData(
            google_id=f"mock_google_{mock_user_id}",
            email="test@example.com",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg",
            email_verified=True,
        )

    def _verify_production_google_token(self, token: str) -> GoogleOAuthData:
        """Verify real Google OAuth token in production"""
        if not self.google_client_id:
            raise ValueError("Google Client ID not configured")

        try:
            # Verify token with Google
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), self.google_client_id
            )

            # Validate required fields
            required_fields = ["sub", "email", "name"]
            missing_fields = [
                field for field in required_fields if not idinfo.get(field)
            ]
            if missing_fields:
                raise ValueError(
                    f"Missing required Google OAuth fields: {missing_fields}"
                )

            # Additional security checks
            if not idinfo.get("email_verified", False):
                logger.warning(
                    f"Unverified email from Google OAuth: {idinfo.get('email')}"
                )
                raise ValueError("Email not verified by Google")

            # Extract and validate user information
            google_data = GoogleOAuthData(
                google_id=idinfo["sub"],
                email=idinfo["email"],
                name=idinfo["name"],
                avatar_url=idinfo.get("picture"),
                email_verified=idinfo.get("email_verified", False),
            )

            logger.info(
                f"Successfully verified Google token for user: {google_data.email}"
            )
            return google_data

        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Google token verification failed: {str(e)}")
            raise ValueError(f"Invalid Google token: {str(e)}")

    def login_with_google(self, google_token: str) -> Tuple[UserInDB, str, str, bool]:
        """
        Login with Google OAuth token
        Enhanced with better logging and error handling
        Returns: (user, access_token, refresh_token, is_new_user)
        """
        try:
            logger.info("Starting Google OAuth login process")

            # Verify Google token
            google_data = self.verify_google_token(google_token)
            logger.info(f"Google token verified for user: {google_data.email}")

            # Create or update user
            user, is_new = self.user_service.create_or_update_from_google_oauth(
                google_data
            )
            logger.info(f"User {'created' if is_new else 'updated'}: {user.email}")

            # Update last sign-in
            user = self.user_service.update_last_sign_in(user.id)

            # Create tokens
            access_token = self.create_access_token(str(user.id), user.email)
            refresh_token = self.create_refresh_token(str(user.id), user.email)

            logger.info(f"Login successful for user: {user.email}")
            return user, access_token, refresh_token, is_new

        except Exception as e:
            logger.error(f"Google login failed: {str(e)}")
            raise

    def refresh_access_token(self, refresh_token: str) -> Tuple[str, UserInDB]:
        """
        Refresh access token using refresh token
        Returns: (new_access_token, user)
        """
        try:
            logger.info("Processing token refresh request")

            # Verify refresh token
            token_data = self.verify_token(refresh_token, token_type="refresh")

            # Get user from database
            user = self.user_service.get_user_by_email(token_data.email)
            if not user:
                logger.warning(
                    f"Token refresh failed: User not found for email {token_data.email}"
                )
                raise jwt.InvalidTokenError("User not found")

            if not user.is_active:
                logger.warning(
                    f"Token refresh failed: User account inactive {user.email}"
                )
                raise jwt.InvalidTokenError("User account is deactivated")

            # Create new access token
            new_access_token = self.create_access_token(str(user.id), user.email)

            logger.info(f"Token refreshed successfully for user: {user.email}")
            return new_access_token, user

        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise

    def get_current_user(self, access_token: str) -> UserInDB:
        """Get current user from access token"""
        try:
            # Verify access token
            token_data = self.verify_token(access_token, token_type="access")

            # Get user from database
            user = self.user_service.get_user_by_email(token_data.email)
            if not user:
                logger.warning(
                    f"Current user request failed: User not found for email {token_data.email}"
                )
                raise jwt.InvalidTokenError("User not found")

            if not user.is_active:
                logger.warning(
                    f"Current user request failed: User account inactive {user.email}"
                )
                raise jwt.InvalidTokenError("User account is deactivated")

            return user

        except Exception as e:
            logger.error(f"Get current user failed: {str(e)}")
            raise

    def revoke_user_tokens(self, user_id: str) -> bool:
        """
        Revoke all tokens for a user (logout)
        Note: With JWT, we can't actually revoke tokens server-side without a blacklist.
        This is a placeholder for future token blacklist implementation.
        """
        logger.info(f"Token revocation requested for user: {user_id}")
        # In a production system, you would add the user's tokens to a blacklist
        # For now, we just return True as logout is handled client-side
        return True

    def validate_google_client_configuration(self) -> Dict[str, any]:
        """Validate Google OAuth client configuration"""
        config_status = {
            "google_client_id_configured": bool(self.google_client_id),
            "google_client_secret_configured": bool(self.google_client_secret),
            "environment": self.environment,
            "mock_auth_enabled": self.enable_mock_auth,
        }

        if self.environment == "production":
            if not self.google_client_id or not self.google_client_secret:
                config_status["production_ready"] = False
                config_status["issues"] = [
                    "Google OAuth credentials not configured for production"
                ]
            else:
                config_status["production_ready"] = True
        else:
            config_status["production_ready"] = True

        return config_status

    def health_check(self) -> Dict[str, any]:
        """Enhanced health check for auth service"""
        try:
            # Test JWT encoding/decoding
            test_token = self.create_access_token("test_user", "test@example.com")
            self.verify_token(test_token)
            jwt_working = True

        except Exception as e:
            logger.error(f"JWT health check failed: {str(e)}")
            jwt_working = False

        try:
            # Test user service connection
            user_health = self.user_service.health_check()
            user_service_healthy = user_health.get("status") == "healthy"

        except Exception as e:
            logger.error(f"User service health check failed: {str(e)}")
            user_service_healthy = False
            user_health = {"status": "unhealthy", "error": str(e)}

        # Validate Google OAuth configuration
        google_config = self.validate_google_client_configuration()

        overall_status = (
            "healthy" if (jwt_working and user_service_healthy) else "unhealthy"
        )

        return {
            "status": overall_status,
            "jwt_working": jwt_working,
            "user_service": user_health,
            "google_oauth": google_config,
            "environment": self.environment,
            "access_token_expire_minutes": self.access_token_expire_minutes,
            "refresh_token_expire_days": self.refresh_token_expire_days,
        }
