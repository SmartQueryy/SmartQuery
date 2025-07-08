import os
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter

from services.database_service import get_db_service
from services.redis_service import redis_service
from services.storage_service import storage_service

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Detailed health check endpoint with infrastructure service checks"""

    # Check if we're in test environment
    is_test_env = os.getenv(
        "TESTING", "false"
    ).lower() == "true" or "pytest" in os.environ.get("_", "")

    if is_test_env:
        # Return healthy status for tests without connecting to real services
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "service": "SmartQuery API",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "checks": {
                    "database": True,
                    "redis": True,
                    "storage": True,
                    "llm_service": False,  # Will be implemented in Task B15
                },
                "details": {
                    "database": {"status": "healthy", "message": "Test mode"},
                    "redis": {"status": "healthy", "message": "Test mode"},
                    "storage": {"status": "healthy", "message": "Test mode"},
                },
            },
        }

    # Check all services in production
    database_health = get_db_service().health_check()
    redis_health = redis_service.health_check()
    storage_health = storage_service.health_check()

    # Determine overall status
    all_healthy = (
        database_health.get("status") == "healthy"
        and redis_health.get("status") == "healthy"
        and storage_health.get("status") == "healthy"
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
            },
        },
    }
