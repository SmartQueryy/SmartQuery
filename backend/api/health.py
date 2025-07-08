from datetime import datetime
from fastapi import APIRouter
from typing import Dict, Any

from services.database_service import db_service
from services.redis_service import redis_service
from services.storage_service import storage_service

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Detailed health check endpoint with infrastructure service checks"""
    
    # Check all services
    database_health = db_service.health_check()
    redis_health = redis_service.health_check()
    storage_health = storage_service.health_check()
    
    # Determine overall status
    all_healthy = (
        database_health.get("status") == "healthy" and
        redis_health.get("status") == "healthy" and
        storage_health.get("status") == "healthy"
    )
    
    overall_status = "healthy" if all_healthy else "partial"
    
    return {
        "success": True,
        "data": {
            "status": overall_status,
            "service": "SmartQuery API",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {
                "database": database_health.get("status") == "healthy",
                "redis": redis_health.get("status") == "healthy",
                "storage": storage_health.get("status") == "healthy",
                "llm_service": False,  # Will be implemented in Task B15
            },
            "details": {
                "database": database_health,
                "redis": redis_health,
                "storage": storage_health,
            }
        },
    } 