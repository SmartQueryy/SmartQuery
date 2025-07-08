from typing import Any, Optional, Generic, TypeVar, List, Dict
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """Standard API response format matching the frontend contract"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None

class HealthStatus(BaseModel):
    """Health check status model"""
    status: str
    service: str
    version: str
    timestamp: str
    checks: dict

class HealthChecks(BaseModel):
    """Individual health checks"""
    database: bool
    redis: bool
    storage: bool
    llm_service: bool

class ValidationError(BaseModel):
    """Validation error details"""
    field: str
    message: str
    code: str

class ApiError(BaseModel):
    """API error response format"""
    error: str
    message: str
    code: int
    details: Optional[List[ValidationError]] = None
    timestamp: str

# ===========================================
# AUTHENTICATION MODELS
# ===========================================

class User(BaseModel):
    """User model"""
    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    created_at: str
    last_sign_in_at: Optional[str] = None

class LoginRequest(BaseModel):
    """Google OAuth login request"""
    google_token: str

class AuthResponse(BaseModel):
    """Authentication response"""
    user: User
    access_token: str
    refresh_token: str
    expires_in: int

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str

# ===========================================
# PROJECT MODELS
# ===========================================

class ProjectStatus(str, Enum):
    """Project status enum"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"

class ColumnMetadata(BaseModel):
    """Column metadata model"""
    name: str
    type: str
    nullable: bool
    sample_values: List[Any]
    unique_count: Optional[int] = None

class Project(BaseModel):
    """Project model"""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    csv_filename: str
    csv_path: str
    row_count: int
    column_count: int
    columns_metadata: List[ColumnMetadata]
    created_at: str
    updated_at: str
    status: ProjectStatus

class CreateProjectRequest(BaseModel):
    """Create project request"""
    name: str
    description: Optional[str] = None

class CreateProjectResponse(BaseModel):
    """Create project response"""
    project: Project
    upload_url: str
    upload_fields: Dict[str, str]

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    limit: int = 20

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response"""
    items: List[T]
    total: int
    page: int
    limit: int
    hasMore: bool

class UploadStatusResponse(BaseModel):
    """Upload status response"""
    project_id: str
    status: str
    progress: int
    message: str

# ===========================================
# CHAT & QUERY MODELS
# ===========================================

class ChatMessage(BaseModel):
    """Chat message model"""
    id: str
    project_id: str
    user_id: str
    content: str
    role: str  # 'user' or 'assistant'
    created_at: str
    metadata: Optional[Dict[str, Any]] = None

class SendMessageRequest(BaseModel):
    """Send message request"""
    message: str
    context: Optional[List[str]] = None

class QueryResult(BaseModel):
    """Query result model"""
    id: str
    query: str
    sql_query: str
    result_type: str  # 'table', 'chart', 'summary'
    data: List[Dict[str, Any]]
    execution_time: float
    row_count: int
    chart_config: Optional[Dict[str, Any]] = None

class SendMessageResponse(BaseModel):
    """Send message response"""
    message: ChatMessage
    result: QueryResult

class CSVPreview(BaseModel):
    """CSV preview model"""
    columns: List[str]
    sample_data: List[List[Any]]
    total_rows: int
    data_types: Dict[str, str]

class QuerySuggestion(BaseModel):
    """Query suggestion model"""
    id: str
    text: str
    category: str
    complexity: str 