"""
Enhance Behavioral Logs for BIS HCMC Briefing System

This script ensures behavioral logs are properly categorized and recent enough
for the briefing alerts system to generate meaningful student alerts.
"""

import sys
import os
from datetime import datetime, timedelta
# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal, create_tables
from backend.models.database_models import QuickLog, Student
from backend.core.logging_config import get_logger

logger = get_logger("enhance_behavioral_logs")


def enhance_behavioral_logs():
    """Enhance behavioral logs with recent, categorized data for briefing alerts"""
    logger.info("Starting behavioral logs enhancement...")

    db = SessionLocal()
    try:
        # Get all students
        students = db.query(Student).all()
        logger.info(f"Found {len(students)} students")

        # Create recent behavioral logs (last 7 days) to ensure briefing has alerts
        recent_logs = []
        base_date = datetime.now()

        # Categories for different types of behavior
        positive_categories = [
            "excellent_contribution", "helpful_behavior", "creative_thinking",
            "leadership", "perseverance", "teamwork", "curiosity", "initiative"
        ]

        negative_categories = [
            "off_task", "disruptive", "incomplete_work", "late_assignment",
            "poor_effort", "unprepared", "distracting_others", "talking_out_of_turn"
        ]

        neutral_categories = [
            "present", "participated", "asked_question", "completed_work",
            "attended_tutorial", "used_resources", "worked_independently"
        ]

        # Create logs for the last 7 days
        for day_offset in range(7):
            log_date = base_date - timedelta(days=day_offset)

            # Create 2-4 logs per day per class
            for student in students:
                # Skip some students randomly to create variety
                import random
                if random.random() < 0.6:  # 60% of students get logs
                    continue

                num_logs = random.randint(1, 3)

                for _ in range(num_logs):
                    # Determine log type with weighted distribution
                    log_type = random.choices(
                        ["positive", "negative", "neutral"],
                        weights=[0.5, 0.3, 0.2]  # More positive and negative for alerts
                    )[0]

                    if log_type == "positive":
                        category = random.choice(positive_categories)
                        points = random.randint(1, 3)
                    elif log_type == "negative":
                        category = random.choice(negative_categories)
                        points = random.randint(-3, -1)
                    else:
                        category = random.choice(neutral_categories)
                        points = 0

                    # Random time during school hours
                    hour = random.randint(8, 15)
                    minute = random.choice([0, 15, 30, 45])
                    timestamp = log_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

                    # Check if this log already exists (avoid duplicates)
                    existing = db.query(QuickLog).filter(
                        QuickLog.student_id == student.id,
                        QuickLog.timestamp == timestamp,
                        QuickLog.category == category
                    ).first()

                    if not existing:
                        log = QuickLog(
                            student_id=student.id,
                            class_code=student.class_code,
                            timestamp=timestamp,
                            log_type=log_type,
                            category=category,
                            points=points,
                            note=f"Recent {category.replace('_', ' ')} observation"
                        )
                        recent_logs.append(log)

        # Insert the new logs
        if recent_logs:
            db.add_all(recent_logs)
            db.commit()
            logger.info(f"Successfully added {len(recent_logs)} recent behavioral logs")

            # Log summary by type
            positive_count = len([l for l in recent_logs if l.log_type == "positive"])
            negative_count = len([l for l in recent_logs if l.log_type == "negative"])
            neutral_count = len([l for l in recent_logs if l.log_type == "neutral"])

            logger.info(f"Log distribution: {positive_count} positive, {negative_count} negative, {neutral_count} neutral")

        else:
            logger.info("No new behavioral logs to add")

        # Ensure we have some high-frequency negative logs for alert testing
        # Create concentrated negative logs for a few students to trigger alerts
        alert_students = students[:3]  # First 3 students

        alert_logs = []
        for student in alert_students:
            # Add 3-5 negative logs in the last 3 days for these students
            for day_offset in range(3):
                log_date = base_date - timedelta(days=day_offset)

                for i in range(random.randint(3, 5)):
                    hour = random.randint(8, 15)
                    minute = random.choice([0, 15, 30, 45])
                    timestamp = log_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

                    category = random.choice(negative_categories)
                    points = random.randint(-3, -1)

                    # Check for existing
                    existing = db.query(QuickLog).filter(
                        QuickLog.student_id == student.id,
                        QuickLog.timestamp == timestamp,
                        QuickLog.category == category
                    ).first()

                    if not existing:
                        log = QuickLog(
                            student_id=student.id,
                            class_code=student.class_code,
                            timestamp=timestamp,
                            log_type="negative",
                            category=category,
                            points=points,
                            note=f"Alert-triggering {category.replace('_', ' ')} incident"
                        )
                        alert_logs.append(log)

        if alert_logs:
            db.add_all(alert_logs)
            db.commit()
            logger.info(f"Added {len(alert_logs)} concentrated negative logs for alert testing")

        return len(recent_logs) + len(alert_logs)

    except Exception as e:
        logger.error(f"Error enhancing behavioral logs: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function"""
    logger.info("BIS HCMC Behavioral Logs Enhancement Script")
    logger.info("=" * 50)

    try:
        count = enhance_behavioral_logs()
        logger.info(f"✅ Successfully enhanced behavioral logs with {count} entries")
        return 0
    except Exception as e:
        logger.error(f"❌ Failed to enhance behavioral logs: {e}")
        return 1


if __name__ == "__main__":
    exit(main())