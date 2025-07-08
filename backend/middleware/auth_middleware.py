"""
Authentication middleware for SmartQuery API
Provides JWT token validation and user context injection
"""

import logging
from typing import Optional, Callable, Any
from functools import wraps

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from services.auth_service import AuthService
from models.user import UserInDB

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
        self, 
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
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
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
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
            raise HTTPException(
                status_code=500,
                detail="Authentication service error"
            )
    
    async def verify_token_only(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
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
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserInDB]:
    """Dependency for optional authentication"""
    return await auth_middleware.get_current_user_optional(credentials)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInDB:
    """Dependency for required authentication"""
    return await auth_middleware.get_current_user_required(credentials)


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Dependency for token verification only (returns user_id)"""
    return await auth_middleware.verify_token_only(credentials)


def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication for a function"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Check if user is provided in kwargs
        if 'current_user' not in kwargs:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )
        return await func(*args, **kwargs)
    return wrapper


def require_active_user(func: Callable) -> Callable:
    """Decorator to require an active user account"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )
        
        if not current_user.is_active:
            logger.warning(f"Inactive user attempted access: {current_user.email}")
            raise HTTPException(
                status_code=403,
                detail="Account is deactivated"
            )
        
        return await func(*args, **kwargs)
    return wrapper


def require_verified_user(func: Callable) -> Callable:
    """Decorator to require a verified user account"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )
        
        if not current_user.is_verified:
            logger.warning(f"Unverified user attempted access: {current_user.email}")
            raise HTTPException(
                status_code=403,
                detail="Email verification required"
            )
        
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
            context.update({
                "user_id": token_data.user_id,
                "email": token_data.email,
                "is_authenticated": True,
            })
        except jwt.InvalidTokenError:
            pass  # Keep default values
        except Exception as e:
            logger.error(f"Error extracting user context: {str(e)}")
    
    return context


class RateLimitMiddleware:
    """Simple rate limiting middleware (placeholder for future implementation)"""
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.user_requests = {}  # In production, use Redis
        logger.info(f"RateLimitMiddleware initialized with {requests_per_minute} requests/minute")
    
    async def check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limit"""
        # Placeholder implementation
        # In production, implement proper rate limiting with Redis
        return True
    
    async def apply_rate_limit(
        self,
        current_user: Optional[UserInDB] = Depends(get_current_user_optional)
    ) -> bool:
        """Apply rate limiting based on user"""
        if not current_user:
            # Apply stricter limits for anonymous users
            return True
        
        return await self.check_rate_limit(str(current_user.id))


# Global rate limiter instance
rate_limiter = RateLimitMiddleware()


def with_rate_limit(func: Callable) -> Callable:
    """Decorator to apply rate limiting to endpoints"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        
        # Check rate limit
        if current_user:
            rate_check = await rate_limiter.check_rate_limit(str(current_user.id))
            if not rate_check:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
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