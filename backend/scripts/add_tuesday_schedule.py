"""
Add Tuesday Schedule Data for BIS HCMC Classes

This script creates schedule entries for Tuesday classes to provide
the briefing with today's schedule data.
"""

import sys
import os
# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal, create_tables
from backend.models.database_models import Schedule
from backend.core.logging_config import get_logger

logger = get_logger("add_tuesday_schedule")


def add_tuesday_schedule():
    """Add Tuesday schedule entries for BIS HCMC classes"""
    logger.info("Starting Tuesday schedule creation...")

    db = SessionLocal()
    try:
        # Define Tuesday schedule for BIS HCMC classes
        # Note: The unique constraint is on (day_of_week, period), so we can only have one class per period per day
        # We'll create a schedule where different classes have different periods
        tuesday_schedule = [
            # Period 1: 3A English
            {"period": 1, "start_time": "08:30", "end_time": "09:15", "class_code": "3A", "subject": "English", "room": "3A"},
            # Period 2: 4B Mathematics
            {"period": 2, "start_time": "09:15", "end_time": "10:00", "class_code": "4B", "subject": "Mathematics", "room": "4B"},
            # Period 3: 5C Science
            {"period": 3, "start_time": "10:15", "end_time": "11:00", "class_code": "5C", "subject": "Science", "room": "Lab1"},
            # Period 4: 6D History
            {"period": 4, "start_time": "11:00", "end_time": "11:45", "class_code": "6D", "subject": "History", "room": "6D"},
            # Period 5: 3A Physical Education
            {"period": 5, "start_time": "12:30", "end_time": "13:15", "class_code": "3A", "subject": "Physical Education", "room": "Gym"},
            # Period 6: 4B Music
            {"period": 6, "start_time": "13:15", "end_time": "14:00", "class_code": "4B", "subject": "Music", "room": "MusicRoom"},
            # Period 7: 5C ICT
            {"period": 7, "start_time": "14:15", "end_time": "15:00", "class_code": "5C", "subject": "ICT", "room": "ComputerLab"},
            # Period 8: 6D Art
            {"period": 8, "start_time": "15:00", "end_time": "15:45", "class_code": "6D", "subject": "Art", "room": "ArtRoom"},
        ]

        # Check for existing Tuesday entries and create new ones
        schedule_entries = []
        for entry_data in tuesday_schedule:
            # Check if this entry already exists (note: unique constraint is on day_of_week + period only)
            existing = db.query(Schedule).filter(
                Schedule.day_of_week == "Tuesday",
                Schedule.period == entry_data["period"]
            ).first()

            if existing:
                logger.info(f"Schedule entry already exists: Tuesday P{entry_data['period']} {entry_data['class_code']}")
                continue

            # Create new schedule entry
            schedule_entry = Schedule(
                day_of_week="Tuesday",
                period=entry_data["period"],
                start_time=entry_data["start_time"],
                end_time=entry_data["end_time"],
                class_code=entry_data["class_code"],
                subject=entry_data["subject"],
                room=entry_data["room"]
            )
            schedule_entries.append(schedule_entry)

        # Insert new schedule entries
        if schedule_entries:
            db.add_all(schedule_entries)
            db.commit()
            logger.info(f"Successfully created {len(schedule_entries)} Tuesday schedule entries")

            # Log schedule summary
            class_counts = {}
            for entry in schedule_entries:
                class_counts[entry.class_code] = class_counts.get(entry.class_code, 0) + 1

            logger.info("Tuesday schedule summary:")
            for class_code, count in class_counts.items():
                logger.info(f"  {class_code}: {count} periods")

        else:
            logger.info("No new Tuesday schedule entries to create")

        return len(schedule_entries)

    except Exception as e:
        logger.error(f"Error adding Tuesday schedule: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function"""
    logger.info("BIS HCMC Tuesday Schedule Creation Script")
    logger.info("=" * 50)

    try:
        count = add_tuesday_schedule()
        logger.info(f"✅ Successfully added {count} Tuesday schedule entries")
        return 0
    except Exception as e:
        logger.error(f"❌ Failed to add Tuesday schedule: {e}")
        return 1


if __name__ == "__main__":
    exit(main())