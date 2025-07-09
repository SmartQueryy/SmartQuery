import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import Boolean, Column, DateTime, String, Text, TypeDecorator, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.project import ProjectTable


class UUID(TypeDecorator):
    """
    Platform-independent UUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as string.
    """

    impl = PG_UUID
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(String(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class UserTable(Base):
    """SQLAlchemy User table model for PostgreSQL"""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url = Column(Text, nullable=True)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    projects: Mapped[List["ProjectTable"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    # chat_messages: Mapped[List["ChatMessageTable"]] = relationship(
    #     back_populates="user", cascade="all, delete-orphan"
    # )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"


# Pydantic models for API validation and serialization


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    google_id: str
    name: str  # Make name required for UserCreate

    @field_validator("name", "google_id")
    @classmethod
    def validate_non_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserInDB(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoogleOAuthData(BaseModel):
    google_id: str
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    email_verified: bool = True

    @field_validator("name", "google_id", "email")
    @classmethod
    def strip_whitespace(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    class Config:
        from_attributes = True
