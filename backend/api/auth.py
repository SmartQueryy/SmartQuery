import uuid
from typing import Optional
import logging

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt

from models.response_schemas import ApiResponse, AuthResponse, LoginRequest, User
from models.user import UserPublic
from services.auth_service import AuthService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()
security = HTTPBearer()


def get_current_user_token(token: str = Depends(security)) -> str:
    """Extract token from Authorization header"""
    return token.credentials


@router.post("/google")
async def login_with_google(request: LoginRequest) -> ApiResponse[AuthResponse]:
    """Google OAuth login with enhanced error handling"""
    try:
        logger.info("Received Google OAuth login request")
        
        # Validate request
        if not request.google_token or not request.google_token.strip():
            logger.warning("Empty Google token received")
            raise HTTPException(status_code=400, detail="Google token is required")
        
        user, access_token, refresh_token, is_new_user = auth_service.login_with_google(
            request.google_token.strip()
        )

        # Convert UserInDB to UserPublic for API response
        public_user = UserPublic.from_db_user(user)
        
        # Convert to response format expected by frontend
        user_response = User(
            id=public_user.id,
            email=public_user.email,
            name=public_user.name,
            avatar_url=public_user.avatar_url,
            created_at=public_user.created_at,
            last_sign_in_at=public_user.last_sign_in_at,
        )

        auth_response = AuthResponse(
            user=user_response,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_service.access_token_expire_minutes * 60,
        )

        logger.info(f"Google OAuth login successful for user: {user.email}, is_new_user: {is_new_user}")
        return ApiResponse(
            success=True, 
            data=auth_response,
            message="Login successful" if not is_new_user else "Account created and login successful"
        )

    except ValueError as e:
        logger.error(f"Google OAuth validation error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")
    except Exception as e:
        logger.error(f"Google OAuth login failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.get("/me")
async def get_current_user(token: str = Depends(get_current_user_token)) -> ApiResponse[User]:
    """Get current user information with enhanced error handling"""
    try:
        logger.info("Received current user request")
        
        user = auth_service.get_current_user(token)
        public_user = UserPublic.from_db_user(user)
        
        user_response = User(
            id=public_user.id,
            email=public_user.email,
            name=public_user.name,
            avatar_url=public_user.avatar_url,
            created_at=public_user.created_at,
            last_sign_in_at=public_user.last_sign_in_at,
        )

        logger.info(f"Current user request successful for: {user.email}")
        return ApiResponse(success=True, data=user_response)

    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token in current user request: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")
    except Exception as e:
        logger.error(f"Current user request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user information: {str(e)}")


@router.post("/logout")
async def logout(token: str = Depends(get_current_user_token)) -> ApiResponse[dict]:
    """Logout current user with enhanced logging"""
    try:
        logger.info("Received logout request")
        
        # Verify token and get user for logging
        user = auth_service.get_current_user(token)
        
        # Revoke tokens (placeholder implementation)
        success = auth_service.revoke_user_tokens(str(user.id))
        
        if success:
            logger.info(f"Logout successful for user: {user.email}")
            return ApiResponse(
                success=True, 
                data={"message": "Logged out successfully"},
                message="You have been logged out"
            )
        else:
            logger.error(f"Token revocation failed for user: {user.email}")
            raise HTTPException(status_code=500, detail="Logout failed")

    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token in logout request: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")


@router.post("/refresh")
async def refresh_token(request: dict) -> ApiResponse[AuthResponse]:
    """Refresh access token with enhanced validation"""
    try:
        logger.info("Received token refresh request")
        
        # Validate request
        refresh_token = request.get("refresh_token")
        if not refresh_token or not refresh_token.strip():
            logger.warning("Empty refresh token received")
            raise HTTPException(status_code=400, detail="Refresh token is required")
        
        new_access_token, user = auth_service.refresh_access_token(refresh_token.strip())
        
        # Convert to response format
        public_user = UserPublic.from_db_user(user)
        user_response = User(
            id=public_user.id,
            email=public_user.email,
            name=public_user.name,
            avatar_url=public_user.avatar_url,
            created_at=public_user.created_at,
            last_sign_in_at=public_user.last_sign_in_at,
        )

        auth_response = AuthResponse(
            user=user_response,
            access_token=new_access_token,
            refresh_token=refresh_token,  # Keep the same refresh token
            expires_in=auth_service.access_token_expire_minutes * 60,
        )

        logger.info(f"Token refresh successful for user: {user.email}")
        return ApiResponse(
            success=True, 
            data=auth_response,
            message="Token refreshed successfully"
        )

    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid refresh token: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid or expired refresh token: {str(e)}")
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")


@router.get("/health")
async def auth_health_check() -> ApiResponse[dict]:
    """Enhanced authentication service health check"""
    try:
        logger.info("Received auth health check request")
        
        health_data = auth_service.health_check()
        
        # Determine HTTP status based on health
        if health_data.get("status") == "healthy":
            logger.info("Auth health check passed")
            return ApiResponse(
                success=True,
                data=health_data,
                message="Authentication service is healthy"
            )
        else:
            logger.warning(f"Auth health check failed: {health_data}")
            raise HTTPException(
                status_code=503, 
                detail=f"Authentication service is unhealthy: {health_data.get('error', 'Unknown error')}"
            )

    except Exception as e:
        logger.error(f"Auth health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
