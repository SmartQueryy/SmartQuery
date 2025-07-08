from typing import Any, Optional, Generic, TypeVar, List
from pydantic import BaseModel
from datetime import datetime

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