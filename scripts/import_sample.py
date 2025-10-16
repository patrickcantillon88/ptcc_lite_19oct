#!/usr/bin/env python3
"""
Import sample data for PTCC
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.database import create_tables
from backend.core.logging_config import setup_logging

def main():
    """Import sample data"""
    setup_logging()
    print("Importing sample data...")
    
    try:
        # Initialize database first
        create_tables()
        
        # Import sample data
        from backend.scripts.import_sample import main as import_sample_data
        import_sample_data()
        
        print("Sample data imported successfully!")
    except Exception as e:
        print(f"Error importing sample data: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())