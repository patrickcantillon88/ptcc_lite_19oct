"""
Populate Class Roster Assignments for BIS HCMC Students

This script creates class roster entries linking the 16 BIS HCMC students
to their appropriate classes (7A, 7B, 8A, 8B).
"""

import sys
import os
# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal, create_tables
from backend.models.database_models import Student, ClassRoster
from backend.core.logging_config import get_logger

logger = get_logger("populate_rosters")


def populate_class_rosters():
    """Populate the ClassRoster table with student-class assignments"""
    logger.info("Starting class roster population...")

    db = SessionLocal()
    try:
        # Get all students
        students = db.query(Student).all()
        logger.info(f"Found {len(students)} students in database")

        # Filter for BIS HCMC students (classes 3A, 4B, 5C, 6D - these are the actual classes in the data)
        bis_students = [s for s in students if s.class_code in ['3A', '4B', '5C', '6D']]
        logger.info(f"Found {len(bis_students)} BIS HCMC students")

        # Create roster entries
        roster_entries = []
        for student in bis_students:
            roster = ClassRoster(
                class_code=student.class_code,
                student_id=student.id
            )
            roster_entries.append(roster)

        # Insert roster entries
        if roster_entries:
            db.add_all(roster_entries)
            db.commit()
            logger.info(f"Successfully created {len(roster_entries)} class roster entries")

            # Log class distribution
            class_counts = {}
            for student in bis_students:
                class_counts[student.class_code] = class_counts.get(student.class_code, 0) + 1

            logger.info("Class distribution:")
            for class_code, count in class_counts.items():
                logger.info(f"  {class_code}: {count} students")

        else:
            logger.warning("No roster entries to create")

        return len(roster_entries)

    except Exception as e:
        logger.error(f"Error populating class rosters: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function"""
    logger.info("BIS HCMC Class Roster Population Script")
    logger.info("=" * 50)

    try:
        count = populate_class_rosters()
        logger.info(f"✅ Successfully populated {count} class roster entries")
        return 0
    except Exception as e:
        logger.error(f"❌ Failed to populate class rosters: {e}")
        return 1


if __name__ == "__main__":
    exit(main())