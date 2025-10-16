#!/usr/bin/env python3
"""
Database migration: Add cca_subject column to quick_logs table

This migration adds support for CCA (Co-Curricular Activities) comments
by adding a cca_subject field to the existing quick_logs table.
"""

import sqlite3
import sys
from pathlib import Path

def migrate_database(db_path: str = "data/ptcc.db"):
    """Add cca_subject column to quick_logs table"""
    
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"❌ Database not found: {db_path}")
        print("Creating new database with CCA support...")
        # Database will be created automatically on first run
        return True
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(quick_logs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'cca_subject' in columns:
            print("✅ Database already has cca_subject column")
            return True
        
        # Add cca_subject column
        print("📝 Adding cca_subject column to quick_logs table...")
        cursor.execute("""
            ALTER TABLE quick_logs 
            ADD COLUMN cca_subject TEXT
        """)
        
        # Create index on cca_subject
        print("📇 Creating index on cca_subject...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_quick_logs_cca_subject 
            ON quick_logs(cca_subject)
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/ptcc.db"
    success = migrate_database(db_path)
    sys.exit(0 if success else 1)
