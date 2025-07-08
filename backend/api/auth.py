from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import uuid
import jwt
import os

from models.response_schemas import (
    ApiResponse, User, LoginRequest, AuthResponse, 
    RefreshTokenRequest
)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Mock user database
MOCK_USERS = {
    "google_user_123": {
        "id": "user_001",
        "email": "john.doe@example.com",
        "name": "John Doe",
        "avatar_url": "https://lh3.googleusercontent.com/a/default-user",
        "created_at": "2025-01-01T00:00:00Z",
        "last_sign_in_at": "2025-01-01T12:00:00Z"
    }
}

# Mock JWT settings
JWT_SECRET = os.getenv("JWT_SECRET", "mock_secret_key_for_development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: Dict[str, Any]) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/google")
async def login_with_google(request: LoginRequest) -> ApiResponse[AuthResponse]:
    """Mock Google OAuth login"""
    # Mock Google token validation
    if not request.google_token.startswith("mock_google_token"):
        raise HTTPException(status_code=401, detail="Invalid Google token")
    
    # Mock user from Google token
    user_data = MOCK_USERS["google_user_123"]
    user = User(**user_data)
    
    # Create JWT tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = str(uuid.uuid4())
    
    auth_response = AuthResponse(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return ApiResponse(success=True, data=auth_response)

@router.get("/me")
async def get_current_user(user_id: str = Depends(verify_token)) -> ApiResponse[User]:
    """Get current user information"""
    # Mock user lookup
    for mock_user in MOCK_USERS.values():
        if mock_user["id"] == user_id:
            user = User(**mock_user)
            return ApiResponse(success=True, data=user)
    
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/logout")
async def logout(user_id: str = Depends(verify_token)) -> ApiResponse[Dict[str, str]]:
    """Logout current user"""
    return ApiResponse(
        success=True, 
        data={"message": "Logged out successfully"}
    )

@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest) -> ApiResponse[Dict[str, Any]]:
    """Refresh access token"""
    # Mock refresh token validation
    if not request.refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Create new access token
    new_access_token = create_access_token(data={"sub": "user_001"})
    
    return ApiResponse(
        success=True,
        data={
            "access_token": new_access_token,
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    ) 