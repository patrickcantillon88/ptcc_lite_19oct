"""
Database connection and schema management
"""

import os
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .config import get_settings, get_database_path
from .logging_config import get_logger

logger = get_logger("database")

# Create database URL
settings = get_settings()
database_path = get_database_path()

# Ensure data directory exists
database_dir = os.path.dirname(database_path)
if not os.path.exists(database_dir):
    os.makedirs(database_dir)

# Create SQLite engine with WAL mode for better concurrency
engine = create_engine(
    f"sqlite:///{database_path}",
    connect_args={
        "check_same_thread": False,  # Allow multiple threads
    },
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=settings.get("system", {}).get("debug", False)  # Log SQL in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    try:
        # Import all SQLAlchemy models to ensure they are registered with SQLAlchemy
        from ..models.database_models import (
            Student, Schedule, ClassRoster, QuickLog, Assessment,
            Reminder, DutyRota, Communication, CCA, ActionItem, NameDrillProgress
        )

        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def get_database_stats() -> dict:
    """Get database statistics"""
    db = SessionLocal()
    try:
        stats = {}

        # Count records in each table
        tables = [
            "students", "quick_logs", "assessments", "schedule",
            "communications", "reminders", "duty_rotas"
        ]

        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                stats[table] = count
            except Exception as e:
                logger.warning(f"Could not count {table}: {e}")
                stats[table] = 0

        # Get database file size
        if os.path.exists(database_path):
            stats["database_size_mb"] = round(os.path.getsize(database_path) / (1024 * 1024), 2)
        else:
            stats["database_size_mb"] = 0

        return stats

    finally:
        db.close()


def backup_database(backup_path=None):
    """Create a backup of the database"""
    if backup_path is None:
        backup_dir = os.path.expanduser(settings["data"]["backups"])
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, "school_backup_{}.db".format(timestamp))

    import shutil
    shutil.copy2(database_path, backup_path)
    logger.info(f"Database backed up to: {backup_path}")
    return backup_path


def restore_database(backup_path):
    """Restore database from backup"""
    if not os.path.exists(backup_path):
        raise FileNotFoundError("Backup file not found: {}".format(backup_path))

    # Create backup of current database
    current_backup = backup_database()

    try:
        # Replace current database with backup
        import shutil
        shutil.copy2(backup_path, database_path)
        logger.info(f"Database restored from: {backup_path}")
        logger.info(f"Previous database backed up to: {current_backup}")
    except Exception as e:
        logger.error(f"Error restoring database: {e}")
        raise


def reset_database():
    """Reset database (development only)"""
    if not settings.get("system", {}).get("debug", False):
        raise ValueError("Database reset only allowed in debug mode")

    confirm = input("Are you sure you want to reset the database? This will delete all data! (type 'yes' to confirm): ")
    if confirm != "yes":
        print("Database reset cancelled")
        return

    # Close all connections
    engine.dispose()

    # Remove database file
    if os.path.exists(database_path):
        os.unlink(database_path)

    # Recreate tables
    create_tables()
    logger.warning("Database has been reset")


# Database health check
def check_database_health() -> dict:
    """Check database health and return status"""
    try:
        db = SessionLocal()

        # Test basic query
        from sqlalchemy import text
        result = db.execute(text("SELECT 1"))
        result.scalar()

        # Get stats
        stats = get_database_stats()

        db.close()

        return {
            "status": "healthy",
            "stats": stats,
            "database_path": database_path
        }

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database_path": database_path
        }