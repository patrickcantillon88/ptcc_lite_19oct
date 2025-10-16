#!/usr/bin/env python3
"""
Migration 003: Add ICT Behavior Management fields to QuickLog table

Adds:
- strike_level: Integer (1, 2, or 3)
- consequence_text: Text description of consequence
- admin_notified: Boolean flag for admin notification
- hod_consulted: Boolean flag for HOD consultation
- parent_meeting_scheduled: Boolean flag for parent meeting
- lesson_session_id: String to group logs by lesson session
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_migration():
    """Add ICT behavior fields to quick_logs table"""
    # Use hardcoded path - adjust if your DB is elsewhere
    db_path = Path("data/school.db")
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    print(f"📁 Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(quick_logs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        migrations_needed = []
        
        if 'strike_level' not in columns:
            migrations_needed.append(
                "ALTER TABLE quick_logs ADD COLUMN strike_level INTEGER"
            )
        
        if 'consequence_text' not in columns:
            migrations_needed.append(
                "ALTER TABLE quick_logs ADD COLUMN consequence_text TEXT"
            )
        
        if 'admin_notified' not in columns:
            migrations_needed.append(
                "ALTER TABLE quick_logs ADD COLUMN admin_notified INTEGER DEFAULT 0"
            )
        
        if 'hod_consulted' not in columns:
            migrations_needed.append(
                "ALTER TABLE quick_logs ADD COLUMN hod_consulted INTEGER DEFAULT 0"
            )
        
        if 'parent_meeting_scheduled' not in columns:
            migrations_needed.append(
                "ALTER TABLE quick_logs ADD COLUMN parent_meeting_scheduled INTEGER DEFAULT 0"
            )
        
        if 'lesson_session_id' not in columns:
            migrations_needed.append(
                "ALTER TABLE quick_logs ADD COLUMN lesson_session_id TEXT"
            )
        
        if not migrations_needed:
            print("✅ All ICT behavior columns already exist!")
            return True
        
        # Run migrations
        print(f"\n🔄 Running {len(migrations_needed)} migrations...")
        for sql in migrations_needed:
            print(f"   Executing: {sql}")
            cursor.execute(sql)
        
        # Create index for lesson_session_id for faster queries
        print("   Creating index on lesson_session_id...")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_quick_logs_lesson_session "
            "ON quick_logs(lesson_session_id)"
        )
        
        conn.commit()
        
        print("\n✅ Migration completed successfully!")
        print("\nAdded fields:")
        print("  - strike_level (INTEGER)")
        print("  - consequence_text (TEXT)")
        print("  - admin_notified (INTEGER/BOOLEAN)")
        print("  - hod_consulted (INTEGER/BOOLEAN)")
        print("  - parent_meeting_scheduled (INTEGER/BOOLEAN)")
        print("  - lesson_session_id (TEXT)")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
