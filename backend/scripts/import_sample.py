"""
Import sample data for testing and development
"""

import random
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session

from ..core.database import SessionLocal, create_tables
from ..models.database_models import (
    Student, Schedule, ClassRoster, QuickLog, Assessment,
    Reminder, DutyRota, Communication
)
from ..core.logging_config import get_logger

logger = get_logger("import_sample")


def create_sample_students(db: Session):
    """Create sample students"""
    logger.info("Creating sample students...")
    
    # Sample student data
    first_names = [
        "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
        "Isabella", "William", "Mia", "James", "Charlotte", "Benjamin", "Amelia",
        "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Abigail", "Michael",
        "Emily", "Elijah", "Elizabeth", "Daniel", "Sofia", "Matthew", "Avery",
        "Joseph", "Ella", "David", "Madison", "Samuel", "Scarlett", "Carter"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Wilson", "Anderson", "Taylor",
        "Thomas", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
        "Harris", "Clark", "Lewis", "Robinson", "Walker", "Young", "Allen",
        "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell"
    ]
    
    # Generate students for different classes and year groups
    classes = ["7A", "7B", "8A", "8B", "9A", "9B", "10A", "10B", "11A", "11B"]
    campuses = ["A", "B"]
    
    students = []
    for i in range(120):  # Create 120 students
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        class_code = random.choice(classes)
        year_group = class_code[0]  # First character of class code
        campus = random.choice(campuses)
        
        # Some students need higher support levels
        support_level = 0
        support_notes = None
        if random.random() < 0.15:  # 15% need some support
            support_level = random.randint(1, 2)
            support_notes = random.choice([
                "Needs extra help with reading",
                "Requires additional math support",
                "Benefits from visual learning aids",
                "Needs encouragement to participate",
                "Requires structured environment"
            ])
        elif random.random() < 0.05:  # 5% need high support
            support_level = 3
            support_notes = random.choice([
                "One-on-one support required",
                "Individualized education plan",
                "Regular check-ins needed",
                "Behavioral support plan in place"
            ])
        
        student = Student(
            name=f"{first_name} {last_name}",
            year_group=year_group,
            class_code=class_code,
            campus=campus,
            support_level=support_level,
            support_notes=support_notes,
            house=random.choice(["Red", "Blue", "Green", "Yellow"]) if random.random() < 0.7 else None
        )
        
        students.append(student)
    
    db.add_all(students)
    db.commit()
    logger.info(f"Created {len(students)} students")
    
    return students


def create_sample_schedule(db: Session):
    """Create sample schedule"""
    logger.info("Creating sample schedule...")
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    subjects = [
        "English", "Mathematics", "Science", "History", "Geography",
        "Physical Education", "Art", "Music", "Drama", "ICT",
        "Foreign Language", "Biology", "Chemistry", "Physics"
    ]
    
    rooms = [f"{i}{chr(65+j)}" for i in range(1, 4) for j in range(5)]  # 1A, 1B, 1C, etc.
    
    schedule_entries = []
    for day in days:
        for period in range(1, 7):  # 6 periods per day
            start_time = f"{8 + period - 1:02d}:{30 if period == 1 else '00'}"
            end_time = f"{8 + period:02d}:{15 if period == 1 else '45'}"
            
            # Random class and subject
            class_code = f"{random.choice(['7', '8', '9', '10', '11'])}{random.choice(['A', 'B'])}"
            subject = random.choice(subjects)
            room = random.choice(rooms)
            
            # Check if this entry already exists
            existing = db.query(Schedule).filter(
                Schedule.day_of_week == day,
                Schedule.period == period
            ).first()
            
            if existing:
                continue  # Skip if already exists
            
            entry = Schedule(
                day_of_week=day,
                period=period,
                start_time=start_time,
                end_time=end_time,
                class_code=class_code,
                subject=subject,
                room=room
            )
            
            schedule_entries.append(entry)
    
    db.add_all(schedule_entries)
    db.commit()
    logger.info(f"Created {len(schedule_entries)} schedule entries")
    
    return schedule_entries


def create_sample_class_rosters(db: Session, students):
    """Create class rosters by assigning students to classes"""
    logger.info("Creating class rosters...")
    
    # Get all students grouped by class
    classes = {}
    for student in students:
        if student.class_code not in classes:
            classes[student.class_code] = []
        classes[student.class_code].append(student)
    
    # Create class roster entries
    roster_entries = []
    for class_code, class_students in classes.items():
        for student in class_students:
            roster = ClassRoster(
                class_code=class_code,
                student_id=student.id
            )
            roster_entries.append(roster)
    
    db.add_all(roster_entries)
    db.commit()
    logger.info(f"Created {len(roster_entries)} class roster entries")


def create_sample_quick_logs(db: Session, students):
    """Create sample quick logs"""
    logger.info("Creating sample quick logs...")
    
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
    
    # Create logs for the last 30 days
    logs = []
    for day_offset in range(30):
        log_date = datetime.now() - timedelta(days=day_offset)
        
        # Random number of logs for each day
        num_logs = random.randint(5, 20)
        
        for _ in range(num_logs):
            student = random.choice(students)
            log_type = random.choices(
                ["positive", "negative", "neutral"],
                weights=[0.6, 0.2, 0.2]  # More positive logs
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
            
            log = QuickLog(
                student_id=student.id,
                class_code=student.class_code,
                timestamp=timestamp,
                log_type=log_type,
                category=category,
                points=points,
                note=f"Sample note for {category.replace('_', ' ')}"
            )
            
            logs.append(log)
    
    db.add_all(logs)
    db.commit()
    logger.info(f"Created {len(logs)} quick logs")


def create_sample_assessments(db: Session, students):
    """Create sample assessments"""
    logger.info("Creating sample assessments...")
    
    assessment_types = ["CAT4", "Quizizz", "Formative", "Exam", "Project", "Presentation"]
    subjects = [
        "English", "Mathematics", "Science", "History", "Geography",
        "Physical Education", "Art", "Music", "ICT", "Foreign Language"
    ]
    
    assessments = []
    
    # Create assessments for the last term
    for week_offset in range(12):  # 12 weeks of assessments
        assessment_date = date.today() - timedelta(weeks=week_offset)
        
        # Random number of assessments each week
        num_assessments = random.randint(3, 8)
        
        for _ in range(num_assessments):
            student = random.choice(students)
            assessment_type = random.choice(assessment_types)
            subject = random.choice(subjects)
            
            # Generate realistic scores
            if assessment_type == "CAT4":
                # CAT4 scores are typically between 60-140
                score = random.randint(80, 130)
                max_score = 140
            else:
                # Percentage-based scores
                max_score = 100
                # Students with higher support levels tend to have lower scores
                if student.support_level >= 2:
                    score = random.randint(40, 75)
                else:
                    score = random.randint(55, 95)
            
            percentage = (score / max_score) * 100
            
            assessment = Assessment(
                student_id=student.id,
                assessment_type=assessment_type,
                subject=subject,
                topic=f"Topic {random.randint(1, 5)}",
                score=score,
                max_score=max_score,
                percentage=percentage,
                date=assessment_date,
                source=f"{assessment_type}_{subject}_{assessment_date.isoformat()}"
            )
            
            assessments.append(assessment)
    
    db.add_all(assessments)
    db.commit()
    logger.info(f"Created {len(assessments)} assessments")


def create_sample_reminders(db: Session):
    """Create sample reminders"""
    logger.info("Creating sample reminders...")
    
    reminders = [
        Reminder(
            title="Morning Briefing",
            reminder_type="daily",
            trigger_time="07:30",
            message="Check today's schedule and student alerts"
        ),
        Reminder(
            title="End of Day Review",
            reminder_type="daily",
            trigger_time="15:30",
            message="Review logs and update student notes"
        ),
        Reminder(
            title="Weekly Planning",
            reminder_type="weekly",
            days="Sunday",
            trigger_time="18:00",
            message="Plan lessons and activities for the week"
        ),
        Reminder(
            title="Staff Meeting",
            reminder_type="weekly",
            days="Wednesday",
            trigger_time="15:45",
            message="Prepare updates for department meeting"
        ),
        Reminder(
            title="Report Cards Due",
            reminder_type="once",
            trigger_time="09:00",
            message="Submit Term 2 report cards"
        )
    ]
    
    db.add_all(reminders)
    db.commit()
    logger.info(f"Created {len(reminders)} reminders")


def create_sample_duty_rotas(db: Session):
    """Create sample duty rotas"""
    logger.info("Creating sample duty rotas...")
    
    duty_types = [
        "Gate Supervision", "Morning Duty", "Lunch Duty", 
        "After School Duty", "Assembly Supervision", "CCA Supervision"
    ]
    
    locations = ["Main Gate", "Front Entrance", "Cafeteria", "Playground", "Hall", "Sports Field"]
    
    # Create duties for the next 2 weeks
    duties = []
    for day_offset in range(14):
        duty_date = date.today() + timedelta(days=day_offset)
        
        # Random number of duties each day
        num_duties = random.randint(1, 3)
        
        for _ in range(num_duties):
            duty_type = random.choice(duty_types)
            location = random.choice(locations)
            
            # Random time slots
            time_slots = [
                ("07:30", "08:00"),  # Before school
                ("12:30", "13:30"),  # Lunch
                ("15:00", "15:30")   # After school
            ]
            
            start_time, end_time = random.choice(time_slots)
            
            duty = DutyRota(
                date=duty_date,
                duty_type=duty_type,
                location=location,
                start_time=start_time,
                end_time=end_time,
                notes=f"Please be on time for {duty_type}"
            )
            
            duties.append(duty)
    
    db.add_all(duties)
    db.commit()
    logger.info(f"Created {len(duties)} duty rota entries")


def create_sample_communications(db: Session):
    """Create sample communications"""
    logger.info("Creating sample communications...")
    
    subjects = [
        "Parent-Teacher Meeting Request",
        "Student Progress Update",
        "Upcoming Event Notice",
        "Policy Change Notification",
        "Urgent: Student Absence",
        "Permission Slip Required",
        "Department Meeting Minutes",
        "Curriculum Update"
    ]
    
    senders = [
        "Principal", "Department Head", "School Office", 
        "Parent Portal", "HR Department", "IT Support"
    ]
    
    categories = ["urgent", "calendar", "fyi", "action_required"]
    
    communications = []
    
    # Create communications for the last 2 weeks
    for day_offset in range(14):
        comm_date = datetime.now() - timedelta(days=day_offset)
        
        # Random number of communications each day
        num_comms = random.randint(1, 4)
        
        for _ in range(num_comms):
            subject = random.choice(subjects)
            sender = random.choice(senders)
            category = random.choice(categories)
            campus = random.choice(["A", "B", None])  # None means both campuses
            
            # Make some communications unread
            read = random.random() < 0.7  # 70% are read
            
            communication = Communication(
                source=random.choice(["email", "google_doc", "manual"]),
                campus=campus,
                subject=subject,
                sender=sender,
                content=f"This is a sample communication about {subject.lower()}.",
                category=category,
                received_date=comm_date,
                action_required=category == "action_required",
                read=read
            )
            
            communications.append(communication)
    
    db.add_all(communications)
    db.commit()
    logger.info(f"Created {len(communications)} communications")


def main():
    """Main function to import all sample data"""
    logger.info("Starting sample data import...")
    
    # Create database tables
    create_tables()
    
    db = SessionLocal()
    try:
        # Import all sample data
        students = create_sample_students(db)
        create_sample_schedule(db)
        create_sample_class_rosters(db, students)
        create_sample_quick_logs(db, students)
        create_sample_assessments(db, students)
        create_sample_reminders(db)
        create_sample_duty_rotas(db)
        create_sample_communications(db)
        
        logger.info("Sample data import completed successfully!")
        
    except Exception as e:
        logger.error(f"Error importing sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()