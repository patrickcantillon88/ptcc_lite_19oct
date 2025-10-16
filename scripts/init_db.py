#!/usr/bin/env python3
"""
Initialize PTCC database
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Import with absolute path to avoid relative import issues
import backend.core.database as db_module
import backend.core.logging_config as logging_module

create_tables = db_module.create_tables
setup_logging = logging_module.setup_logging

def main():
    """Initialize database with tables"""
    setup_logging()
    print("Initializing PTCC database...")
    
    try:
        create_tables()
        print("Database initialized successfully!")
        print("Run 'python -m backend.scripts.import_sample' to add sample data")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())