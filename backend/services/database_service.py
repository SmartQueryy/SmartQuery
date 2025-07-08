import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DatabaseService:
    """Database service for PostgreSQL operations"""

    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://smartquery_user:smartquery_dev_password@localhost:5432/smartquery",
        )
        self.engine = None
        self.SessionLocal = None

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.engine = create_engine(self.database_url)
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info("Database connection established successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            if not self.engine:
                self.connect()

            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]

                # Get basic stats
                stats_query = text(
                    """
                    SELECT 
                        (SELECT count(*) FROM users) as user_count,
                        (SELECT count(*) FROM projects) as project_count,
                        (SELECT count(*) FROM chat_messages) as message_count
                """
                )
                stats = conn.execute(stats_query).fetchone()

                return {
                    "status": "healthy",
                    "version": version,
                    "stats": {
                        "users": stats.user_count,
                        "projects": stats.project_count,
                        "messages": stats.message_count,
                    },
                }

        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

    def get_session(self):
        """Get database session"""
        if not self.SessionLocal:
            self.connect()
        return self.SessionLocal()


# Global database service instance
db_service = DatabaseService()
