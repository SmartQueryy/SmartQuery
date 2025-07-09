# Models package for SmartQuery backend

# Import all models to ensure they are registered with SQLAlchemy
from models.base import Base
from models.project import (
    ColumnMetadata,
    ProjectBase,
    ProjectCreate,
    ProjectInDB,
    ProjectPublic,
    ProjectStatusEnum,
    ProjectTable,
    ProjectUpdate,
)
from models.response_schemas import (
    ApiResponse,
    AuthResponse,
    ChatMessage,
    CreateProjectRequest,
    CreateProjectResponse,
    CSVPreview,
    HealthChecks,
    HealthStatus,
    PaginatedResponse,
    PaginationParams,
    Project,
    QueryResult,
    QuerySuggestion,
    UploadStatusResponse,
    User,
    ValidationError,
)
from models.user import (
    GoogleOAuthData,
    UserBase,
    UserCreate,
    UserInDB,
    UserTable,
    UserUpdate,
)

__all__ = [
    # Base
    "Base",
    # User models
    "UserTable",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "GoogleOAuthData",
    # Project models
    "ProjectTable",
    "ProjectStatusEnum",
    "ColumnMetadata",
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectInDB",
    "ProjectPublic",
    # Response schemas
    "ApiResponse",
    "HealthStatus",
    "HealthChecks",
    "ValidationError",
    "User",
    "AuthResponse",
    "Project",
    "CreateProjectRequest",
    "CreateProjectResponse",
    "PaginationParams",
    "PaginatedResponse",
    "UploadStatusResponse",
    "ChatMessage",
    "QueryResult",
    "CSVPreview",
    "QuerySuggestion",
]
