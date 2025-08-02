import logging
import os
from typing import Any, Dict, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from models.base import Base
from middleware.monitoring import track_performance

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service to manage database connections"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.connect()

    def connect(self):
        """Establish connection to the database"""
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logger.error("DATABASE_URL environment variable not set.")
            raise ValueError("DATABASE_URL environment variable not set.")

        try:
            # Add SQLite-specific configuration for testing
            engine_kwargs = {}
            if db_url.startswith("sqlite://"):
                engine_kwargs["connect_args"] = {"check_same_thread": False}

            self.engine = create_engine(db_url, **engine_kwargs)
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )
            logger.info("Database connection established successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def reconnect(self):
        """Force a reconnection to the database."""
        self.connect()

    @track_performance("database_health_check")
    def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            if not self.engine:
                self.connect()

            with self.engine.connect() as conn:
                # Use database-specific version query
                if self.engine.dialect.name == "postgresql":
                    result = conn.execute(text("SELECT version()"))
                    version = result.fetchone()[0]
                elif self.engine.dialect.name == "sqlite":
                    result = conn.execute(text("SELECT sqlite_version()"))
                    version = f"SQLite {result.fetchone()[0]}"
                else:
                    version = f"{self.engine.dialect.name} (version unknown)"

                # Get basic stats - handle potential missing tables
                user_count = 0
                project_count = 0
                message_count = 0
                try:
                    stats_query = text(
                        """
                        SELECT 
                            (SELECT count(*) FROM users) as user_count,
                            (SELECT count(*) FROM projects) as project_count,
                            (SELECT count(*) FROM chat_messages) as message_count
                    """
                    )
                    stats = conn.execute(stats_query).fetchone()
                    user_count = stats.user_count
                    project_count = stats.project_count
                    message_count = stats.message_count
                except Exception:
                    # If tables don't exist, we can ignore for health check
                    pass

                return {
                    "status": "healthy",
                    "version": version,
                    "stats": {
                        "users": user_count,
                        "projects": project_count,
                        "messages": message_count,
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


_db_service_instance = None


def get_db_service():
    """Returns a singleton instance of the DatabaseService."""
    global _db_service_instance
    if _db_service_instance is None:
        _db_service_instance = DatabaseService()
    return _db_service_instance


def get_db():
    """FastAPI dependency to get a DB session"""
    db = get_db_service().get_session()
    try:
        yield db
    finally:
        db.close()
