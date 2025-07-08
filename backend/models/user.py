import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class UserTable(Base):
    """SQLAlchemy User table model for PostgreSQL"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    avatar_url = Column(Text, nullable=True)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_sign_in_at = Column(DateTime, nullable=True)

    # Relationships
    # projects = relationship(
    #     "ProjectTable", back_populates="user", cascade="all, delete"
    # )
    # chat_messages = relationship(
    #     "ChatMessageTable", back_populates="user", cascade="all, delete"
    # )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"


class UserCreate(BaseModel):
    """Pydantic model for creating a user"""

    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=255, description="User full name")
    avatar_url: Optional[str] = Field(None, description="User avatar URL")
    google_id: Optional[str] = Field(None, description="Google OAuth ID")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or just whitespace")
        return v.strip()

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("Avatar URL must be a valid HTTP/HTTPS URL")
        return v


class UserUpdate(BaseModel):
    """Pydantic model for updating a user"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar_url: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    is_verified: Optional[bool] = Field(None)
    last_sign_in_at: Optional[datetime] = Field(None)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Name cannot be empty or just whitespace")
        return v.strip() if v else v

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("Avatar URL must be a valid HTTP/HTTPS URL")
        return v


class UserInDB(BaseModel):
    """Pydantic model for user data from database"""

    id: uuid.UUID
    email: str
    name: str
    avatar_url: Optional[str] = None
    google_id: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_sign_in_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserPublic(BaseModel):
    """Pydantic model for public user data (API responses)"""

    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    created_at: str
    last_sign_in_at: Optional[str] = None

    @classmethod
    def from_db_user(cls, user: UserInDB) -> "UserPublic":
        """Convert database user to public user model"""
        return cls(
            id=str(user.id),
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            created_at=user.created_at.isoformat() + "Z",
            last_sign_in_at=(
                user.last_sign_in_at.isoformat() + "Z" if user.last_sign_in_at else None
            ),
        )


class GoogleOAuthData(BaseModel):
    """Pydantic model for Google OAuth data"""

    google_id: str
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    email_verified: bool = False

    @field_validator("google_id")
    @classmethod
    def validate_google_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Google ID cannot be empty")
        return v.strip()
