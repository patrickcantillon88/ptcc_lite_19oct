"""
Migration script to create context tables (Staff, Timetable, etc.)
Run: python backend/migrations/create_context_tables.py
"""

from backend.core.database import Base, engine
from backend.models.database_models import (
    Staff, Timetable, SpecialistLessonSchedule, StudentAccommodation
)

def migrate():
    """Create all context tables"""
    print("Creating context tables...")
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("✅ Staff table created")
    print("✅ Timetable table created")
    print("✅ SpecialistLessonSchedule table created")
    print("✅ StudentAccommodation table created")
    print("\nAll context tables created successfully!")

if __name__ == "__main__":
    migrate()
