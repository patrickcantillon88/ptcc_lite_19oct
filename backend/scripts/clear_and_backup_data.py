"""
Data Clearing Script for PTCC

Safely clears all existing data while preserving database schema and creating backup.
This script is designed to prepare the database for importing the comprehensive BIS HCMC dataset.

Author: PTCC System
Date: 2025-10-14
"""

import os
import sys
import shutil
from datetime import datetime
from typing import Dict, List, Tuple
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker, Session

# Add the backend directory to the path so we can import modules
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from ..core.database import (
    SessionLocal, create_tables, backup_database, get_database_path,
    get_database_stats, check_database_health
)
from ..core.logging_config import get_logger
from ..core.config import get_settings

logger = get_logger("clear_and_backup")
settings = get_settings()

# Core tables that need to be cleared (in dependency order)
CORE_TABLES = [
    "quick_logs",      # No dependencies
    "assessments",     # Depends on students
    "class_rosters",   # Depends on students
    "ccas",           # Depends on students
    "communications",  # No dependencies
    "duty_rotas",     # No dependencies
    "reminders",      # No dependencies
    "action_items",   # No dependencies
    "name_drill_progress",  # Depends on students
    "schedule",       # No dependencies
    "students"        # Cleared last (other tables depend on it)
]

# Tables to preserve (schema and structure only)
PRESERVE_TABLES = [
    # These tables typically don't need clearing as they contain system data
    # Add any system configuration tables here if they exist
]


class DataClearingError(Exception):
    """Custom exception for data clearing errors"""
    pass


def verify_backup_creation(backup_path: str) -> bool:
    """
    Verify that the backup was created successfully and is valid.

    Args:
        backup_path: Path to the backup file

    Returns:
        bool: True if backup is valid, False otherwise
    """
    try:
        if not os.path.exists(backup_path):
            logger.error(f"Backup file does not exist: {backup_path}")
            return False

        # Check file size (should be > 0)
        file_size = os.path.getsize(backup_path)
        if file_size == 0:
            logger.error(f"Backup file is empty: {backup_path}")
            return False

        logger.info(f"Backup verified successfully: {backup_path} ({file_size} bytes)")
        return True

    except Exception as e:
        logger.error(f"Error verifying backup: {e}")
        return False


def get_table_record_counts(db: Session) -> Dict[str, int]:
    """
    Get record counts for all tables before clearing.

    Args:
        db: Database session

    Returns:
        Dict mapping table names to record counts
    """
    counts = {}

    for table in CORE_TABLES + PRESERVE_TABLES:
        try:
            result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            counts[table] = count
            logger.info(f"Table {table}: {count} records")
        except Exception as e:
            logger.warning(f"Could not count records in {table}: {e}")
            counts[table] = 0

    return counts


def clear_table_data(db: Session, table_name: str, preserve_schema: bool = True) -> int:
    """
    Clear all data from a specific table while preserving schema.

    Args:
        db: Database session
        table_name: Name of table to clear
        preserve_schema: Whether to preserve table schema and indexes

    Returns:
        Number of records deleted
    """
    try:
        # Get count before deletion
        result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count_before = result.scalar()

        if count_before == 0:
            logger.info(f"Table {table_name} is already empty")
            return 0

        # Clear the table data
        if preserve_schema:
            # Use DELETE to preserve schema, indexes, and constraints
            db.execute(text(f"DELETE FROM {table_name}"))
            logger.info(f"Cleared {count_before} records from {table_name} (schema preserved)")
        else:
            # Use DROP TABLE (more aggressive, recreates schema)
            db.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            logger.info(f"Dropped table {table_name}")

        db.commit()
        return count_before

    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing table {table_name}: {e}")
        raise DataClearingError(f"Failed to clear table {table_name}: {e}")


def verify_clearing_success(db: Session) -> Dict[str, int]:
    """
    Verify that all core tables have been cleared successfully.

    Args:
        db: Database session

    Returns:
        Dict mapping table names to remaining record counts
    """
    remaining_counts = {}

    for table in CORE_TABLES:
        try:
            result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            remaining_counts[table] = count

            if count > 0:
                logger.warning(f"Table {table} still has {count} records after clearing")
            else:
                logger.info(f"Table {table} successfully cleared")

        except Exception as e:
            logger.error(f"Error checking table {table}: {e}")
            remaining_counts[table] = -1  # Error indicator

    return remaining_counts


def create_clearing_report(
    before_counts: Dict[str, int],
    after_counts: Dict[str, int],
    backup_path: str,
    start_time: datetime,
    end_time: datetime
) -> str:
    """
    Create a detailed report of the clearing operation.

    Args:
        before_counts: Record counts before clearing
        after_counts: Record counts after clearing
        backup_path: Path to the backup file
        start_time: Operation start time
        end_time: Operation end time

    Returns:
        Formatted report string
    """
    duration = end_time - start_time

    report = []
    report.append("=" * 80)
    report.append("PTCC DATA CLEARING REPORT")
    report.append("=" * 80)
    report.append(f"Operation completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Duration: {duration.total_seconds():.2f} seconds")
    report.append(f"Backup location: {backup_path}")
    report.append("")

    report.append("RECORDS CLEARED:")
    report.append("-" * 40)

    total_cleared = 0
    for table in CORE_TABLES:
        before = before_counts.get(table, 0)
        after = after_counts.get(table, 0)
        cleared = before - after

        if cleared > 0:
            report.append(f"{table:<20} : {cleared:>6} records")
            total_cleared += cleared

    report.append("-" * 40)
    report.append(f"{'TOTAL':<20} : {total_cleared:>6} records")
    report.append("")

    report.append("REMAINING RECORDS:")
    report.append("-" * 40)
    for table in CORE_TABLES:
        remaining = after_counts.get(table, 0)
        if remaining > 0:
            report.append(f"{table:<20} : {remaining:>6} records (WARNING)")

    if not any(after_counts.get(table, 0) > 0 for table in CORE_TABLES):
        report.append("All core tables successfully cleared!")
    else:
        report.append("WARNING: Some tables still contain data!")

    report.append("")
    report.append("=" * 80)

    return "\n".join(report)


def clear_all_data(dry_run: bool = False, force: bool = False) -> Dict:
    """
    Main function to clear all data while preserving schema.

    Args:
        dry_run: If True, only show what would be cleared without actually doing it
        force: If True, skip confirmation prompts

    Returns:
        Dict containing operation results and statistics
    """
    start_time = datetime.now()
    logger.info("Starting data clearing operation...")

    # Get initial database stats
    initial_stats = get_database_stats()
    logger.info(f"Initial database size: {initial_stats.get('database_size_mb', 0):.2f} MB")

    # Create database session
    db = SessionLocal()

    try:
        # Get record counts before clearing
        logger.info("Getting pre-clearing record counts...")
        before_counts = get_table_record_counts(db)

        if dry_run:
            logger.info("DRY RUN - No data will be modified")
            logger.info("Would clear the following records:")
            for table, count in before_counts.items():
                if count > 0:
                    logger.info(f"  {table}: {count} records")
            return {"success": True, "dry_run": True, "before_counts": before_counts}

        # Create backup before clearing
        logger.info("Creating database backup...")
        backup_path = backup_database()

        if not verify_backup_creation(backup_path):
            raise DataClearingError("Backup verification failed")

        # Confirm before proceeding (unless forced)
        if not force:
            confirm = input("Backup created. Proceed with data clearing? (type 'yes' to confirm): ")
            if confirm.lower() != 'yes':
                logger.info("Data clearing cancelled by user")
                return {"success": False, "cancelled": True, "backup_path": backup_path}

        # Clear data from each table
        logger.info("Starting data clearing...")
        total_cleared = 0

        for table in CORE_TABLES:
            if before_counts.get(table, 0) > 0:
                cleared_count = clear_table_data(db, table, preserve_schema=True)
                total_cleared += cleared_count

        # Verify clearing success
        logger.info("Verifying clearing operation...")
        after_counts = verify_clearing_success(db)

        # Check for any remaining records in core tables
        remaining_records = sum(after_counts.values())
        if remaining_records > 0:
            logger.warning(f"Some records remain after clearing: {remaining_records} total")

        # Get final database stats
        final_stats = get_database_stats()

        # Create report
        end_time = datetime.now()
        report = create_clearing_report(
            before_counts, after_counts, backup_path,
            start_time, end_time
        )

        # Log the report
        logger.info("Data clearing completed. Report:")
        logger.info("\n" + report)

        # Save report to file
        report_path = backup_path.replace('.db', '_clearing_report.txt')
        with open(report_path, 'w') as f:
            f.write(report)
        logger.info(f"Detailed report saved to: {report_path}")

        # Final verification
        if remaining_records == 0:
            logger.info("✅ Data clearing completed successfully!")
        else:
            logger.warning(f"⚠️  Data clearing completed with {remaining_records} remaining records")

        return {
            "success": remaining_records == 0,
            "total_cleared": total_cleared,
            "remaining_records": remaining_records,
            "backup_path": backup_path,
            "report_path": report_path,
            "before_counts": before_counts,
            "after_counts": after_counts,
            "initial_size_mb": initial_stats.get('database_size_mb', 0),
            "final_size_mb": final_stats.get('database_size_mb', 0),
            "duration_seconds": (end_time - start_time).total_seconds()
        }

    except Exception as e:
        logger.error(f"Error during data clearing: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main entry point for the script"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Clear PTCC database data while preserving schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clear_and_backup_data.py                    # Interactive mode
  python clear_and_backup_data.py --dry-run         # Show what would be cleared
  python clear_and_backup_data.py --force           # Skip confirmations
  python clear_and_backup_data.py --dry-run --force # Dry run without confirmation
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be cleared without actually doing it'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompts'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        logger.info("PTCC Data Clearing Script")
        logger.info("=" * 50)

        # Check database health first
        health = check_database_health()
        if health["status"] != "healthy":
            logger.error(f"Database health check failed: {health.get('error', 'Unknown error')}")
            return 1

        logger.info(f"Database status: {health['status']}")
        logger.info(f"Database path: {health['database_path']}")

        # Perform the clearing operation
        result = clear_all_data(dry_run=args.dry_run, force=args.force)

        if result.get("dry_run"):
            logger.info("Dry run completed - no data was modified")
            return 0

        if result.get("cancelled"):
            logger.info("Operation cancelled by user")
            return 0

        if result["success"]:
            logger.info("✅ Data clearing completed successfully!")
            logger.info(f"📦 Backup available at: {result['backup_path']}")
            logger.info(f"📊 Total records cleared: {result['total_cleared']}")
            return 0
        else:
            logger.error("❌ Data clearing completed with errors")
            logger.error(f"Remaining records: {result['remaining_records']}")
            return 1

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)