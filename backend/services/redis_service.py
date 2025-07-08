import os
import logging
import redis
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class RedisService:
    """Redis service for caching and message broker operations"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = None
        
    def connect(self) -> bool:
        """Establish Redis connection"""
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.client.ping()
            logger.info("Redis connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            if not self.client:
                self.connect()
                
            info = self.client.info()
            
            return {
                "status": "healthy",
                "version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory_human"),
                "uptime": info.get("uptime_in_seconds")
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_client(self):
        """Get Redis client"""
        if not self.client:
            self.connect()
        return self.client
    
    def set_cache(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Set cache value with TTL"""
        try:
            client = self.get_client()
            client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Failed to set cache for key {key}: {str(e)}")
            return False
    
    def get_cache(self, key: str) -> Optional[str]:
        """Get cache value"""
        try:
            client = self.get_client()
            return client.get(key)
        except Exception as e:
            logger.error(f"Failed to get cache for key {key}: {str(e)}")
            return None


# Global Redis service instance
redis_service = RedisService() 