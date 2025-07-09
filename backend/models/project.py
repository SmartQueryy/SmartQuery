import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    TypeDecorator,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.user import UserTable


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


class CrossDatabaseJSON(TypeDecorator):
    """
    Platform-independent JSON type.

    Uses PostgreSQL's JSONB type for better performance,
    otherwise uses standard JSON type.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())


class ProjectStatusEnum(str, Enum):
    """Project status enumeration"""

    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class ProjectTable(Base):
    """SQLAlchemy Project table model for PostgreSQL"""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    csv_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    csv_path: Mapped[str] = mapped_column(Text, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    column_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    columns_metadata = Column(CrossDatabaseJSON, nullable=True)
    status: Mapped[ProjectStatusEnum] = mapped_column(
        SQLEnum(ProjectStatusEnum), nullable=False, default=ProjectStatusEnum.UPLOADING
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["UserTable"] = relationship(back_populates="projects")
    # chat_messages: Mapped[List["ChatMessageTable"]] = relationship(
    #     back_populates="project", cascade="all, delete-orphan"
    # )

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', user_id={self.user_id}, status='{self.status}')>"


# Pydantic models for API validation and serialization


class ColumnMetadata(BaseModel):
    """Column metadata model"""

    name: str
    type: str
    nullable: bool = True
    sample_values: List[Any] = Field(default_factory=list)
    unique_count: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    """Base project model with common fields"""

    name: str
    description: Optional[str] = None
    csv_filename: str
    csv_path: str
    row_count: int = 0
    column_count: int = 0
    columns_metadata: List[ColumnMetadata] = Field(default_factory=list)
    status: ProjectStatusEnum = ProjectStatusEnum.UPLOADING

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    """Project creation model"""

    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Project name cannot be empty")
        if len(v.strip()) > 255:
            raise ValueError("Project name cannot exceed 255 characters")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None and len(v.strip()) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
        return v.strip() if v else None

    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    """Project update model"""

    name: Optional[str] = None
    description: Optional[str] = None
    csv_filename: Optional[str] = None
    csv_path: Optional[str] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    columns_metadata: Optional[List[ColumnMetadata]] = None
    status: Optional[ProjectStatusEnum] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Project name cannot be empty")
            if len(v.strip()) > 255:
                raise ValueError("Project name cannot exceed 255 characters")
            return v.strip()
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None and len(v.strip()) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
        return v.strip() if v else None

    @field_validator("row_count", "column_count")
    @classmethod
    def validate_counts(cls, v):
        if v is not None and v < 0:
            raise ValueError("Counts cannot be negative")
        return v

    class Config:
        from_attributes = True


class ProjectInDB(ProjectBase):
    """Project model as stored in database"""

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectPublic(BaseModel):
    """Public project model for API responses"""

    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    csv_filename: str
    csv_path: str
    row_count: int
    column_count: int
    columns_metadata: List[ColumnMetadata]
    status: ProjectStatusEnum
    created_at: str
    updated_at: str

    @classmethod
    def from_db_project(cls, project: ProjectInDB) -> "ProjectPublic":
        """Convert ProjectInDB to ProjectPublic"""
        return cls(
            id=str(project.id),
            user_id=str(project.user_id),
            name=project.name,
            description=project.description,
            csv_filename=project.csv_filename,
            csv_path=project.csv_path,
            row_count=project.row_count,
            column_count=project.column_count,
            columns_metadata=project.columns_metadata,
            status=project.status,
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat(),
        )

    class Config:
        from_attributes = True
