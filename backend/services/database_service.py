import logging
import os
from typing import Any, Dict, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

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

    def create_tables(self):
        """Create database tables using SQLAlchemy models"""
        try:
            from models.user import Base

            if not self.engine:
                self.connect()

            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            return False

    def run_migration(self, migration_file: str) -> bool:
        """Run a SQL migration file"""
        try:
            if not self.engine:
                self.connect()

            migration_path = f"database/migrations/{migration_file}"

            if not os.path.exists(migration_path):
                logger.error(f"Migration file not found: {migration_path}")
                return False

            with open(migration_path, "r") as f:
                migration_sql = f.read()

            with self.engine.connect() as conn:
                # Execute migration
                conn.execute(text(migration_sql))
                conn.commit()

            logger.info(f"Migration {migration_file} executed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to run migration {migration_file}: {str(e)}")
            return False


# Global database service instance
db_service = DatabaseService()
