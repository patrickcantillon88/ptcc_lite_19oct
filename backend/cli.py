#!/usr/bin/env python3
"""
Command Line Interface for PTCC
Main entry point for teachers to get briefings and manage data
"""

import argparse
import sys
import os
from datetime import date, datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from backend.core.briefing_engine import generate_daily_briefing, format_briefing_text
from backend.core.database import check_database_health, get_database_stats
from backend.core.logging_config import setup_logging
from backend.core.config import get_settings


def show_briefing(args):
    """Show daily briefing"""
    try:
        print("Generating briefing...")
        briefing = generate_daily_briefing()

        if args.format == "text":
            print(format_briefing_text(briefing))
        else:
            # JSON format for API consumption
            import json
            print(json.dumps(briefing.to_dict(), indent=2))

    except Exception as e:
        print("Error generating briefing: {}".format(e))
        return 1
    return 0


def show_health(args):
    """Show system health"""
    try:
        health = check_database_health()
        stats = get_database_stats()

        print("PTCC System Health")
        print("=" * 30)
        print("Status: {}".format(health['status']))
        print("Database: {}".format(health.get('path', 'unknown')))

        if health['status'] == 'healthy':
            print("\nDatabase Statistics:")
            for table, count in stats.items():
                if table != 'database_size_mb':
                    print(f"  {table}: {count} records")

            print("\nDatabase size: {} MB".format(stats.get('database_size_mb', 0)))
        else:
            print("Error: {}".format(health.get('error', 'Unknown error')))

    except Exception as e:
        print("Error checking health: {}".format(e))
        return 1
    return 0


def init_database(args):
    """Initialize database"""
    try:
        from backend.core.database import create_tables

        print("Initializing database...")
        create_tables()
        print("Database initialized successfully")

        if not args.skip_sample:
            print("Importing sample data...")
            from backend.scripts.import_sample import main as import_sample
            import_sample()
            print("Sample data imported")

        return 0

    except Exception as e:
        print("Error initializing database: {}".format(e))
        return 1


def search_data(args):
    """Search across all data"""
    try:
        # For now, just search students
        # TODO: Implement full RAG search
        from sqlalchemy.orm import Session
        from backend.models.database_models import Student
        from backend.core.database import SessionLocal

        db = SessionLocal()
        try:
            students = db.query(Student).filter(
                Student.name.contains(args.query)
            ).limit(10).all()

            if students:
                print("Search results for '{}':".format(args.query))
                for student in students:
                    print("  • {} ({}, Year {})".format(student.name, student.class_code, student.year_group))
            else:
                print("No results found for '{}'".format(args.query))

        finally:
            db.close()

    except Exception as e:
        print("Error searching: {}".format(e))
        return 1
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Personal Teaching Command Center",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py briefing                    # Get today's briefing
  python cli.py briefing --format json     # Get briefing as JSON
  python cli.py health                      # Check system health
  python cli.py init --skip-sample         # Initialize without sample data
  python cli.py search "Emma Chen"         # Search for student
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Briefing command
    briefing_parser = subparsers.add_parser("briefing", help="Generate daily briefing")
    briefing_parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)"
    )
    briefing_parser.set_defaults(func=show_briefing)

    # Health command
    health_parser = subparsers.add_parser("health", help="Check system health")
    health_parser.set_defaults(func=show_health)

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize database")
    init_parser.add_argument(
        "--skip-sample", action="store_true",
        help="Skip importing sample data"
    )
    init_parser.set_defaults(func=init_database)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search across data")
    search_parser.add_argument("query", help="Search query")
    search_parser.set_defaults(func=search_data)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Setup logging and configuration
    setup_logging()
    settings = get_settings()

    # Execute command
    return args.func(args)


if __name__ == "__main__":
    exit(main())