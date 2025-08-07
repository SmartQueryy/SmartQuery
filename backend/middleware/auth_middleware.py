"""
Authentication middleware for SmartQuery API
Provides JWT token validation and user context injection
"""

import logging
import os
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from models.user import UserInDB
from services.auth_service import AuthService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize auth service and security
auth_service = AuthService()
security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Authentication middleware for request processing"""

    def __init__(self):
        self.auth_service = AuthService()
        logger.info("AuthMiddleware initialized")

    async def get_current_user_optional(
        self, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[UserInDB]:
        """Get current user from token, return None if not authenticated"""
        if not credentials:
            return None

        try:
            user = self.auth_service.get_current_user(credentials.credentials)
            return user
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            return None

    async def get_current_user_required(
        self, credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> UserInDB:
        """Get current user from token, raise 401 if not authenticated"""
        if not credentials:
            logger.warning("Authentication required but no credentials provided")
            raise HTTPException(
                status_code=401,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            user = self.auth_service.get_current_user(credentials.credentials)
            logger.debug(f"Authenticated user: {user.email}")
            return user
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token provided: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail=f"Invalid or expired token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(status_code=500, detail="Authentication service error")

    async def verify_token_only(
        self, credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> str:
        """Verify token and return user ID without database lookup"""
        if not credentials:
            raise HTTPException(
                status_code=401,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            token_data = self.auth_service.verify_token(credentials.credentials)
            return token_data.user_id
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token in verification: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail=f"Invalid or expired token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )


# Global middleware instance
auth_middleware = AuthMiddleware()


# Dependency functions for use in FastAPI routes
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[UserInDB]:
    """Dependency for optional authentication"""
    return await auth_middleware.get_current_user_optional(credentials)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserInDB:
    """Dependency for required authentication"""
    return await auth_middleware.get_current_user_required(credentials)


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Dependency for token verification only (returns user_id)"""
    return await auth_middleware.verify_token_only(credentials)


def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication for a function"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Check if user is provided in kwargs
        if "current_user" not in kwargs:
            raise HTTPException(status_code=401, detail="Authentication required")
        return await func(*args, **kwargs)

    return wrapper


def require_active_user(func: Callable) -> Callable:
    """Decorator to require an active user account"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        if not current_user.is_active:
            logger.warning(f"Inactive user attempted access: {current_user.email}")
            raise HTTPException(status_code=403, detail="Account is deactivated")

        return await func(*args, **kwargs)

    return wrapper


def require_verified_user(func: Callable) -> Callable:
    """Decorator to require a verified user account"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        if not current_user.is_verified:
            logger.warning(f"Unverified user attempted access: {current_user.email}")
            raise HTTPException(status_code=403, detail="Email verification required")

        return await func(*args, **kwargs)

    return wrapper


async def extract_user_context(request: Request) -> dict:
    """Extract user context from request for logging and monitoring"""
    context = {
        "user_id": None,
        "email": None,
        "is_authenticated": False,
        "request_path": request.url.path,
        "request_method": request.method,
    }

    # Try to extract user from Authorization header
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            token_data = auth_service.verify_token(token)
            context.update(
                {
                    "user_id": token_data.user_id,
                    "email": token_data.email,
                    "is_authenticated": True,
                }
            )
        except jwt.InvalidTokenError:
            pass  # Keep default values
        except Exception as e:
            logger.error(f"Error extracting user context: {str(e)}")

    return context


class RateLimitMiddleware:
    """Enhanced rate limiting middleware with Redis-like functionality"""

    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.user_requests = {}  # In production, use Redis
        self.blocked_users = set()  # Temporarily blocked users
        self.rate_limit_enabled = (
            os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        )

        # Different limits for different operations
        self.endpoint_limits = {
            "auth": 20,  # Auth operations
            "projects": 50,  # Project operations
            "chat": 30,  # Chat operations
            "default": requests_per_minute,
        }

        logger.info(
            f"RateLimitMiddleware initialized with {requests_per_minute} requests/minute"
        )

    def _get_endpoint_category(self, path: str) -> str:
        """Categorize endpoint for rate limiting"""
        if "/auth/" in path:
            return "auth"
        elif "/projects" in path:
            return "projects"
        elif "/chat/" in path:
            return "chat"
        else:
            return "default"

    async def check_rate_limit(
        self, user_id: str, endpoint_path: str = ""
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if user has exceeded rate limit"""
        if not self.rate_limit_enabled:
            return True, {}

        # Check if user is temporarily blocked
        if user_id in self.blocked_users:
            return False, {
                "reason": "Temporarily blocked due to excessive requests",
                "retry_after": 300,  # 5 minutes
            }

        # Get appropriate limit for endpoint
        category = self._get_endpoint_category(endpoint_path)
        limit = self.endpoint_limits.get(category, self.endpoint_limits["default"])

        # Get current time window
        import time

        current_time = time.time()
        window_start = int(current_time // 60) * 60  # Start of current minute

        # Initialize user request tracking
        if user_id not in self.user_requests:
            self.user_requests[user_id] = {}

        # Clean old windows (keep last 2 minutes for analysis)
        user_windows = self.user_requests[user_id]
        old_windows = [w for w in user_windows.keys() if w < window_start - 120]
        for old_window in old_windows:
            del user_windows[old_window]

        # Count requests in current window
        current_requests = user_windows.get(window_start, 0)

        if current_requests >= limit:
            # Check if user should be temporarily blocked
            recent_requests = sum(user_windows.values())
            if recent_requests >= limit * 3:  # 3x the limit across windows
                self.blocked_users.add(user_id)
                logger.warning(
                    f"User {user_id} temporarily blocked for excessive requests"
                )
                return False, {
                    "reason": "Temporarily blocked due to excessive requests",
                    "retry_after": 300,
                }

            return False, {
                "reason": "Rate limit exceeded",
                "limit": limit,
                "current": current_requests,
                "retry_after": 60,
            }

        # Record this request
        user_windows[window_start] = current_requests + 1

        return True, {
            "limit": limit,
            "current": current_requests + 1,
            "remaining": limit - current_requests - 1,
        }

    async def apply_rate_limit(
        self,
        current_user: Optional[UserInDB] = Depends(get_current_user_optional),
        request: Request = None,
    ) -> bool:
        """Apply rate limiting based on user"""
        if not current_user:
            # Apply stricter limits for anonymous users based on IP
            # This is a simplified implementation
            return True

        endpoint_path = str(request.url.path) if request else ""
        allowed, info = await self.check_rate_limit(str(current_user.id), endpoint_path)

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=info.get("reason", "Rate limit exceeded"),
                headers={"Retry-After": str(info.get("retry_after", 60))},
            )

        return True


# Global rate limiter instance
rate_limiter = RateLimitMiddleware()


def with_rate_limit(func: Callable) -> Callable:
    """Decorator to apply rate limiting to endpoints"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")

        # Check rate limit
        if current_user:
            rate_check = await rate_limiter.check_rate_limit(str(current_user.id))
            if not rate_check:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later.",
                )

        return await func(*args, **kwargs)

    return wrapper


async def log_request_context(request: Request):
    """Middleware to log request context for monitoring"""
    context = await extract_user_context(request)
    logger.info(
        f"Request: {context['request_method']} {context['request_path']} "
        f"- User: {context.get('email', 'anonymous')} "
        f"- Authenticated: {context['is_authenticated']}"
    )
    return context
