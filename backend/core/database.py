"""
Database Configuration and Connection Management
Handles PostgreSQL connections for neurosurgical knowledge system
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import create_engine, text
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator, Optional
import asyncio
from datetime import datetime

from config.settings import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.database_url_async,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_pre_ping=True,  # Verify connections before using
    connect_args={
        "server_settings": {"jit": "off"},
        "command_timeout": 60,
        "timeout": 30,
    } if "postgresql" in settings.database_url_async else {}
)

# Create sync engine for migrations
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_pre_ping=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


class DatabaseManager:
    """
    Manages database connections and transactions
    """

    @staticmethod
    @asynccontextmanager
    async def get_session() -> AsyncGenerator[AsyncSession, None]:
        """
        Async context manager for database sessions
        """
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database transaction error: {e}")
                raise
            finally:
                await session.close()

    @staticmethod
    async def init_db():
        """
        Initialize database tables and indexes
        """
        try:
            logger.info("Initializing database...")

            # Import all models to register them
            from models.database import (
                User, Textbook, BookChapter, Chapter, SurgicalProcedure,
                Reference, QASession, UserInteraction, SynthesisJob,
                CitationNetwork, MedicalImage
            )

            # Create tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # Create custom indexes for neurosurgical queries
            await DatabaseManager.create_custom_indexes()

            # Create full-text search configurations
            await DatabaseManager.setup_text_search()

            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    @staticmethod
    async def create_custom_indexes():
        """
        Create custom indexes for neurosurgical queries
        """
        custom_indexes = [
            # Specialty-based queries
            "CREATE INDEX IF NOT EXISTS idx_chapter_specialty_status ON chapters(specialty, status)",
            "CREATE INDEX IF NOT EXISTS idx_textbook_specialty_processed ON textbooks(specialty, is_processed)",

            # Anatomical region queries
            "CREATE INDEX IF NOT EXISTS idx_chapter_anatomy_gin ON chapters USING gin(anatomical_focus)",
            "CREATE INDEX IF NOT EXISTS idx_procedure_anatomy ON surgical_procedures(anatomical_region)",

            # Medical code queries
            "CREATE INDEX IF NOT EXISTS idx_chapter_icd10 ON chapters USING gin(icd10_codes)",
            "CREATE INDEX IF NOT EXISTS idx_chapter_cpt ON chapters USING gin(cpt_codes)",

            # Performance indexes
            "CREATE INDEX IF NOT EXISTS idx_synthesis_user_status ON synthesis_jobs(user_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_qa_chapter_timestamp ON qa_sessions(chapter_id, asked_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_interaction_user_type ON user_interactions(user_id, interaction_type)",

            # Citation network indexes
            "CREATE INDEX IF NOT EXISTS idx_citation_strength ON citation_networks(citation_strength DESC)",
        ]

        async with engine.begin() as conn:
            for index_sql in custom_indexes:
                try:
                    await conn.execute(text(index_sql))
                    logger.debug(f"Created index: {index_sql[:50]}...")
                except Exception as e:
                    logger.warning(f"Index creation skipped (may already exist): {e}")

    @staticmethod
    async def setup_text_search():
        """
        Setup PostgreSQL full-text search for medical content
        """
        try:
            async with engine.begin() as conn:
                # Create text search configuration for medical terms
                await conn.execute(text("""
                    CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS medical_english (COPY = english);
                """))

                # Add medical dictionaries (would need actual medical dictionary files)
                # This is a placeholder for actual medical dictionary setup
                await conn.execute(text("""
                    COMMENT ON TEXT SEARCH CONFIGURATION medical_english IS
                    'Text search configuration for medical and neurosurgical terms';
                """))

                # Create function to update search vectors
                await conn.execute(text("""
                    CREATE OR REPLACE FUNCTION update_search_vector() RETURNS trigger AS $$
                    BEGIN
                        NEW.search_vector :=
                            setweight(to_tsvector('medical_english', COALESCE(NEW.title, '')), 'A') ||
                            setweight(to_tsvector('medical_english', COALESCE(NEW.content::text, '')), 'B');
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                """))

                # Create triggers for automatic search vector updates
                triggers = [
                    ("chapters", "title, content"),
                    ("textbooks", "title, authors::text")
                ]

                for table, columns in triggers:
                    await conn.execute(text(f"""
                        CREATE TRIGGER update_{table}_search_vector
                        BEFORE INSERT OR UPDATE ON {table}
                        FOR EACH ROW EXECUTE FUNCTION update_search_vector();
                    """))

                logger.info("Text search configuration completed")

        except Exception as e:
            logger.warning(f"Text search setup partial completion: {e}")

    @staticmethod
    async def check_database_health() -> dict:
        """
        Check database health and connectivity
        """
        try:
            start_time = datetime.utcnow()

            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                await result.scalar()

                # Get database statistics
                stats_query = text("""
                    SELECT
                        (SELECT COUNT(*) FROM users) as user_count,
                        (SELECT COUNT(*) FROM chapters) as chapter_count,
                        (SELECT COUNT(*) FROM textbooks) as textbook_count,
                        (SELECT COUNT(*) FROM qa_sessions) as qa_count,
                        pg_database_size(current_database()) as db_size_bytes
                """)

                stats_result = await conn.execute(stats_query)
                stats = dict(stats_result.first()._mapping)

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "statistics": stats,
                "pool_size": engine.pool.size() if hasattr(engine.pool, 'size') else None,
                "pool_checked_in": engine.pool.checkedin() if hasattr(engine.pool, 'checkedin') else None,
            }

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    @staticmethod
    async def backup_database(backup_path: str):
        """
        Create database backup (requires pg_dump)
        """
        try:
            import subprocess
            from urllib.parse import urlparse

            # Parse database URL
            db_url = urlparse(settings.DATABASE_URL)

            # Construct pg_dump command
            command = [
                "pg_dump",
                "-h", db_url.hostname or "localhost",
                "-p", str(db_url.port or 5432),
                "-U", db_url.username or "postgres",
                "-d", db_url.path.lstrip("/"),
                "-f", backup_path,
                "--verbose",
                "--format=custom",
                "--no-password"
            ]

            # Set PGPASSWORD environment variable
            env = {"PGPASSWORD": db_url.password or ""}

            # Run pg_dump
            result = subprocess.run(command, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"Database backup created: {backup_path}")
                return True
            else:
                logger.error(f"Database backup failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Database backup error: {e}")
            return False


# Database session dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions
    """
    async with DatabaseManager.get_session() as session:
        yield session


# Initialize database on module import (optional)
async def initialize_database():
    """
    Initialize database on application startup
    """
    await DatabaseManager.init_db()


# Utility functions for common queries
class DatabaseUtils:
    """
    Utility functions for common database operations
    """

    @staticmethod
    async def execute_query(query: str, params: Optional[dict] = None):
        """
        Execute a raw SQL query
        """
        async with engine.connect() as conn:
            result = await conn.execute(text(query), params or {})
            return result.fetchall()

    @staticmethod
    async def get_table_stats(table_name: str) -> dict:
        """
        Get statistics for a specific table
        """
        query = f"""
            SELECT
                COUNT(*) as row_count,
                pg_size_pretty(pg_total_relation_size('{table_name}')) as total_size,
                pg_size_pretty(pg_relation_size('{table_name}')) as table_size,
                pg_size_pretty(pg_indexes_size('{table_name}')) as indexes_size
            FROM {table_name}
        """

        async with engine.connect() as conn:
            result = await conn.execute(text(query))
            return dict(result.first()._mapping)

    @staticmethod
    async def vacuum_analyze():
        """
        Run VACUUM ANALYZE on all tables (maintenance)
        """
        tables = [
            "users", "textbooks", "book_chapters", "chapters",
            "surgical_procedures", "references", "qa_sessions",
            "user_interactions", "synthesis_jobs", "citation_networks",
            "medical_images"
        ]

        async with engine.connect() as conn:
            for table in tables:
                try:
                    await conn.execute(text(f"VACUUM ANALYZE {table}"))
                    logger.info(f"VACUUM ANALYZE completed for {table}")
                except Exception as e:
                    logger.warning(f"VACUUM ANALYZE failed for {table}: {e}")


# Export for use in other modules
__all__ = [
    "engine",
    "Base",
    "AsyncSessionLocal",
    "DatabaseManager",
    "get_db",
    "initialize_database",
    "DatabaseUtils",
    "check_database_health"
]