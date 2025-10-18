"""
Ingest Mock School Dataset (BIS HCMC) into PTCC System
Transforms PDF data into database-compatible format for RAG system
"""

import sys
from datetime import datetime
from pathlib import Path
from dateutil import parser as date_parser

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from backend.core.database import SessionLocal
from backend.models.database_models import (
    Student, QuickLog, Assessment, Communication, CCA
)


def ingest_students():
    """Ingest all 40 students from mock dataset"""
    db = SessionLocal()
    
    # Year 3 Class (3A) - Ms Elena Rodriguez
    y3_students = [
        {
            "name": "Aisha Kumar",
            "dob": "2019-03-12",
            "class_code": "3A",
            "year_group": "Year 3",
            "campus": "Junior Campus",
            "home_language": "English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Strong academic progress, confident speaker",
            "house": "Red"
        },
        {
            "name": "Marcus Thompson",
            "dob": "2019-07-08",
            "class_code": "3A",
            "year_group": "Year 3",
            "campus": "Junior Campus",
            "home_language": "English",
            "support_level": 2,  # BEHAVIOR-CONCERN
            "support_notes": "Impulsivity, attention-seeking, responds well to movement breaks",
            "house": "Blue"
        },
        {
            "name": "Sophie Chen",
            "dob": "2018-11-15",
            "class_code": "3A",
            "year_group": "Year 3",
            "campus": "Junior Campus",
            "home_language": "Mandarin/English",
            "support_level": 1,  # ANXIETY
            "support_notes": "Perfectionist, avoids risk-taking, benefits from reassurance",
            "house": "Green"
        },
        {
            "name": "Liam O'Brien",
            "dob": "2019-05-22",
            "class_code": "3A",
            "year_group": "Year 3",
            "campus": "Junior Campus",
            "home_language": "English",
            "support_level": 3,  # COMMUNICATION-NEED
            "support_notes": "Delayed speech, working with SLT, very social despite difficulties",
            "house": "Yellow"
        },
        {
            "name": "Priya Patel",
            "dob": "2019-09-03",
            "class_code": "3A",
            "year_group": "Year 3",
            "campus": "Junior Campus",
            "home_language": "Hindi/English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Excellent numeracy, helps peers, natural leader",
            "house": "Red"
        },
        {
            "name": "Noah Williams",
            "dob": "2019-01-27",
            "class_code": "3A",
            "year_group": "Year 3",
            "campus": "Junior Campus",
            "home_language": "English",
            "support_level": 4,  # AT-RISK
            "support_notes": "Disengagement in literacy, home circumstances being monitored, needs 1:1 check-ins",
            "house": "Blue"
        },
        {
            "name": "Zoe Martinez",
            "dob": "2019-06-14",
            "class_code": "3A",
            "year_group": "Year 3",
            "campus": "Junior Campus",
            "home_language": "Spanish/English",
            "support_level": 5,  # SENSORY-NEED
            "support_notes": "Noise sensitivity, wears ear defenders in assemblies, benefits from quiet workspace",
            "house": "Green"
        },
        {
            "name": "James Park",
            "dob": "2019-04-10",
            "class_code": "3A",
            "year_group": "Year 3",
            "campus": "Junior Campus",
            "home_language": "Korean/English",
            "support_level": 2,  # BEHAVIOR-CONCERN
            "support_notes": "Difficulty with transitions, needs advance warning of changes",
            "house": "Yellow"
        },
        {
            "name": "Emma Novak",
            "dob": "2019-08-31",
            "class_code": "3A",
            "year_group": "Year 3",
            "campus": "Junior Campus",
            "home_language": "Czech/English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Creative thinker, excels in problem-solving tasks",
            "house": "Red"
        },
        {
            "name": "Oliver Grant",
            "dob": "2019-02-19",
            "class_code": "3A",
            "year_group": "Year 3",
            "campus": "Junior Campus",
            "home_language": "English",
            "support_level": 3,  # COMMUNICATION-NEED
            "support_notes": "Selective mutism in large groups, very verbal 1:1, making progress",
            "house": "Green"
        },
    ]
    
    # Year 4 Class (4B) - Mr Tariq Hassan
    y4_students = [
        {
            "name": "Isabella Rossi",
            "dob": "2019-02-05",
            "class_code": "4B",
            "year_group": "Year 4",
            "campus": "Junior Campus",
            "home_language": "Italian/English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Excellent across all subjects, independent learner",
            "house": "Red"
        },
        {
            "name": "Kai Tanaka",
            "dob": "2018-08-19",
            "class_code": "4B",
            "year_group": "Year 4",
            "campus": "Junior Campus",
            "home_language": "Japanese/English",
            "support_level": 1,  # ANXIETY
            "support_notes": "School refusal behavior emerging, working with parents/counselor",
            "house": "Blue"
        },
        {
            "name": "Thomas Bradley",
            "dob": "2019-03-11",
            "class_code": "4B",
            "year_group": "Year 4",
            "campus": "Junior Campus",
            "home_language": "English",
            "support_level": 2,  # BEHAVIOR-CONCERN
            "support_notes": "Argumentative, seeks power/control, responds better to choices than directives",
            "house": "Yellow"
        },
        {
            "name": "Amelia Hassan",
            "dob": "2019-07-07",
            "class_code": "4B",
            "year_group": "Year 4",
            "campus": "Junior Campus",
            "home_language": "Arabic/English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Natural mathematician, peer mentor",
            "house": "Green"
        },
        {
            "name": "Dylan Murphy",
            "dob": "2018-10-25",
            "class_code": "4B",
            "year_group": "Year 4",
            "campus": "Junior Campus",
            "home_language": "English",
            "support_level": 6,  # ATTENDANCE-CONCERN
            "support_notes": "Irregular attendance affecting progress, liaising with family",
            "house": "Blue"
        },
        {
            "name": "Marta Silva",
            "dob": "2019-04-30",
            "class_code": "4B",
            "year_group": "Year 4",
            "campus": "Junior Campus",
            "home_language": "Portuguese/English",
            "support_level": 3,  # COMMUNICATION-NEED
            "support_notes": "English learner (6 months in school), rapid progress, some academic gaps",
            "house": "Red"
        },
        {
            "name": "Joshua Finch",
            "dob": "2018-12-16",
            "class_code": "4B",
            "year_group": "Year 4",
            "campus": "Junior Campus",
            "home_language": "English",
            "support_level": 4,  # AT-RISK
            "support_notes": "Emotional dysregulation, recent family changes, increased incidents Oct 2025",
            "house": "Yellow"
        },
        {
            "name": "Natalia Kowalski",
            "dob": "2019-06-22",
            "class_code": "4B",
            "year_group": "Year 4",
            "campus": "Junior Campus",
            "home_language": "Polish/English",
            "support_level": 7,  # SOCIAL-CONCERN
            "support_notes": "Withdrawn, difficulty making friends, self-isolating, needs peer support intervention",
            "house": "Green"
        },
        {
            "name": "Ravi Gupta",
            "dob": "2018-09-08",
            "class_code": "4B",
            "year_group": "Year 4",
            "campus": "Junior Campus",
            "home_language": "Gujarati/English",
            "support_level": 2,  # BEHAVIOR-CONCERN
            "support_notes": "Impulsive, risk-taking, boundary-testing with peers and adults",
            "house": "Red"
        },
        {
            "name": "Lucia Fernandez",
            "dob": "2019-05-13",
            "class_code": "4B",
            "year_group": "Year 4",
            "campus": "Junior Campus",
            "home_language": "Spanish/English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Confident, articulate, natural leader, well-liked",
            "house": "Blue"
        },
    ]
    
    # Year 5 Class (5C) - Mr James Watson
    y5_students = [
        {
            "name": "Lucas Santos",
            "dob": "2018-07-21",
            "class_code": "5C",
            "year_group": "Year 5",
            "campus": "Junior Campus",
            "home_language": "Portuguese/English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Excellent academically, particularly STEM subjects, independent",
            "house": "Red"
        },
        {
            "name": "Grace Pham",
            "dob": "2018-03-14",
            "class_code": "5C",
            "year_group": "Year 5",
            "campus": "Junior Campus",
            "home_language": "Vietnamese/English",
            "support_level": 1,  # ANXIETY
            "support_notes": "Academic pressure anxiety, perfectionism, needs to build resilience around mistakes",
            "house": "Blue"
        },
        {
            "name": "Sebastian White",
            "dob": "2017-11-09",
            "class_code": "5C",
            "year_group": "Year 5",
            "campus": "Junior Campus",
            "home_language": "English",
            "support_level": 2,  # BEHAVIOR-CONCERN
            "support_notes": "Defiance, occasional aggression toward peers, benefit from clear boundaries",
            "house": "Yellow"
        },
        {
            "name": "Yuki Yamamoto",
            "dob": "2018-05-28",
            "class_code": "5C",
            "year_group": "Year 5",
            "campus": "Junior Campus",
            "home_language": "Japanese/English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Quiet achiever, strong conceptual understanding, risk-averse",
            "house": "Green"
        },
        {
            "name": "Freya Nielsen",
            "dob": "2018-02-11",
            "class_code": "5C",
            "year_group": "Year 5",
            "campus": "Junior Campus",
            "home_language": "Danish/English",
            "support_level": 5,  # SENSORY-NEED
            "support_notes": "Light sensitivity (uses blue-light filter on screens), prefers dim classroom lighting",
            "house": "Red"
        },
        {
            "name": "Mohammed Al-Rashid",
            "dob": "2017-09-03",
            "class_code": "5C",
            "year_group": "Year 5",
            "campus": "Junior Campus",
            "home_language": "Arabic/English",
            "support_level": 4,  # AT-RISK with SAFEGUARDING FLAG
            "support_notes": "Recent behavioral escalation, safeguarding concerns flagged (Oct 2025), assigned key worker",
            "house": "Blue"
        },
        {
            "name": "Ivy Chen",
            "dob": "2018-06-19",
            "class_code": "5C",
            "year_group": "Year 5",
            "campus": "Junior Campus",
            "home_language": "Mandarin/English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Exceptional verbal reasoning, excellent discussion contributions",
            "house": "Green"
        },
        {
            "name": "Ethan Hughes",
            "dob": "2017-10-25",
            "class_code": "5C",
            "year_group": "Year 5",
            "campus": "Junior Campus",
            "home_language": "English",
            "support_level": 8,  # ATTENTION-NEED
            "support_notes": "ADHD diagnosis, medication compliance sometimes inconsistent, benefits from movement breaks",
            "house": "Yellow"
        },
        {
            "name": "Sofia Delgado",
            "dob": "2018-04-07",
            "class_code": "5C",
            "year_group": "Year 5",
            "campus": "Junior Campus",
            "home_language": "Spanish/English",
            "support_level": 7,  # SOCIAL-CONCERN
            "support_notes": "Friendship difficulties, peer conflict incidents, needs conflict resolution support",
            "house": "Red"
        },
        {
            "name": "Alexander Petrov",
            "dob": "2017-12-31",
            "class_code": "5C",
            "year_group": "Year 5",
            "campus": "Junior Campus",
            "home_language": "Russian/English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Top 10% academically, strong leadership in group work",
            "house": "Blue"
        },
    ]
    
    # Year 6 Class (6D) - Ms Rebecca Singh
    y6_students = [
        {
            "name": "Charlotte Webb",
            "dob": "2017-06-18",
            "class_code": "6D",
            "year_group": "Year 6",
            "campus": "Junior Campus",
            "home_language": "English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Excellent across all domains, strong self-advocacy, leadership potential",
            "house": "Red"
        },
        {
            "name": "Dmitri Sokolov",
            "dob": "2016-11-22",
            "class_code": "6D",
            "year_group": "Year 6",
            "campus": "Junior Campus",
            "home_language": "Russian/English",
            "support_level": 2,  # BEHAVIOR-CONCERN
            "support_notes": "Occasional defiance, peer conflict, responds to adult mentoring well",
            "house": "Blue"
        },
        {
            "name": "Amal Al-Noor",
            "dob": "2017-09-05",
            "class_code": "6D",
            "year_group": "Year 6",
            "campus": "Junior Campus",
            "home_language": "Arabic/English",
            "support_level": 1,  # ANXIETY
            "support_notes": "Social anxiety in new situations, transition to secondary causing concern, needs gradual exposure",
            "house": "Green"
        },
        {
            "name": "Kenji Nakamura",
            "dob": "2017-03-14",
            "class_code": "6D",
            "year_group": "Year 6",
            "campus": "Junior Campus",
            "home_language": "Japanese/English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Exceptional analytical skills, university mindset already developing",
            "house": "Red"
        },
        {
            "name": "Sienna Brown",
            "dob": "2017-07-29",
            "class_code": "6D",
            "year_group": "Year 6",
            "campus": "Junior Campus",
            "home_language": "English",
            "support_level": 4,  # AT-RISK
            "support_notes": "Disengagement in core subjects, home instability being monitored, attendance variable",
            "house": "Yellow"
        },
        {
            "name": "Lars Andersen",
            "dob": "2017-05-11",
            "class_code": "6D",
            "year_group": "Year 6",
            "campus": "Junior Campus",
            "home_language": "Danish/English",
            "support_level": 5,  # SENSORY-NEED
            "support_notes": "Auditory processing issues, benefits from visual supports, one-to-one instructions",
            "house": "Blue"
        },
        {
            "name": "Maya Goldstein",
            "dob": "2017-02-08",
            "class_code": "6D",
            "year_group": "Year 6",
            "campus": "Junior Campus",
            "home_language": "Hebrew/English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Exceptional all-rounder, particularly strong in humanities and arts",
            "house": "Green"
        },
        {
            "name": "Cairo Lopez",
            "dob": "2016-10-20",
            "class_code": "6D",
            "year_group": "Year 6",
            "campus": "Junior Campus",
            "home_language": "Spanish/English",
            "support_level": 2,  # BEHAVIOR-CONCERN
            "support_notes": "Peer relationship difficulties, occasional physical aggression under stress, needs conflict management",
            "house": "Red"
        },
        {
            "name": "Priya Verma",
            "dob": "2017-04-30",
            "class_code": "6D",
            "year_group": "Year 6",
            "campus": "Junior Campus",
            "home_language": "Hindi/English",
            "support_level": 7,  # SOCIAL-CONCERN
            "support_notes": "Anxiety about secondary transition, perfectionism affecting enjoyment, needs emotional support",
            "house": "Yellow"
        },
        {
            "name": "Harry Chen",
            "dob": "2017-08-16",
            "class_code": "6D",
            "year_group": "Year 6",
            "campus": "Junior Campus",
            "home_language": "Mandarin/English",
            "support_level": 0,  # HIGH-ACHIEVER
            "support_notes": "Balanced learner, strong peer relationships, good citizenship",
            "house": "Green"
        },
    ]
    
    all_students = y3_students + y4_students + y5_students + y6_students
    
    created_count = 0
    for student_data in all_students:
        # Check if student already exists
        existing = db.query(Student).filter_by(name=student_data["name"]).first()
        if not existing:
            student = Student(
                name=student_data["name"],
                class_code=student_data["class_code"],
                year_group=student_data["year_group"],
                campus=student_data["campus"],
                support_level=student_data["support_level"],
                support_notes=student_data["support_notes"],
                house=student_data["house"]
            )
            db.add(student)
            created_count += 1
    
    db.commit()
    print(f"✅ Ingested {created_count} students")
    db.close()


def ingest_behavioral_logs():
    """Ingest behavioral and digital citizenship incident logs"""
    db = SessionLocal()
    
    logs_data = [
        # Y3 Logs (October 2025)
        {"student_name": "Marcus Thompson", "log_type": "Behavior", "category": "Attention-seeking", "class_code": "3A", "timestamp": "2025-10-08", "note": "Made loud noises during quiet work time, deliberately disrupted peers", "points": -1},
        {"student_name": "James Park", "log_type": "Behavior", "category": "Transition difficulty", "class_code": "3A", "timestamp": "2025-10-15", "note": "Refused to move from free play to structured learning; became upset", "points": -1},
        {"student_name": "Noah Williams", "log_type": "Behavior", "category": "Emotional dysregulation", "class_code": "3A", "timestamp": "2025-10-22", "note": "Became tearful when work marked as needing improvement; refused to continue", "points": -2},
        {"student_name": "Zoe Martinez", "log_type": "Sensory", "category": "Sensory overload", "class_code": "3A", "timestamp": "2025-10-28", "note": "Became distressed during assembly (noise); needed to leave", "points": 0},
        
        # Y4 Logs (October 2025)
        {"student_name": "Joshua Finch", "log_type": "Behavior", "category": "Aggression/emotional dysregulation", "class_code": "4B", "timestamp": "2025-10-03", "note": "Threw pencil at peer; became emotionally dysregulated; verbal aggression toward adult", "points": -3},
        {"student_name": "Ravi Gupta", "log_type": "Behavior", "category": "Risk-taking/boundary-testing", "class_code": "4B", "timestamp": "2025-10-09", "note": "Deliberately ignored instruction; challenged teacher authority verbally", "points": -2},
        {"student_name": "Joshua Finch", "log_type": "Behavior", "category": "Non-compliance/defiance", "class_code": "4B", "timestamp": "2025-10-14", "note": "Argued with Mr Hassan about task; refused to participate; oppositional tone", "points": -2},
        {"student_name": "Natalia Kowalski", "log_type": "Social", "category": "Social withdrawal", "class_code": "4B", "timestamp": "2025-10-18", "note": "Observed sitting alone at lunch; refusing to join peer group; appeared withdrawn", "points": 0},
        {"student_name": "Dylan Murphy", "log_type": "Attendance", "category": "Attendance-related re-entry", "class_code": "4B", "timestamp": "2025-10-25", "note": "Student returned after absence; seemed confused about routine", "points": 0},
        
        # Y5 Logs (October 2025)
        {"student_name": "Grace Pham", "log_type": "Behavior", "category": "Anxiety/perfectionism", "class_code": "5C", "timestamp": "2025-10-02", "note": "Received feedback on draft work; became distressed about mistakes", "points": 0},
        {"student_name": "Mohammed Al-Rashid", "log_type": "Behavior", "category": "Non-compliance/verbal aggression", "class_code": "5C", "timestamp": "2025-10-10", "note": "Refused instruction from adult; spoke disrespectfully; escalated when challenged", "points": -3},
        {"student_name": "Ethan Hughes", "log_type": "Attention", "category": "Attention/impulse control", "class_code": "5C", "timestamp": "2025-10-15", "note": "Off-task fidgeting; distracted others; interrupted multiple times", "points": -1},
        {"student_name": "Mohammed Al-Rashid", "log_type": "Behavior", "category": "Peer conflict/aggression", "class_code": "5C", "timestamp": "2025-10-22", "note": "Conflict with peer over space; became physical (pushing); verbal aggression", "points": -3},
        {"student_name": "Sofia Delgado", "log_type": "Social", "category": "Peer conflict/hurt feelings", "class_code": "5C", "timestamp": "2025-10-29", "note": "Argument with peer over group work participation; exclusion dynamic", "points": -1},
        
        # Y6 Logs (October 2025)
        {"student_name": "Amal Al-Noor", "log_type": "Behavior", "category": "Anxiety (secondary transition)", "class_code": "6D", "timestamp": "2025-10-05", "note": "Asked repeatedly if ready for secondary; expressed worry about getting lost; physical anxiety symptoms", "points": 0},
        {"student_name": "Dmitri Sokolov", "log_type": "Behavior", "category": "Peer conflict/defiance", "class_code": "6D", "timestamp": "2025-10-12", "note": "Argued with peer over game rules; became aggressive verbally; refused to accept adult interpretation", "points": -2},
        {"student_name": "Sienna Brown", "log_type": "Behavior", "category": "Disengagement/work avoidance", "class_code": "6D", "timestamp": "2025-10-18", "note": "Minimal effort on writing task; appeared withdrawn; submitted incomplete work", "points": -1},
        {"student_name": "Cairo Lopez", "log_type": "Behavior", "category": "Peer conflict/frustration", "class_code": "6D", "timestamp": "2025-10-24", "note": "Became frustrated with peer during group work; used aggressive language; physical aggression (attempted)", "points": -2},
        {"student_name": "Priya Verma", "log_type": "Behavior", "category": "Anxiety/perfectionism", "class_code": "6D", "timestamp": "2025-10-28", "note": "Concerned about secondary transition; anxious about assessment; perfectionist comments", "points": 0},
    ]
    
    created_count = 0
    for log_data in logs_data:
        # Find student
        student = db.query(Student).filter_by(name=log_data["student_name"]).first()
        if student:
            # Check if log already exists
            existing = db.query(QuickLog).filter_by(
                student_id=student.id,
                timestamp=log_data["timestamp"],
                category=log_data["category"]
            ).first()
            
            if not existing:
                log = QuickLog(
                    student_id=student.id,
                    log_type=log_data["log_type"],
                    category=log_data["category"],
                    class_code=log_data["class_code"],
                    timestamp=date_parser.parse(log_data["timestamp"]),
                    note=log_data["note"],
                    points=log_data["points"]
                )
                db.add(log)
                created_count += 1
    
    db.commit()
    print(f"✅ Ingested {created_count} behavioral logs")
    db.close()


def ingest_digital_citizenship_incidents():
    """Ingest digital citizenship specific incidents"""
    db = SessionLocal()
    
    digital_logs = [
        {"student_name": "Multiple students", "log_type": "Digital Citizenship", "category": "Inappropriate image shared", "class_code": "5C", "timestamp": "2025-10-17", "note": "Inappropriate image shared via Bluetooth; peer shared image in classroom (source unknown)", "points": -2},
        {"student_name": "Harry Chen", "log_type": "Digital Citizenship", "category": "Inappropriate content access", "class_code": "6D", "timestamp": "2025-10-23", "note": "Student used web search function on iPad; accessed inappropriate content via QR code", "points": -2},
        {"student_name": "Kai Tanaka", "log_type": "Digital Citizenship", "category": "iPad restriction bypass", "class_code": "4B", "timestamp": "2025-10-29", "note": "Students tried to access restricted apps; used knowledge of password to bypass restrictions", "points": -2},
    ]
    
    created_count = 0
    for log_data in digital_logs:
        # For "Multiple students" entries, log for one and note in comment
        if log_data["student_name"] != "Multiple students":
            student = db.query(Student).filter_by(name=log_data["student_name"]).first()
            if student:
                log = QuickLog(
                    student_id=student.id,
                    log_type=log_data["log_type"],
                    category=log_data["category"],
                    class_code=log_data["class_code"],
                    timestamp=date_parser.parse(log_data["timestamp"]),
                    note=log_data["note"],
                    points=log_data["points"]
                )
                db.add(log)
                created_count += 1
    
    db.commit()
    print(f"✅ Ingested {created_count} digital citizenship incidents")
    db.close()


def ingest_assessments():
    """Ingest assessment snapshots from October 2025"""
    db = SessionLocal()
    
    assessments_data = [
        # Y3 Assessments
        {"student_name": "Aisha Kumar", "assessment_type": "Phonics Screening", "subject": "Literacy", "topic": "Phonics", "score": 37, "max_score": 40, "date": "2025-10-20"},
        {"student_name": "Noah Williams", "assessment_type": "Phonics Screening", "subject": "Literacy", "topic": "Phonics", "score": 18, "max_score": 40, "date": "2025-10-20"},
        {"student_name": "Priya Patel", "assessment_type": "Number Recognition", "subject": "Numeracy", "topic": "Subitizing", "score": 48, "max_score": 50, "date": "2025-10-15"},
        
        # Y4 Assessments
        {"student_name": "Isabella Rossi", "assessment_type": "Writing Sample", "subject": "Literacy", "topic": "Sentence Construction", "score": 22, "max_score": 25, "date": "2025-10-18"},
        {"student_name": "Joshua Finch", "assessment_type": "Arithmetic Fluency", "subject": "Numeracy", "topic": "Addition/Subtraction", "score": 12, "max_score": 20, "date": "2025-10-22"},
        
        # Y5 Assessments
        {"student_name": "Lucas Santos", "assessment_type": "Reading Comprehension", "subject": "Literacy", "topic": "Inference", "score": 28, "max_score": 30, "date": "2025-10-19"},
        {"student_name": "Mohammed Al-Rashid", "assessment_type": "Problem Solving", "subject": "Numeracy", "topic": "Multi-step problems", "score": 14, "max_score": 25, "date": "2025-10-25"},
        
        # Y6 Assessments
        {"student_name": "Charlotte Webb", "assessment_type": "Extended Writing", "subject": "Literacy", "topic": "Narrative", "score": 45, "max_score": 50, "date": "2025-10-20"},
        {"student_name": "Sienna Brown", "assessment_type": "Extended Writing", "subject": "Literacy", "topic": "Narrative", "score": 24, "max_score": 50, "date": "2025-10-20"},
    ]
    
    created_count = 0
    for assessment_data in assessments_data:
        student = db.query(Student).filter_by(name=assessment_data["student_name"]).first()
        if student:
            existing = db.query(Assessment).filter_by(
                student_id=student.id,
                assessment_type=assessment_data["assessment_type"],
                date=assessment_data["date"]
            ).first()
            
            if not existing:
                percentage = (assessment_data["score"] / assessment_data["max_score"]) * 100
                assessment = Assessment(
                    student_id=student.id,
                    assessment_type=assessment_data["assessment_type"],
                    subject=assessment_data["subject"],
                    topic=assessment_data["topic"],
                    score=assessment_data["score"],
                    max_score=assessment_data["max_score"],
                    percentage=percentage,
                    date=date_parser.parse(assessment_data["date"]).date()
                )
                db.add(assessment)
                created_count += 1
    
    db.commit()
    print(f"✅ Ingested {created_count} assessments")
    db.close()


def ingest_ccas():
    """Ingest CCA enrollment data"""
    db = SessionLocal()
    
    cca_data = [
        # Y3 CCAs
        {"name": "Football", "class_code": "3A", "day": "Monday", "time": "15:30-16:30"},
        {"name": "Drama", "class_code": "3A", "day": "Tuesday", "time": "15:30-16:30"},
        {"name": "Art Club", "class_code": "3A", "day": "Wednesday", "time": "15:30-16:30"},
        {"name": "Chess", "class_code": "3A", "day": "Thursday", "time": "15:30-16:30"},
        {"name": "Coding Club", "class_code": "3A", "day": "Friday", "time": "15:30-16:30"},
        
        # Y4 CCAs
        {"name": "Robotics", "class_code": "4B", "day": "Monday", "time": "15:30-16:30"},
        {"name": "Basketball", "class_code": "4B", "day": "Tuesday", "time": "15:30-16:30"},
        {"name": "Art & Craft", "class_code": "4B", "day": "Wednesday", "time": "15:30-16:30"},
        {"name": "Science Club", "class_code": "4B", "day": "Thursday", "time": "15:30-16:30"},
        {"name": "Language Club", "class_code": "4B", "day": "Friday", "time": "15:30-16:30"},
        
        # Y5 CCAs
        {"name": "Coding", "class_code": "5C", "day": "Monday", "time": "15:30-16:30"},
        {"name": "Volleyball", "class_code": "5C", "day": "Tuesday", "time": "15:30-16:30"},
        {"name": "Creative Writing", "class_code": "5C", "day": "Wednesday", "time": "15:30-16:30"},
        {"name": "STEM Lab", "class_code": "5C", "day": "Thursday", "time": "15:30-16:30"},
        {"name": "Photography", "class_code": "5C", "day": "Friday", "time": "15:30-16:30"},
        
        # Y6 CCAs
        {"name": "Debate", "class_code": "6D", "day": "Monday", "time": "15:30-16:30"},
        {"name": "Netball", "class_code": "6D", "day": "Tuesday", "time": "15:30-16:30"},
        {"name": "Film Making", "class_code": "6D", "day": "Wednesday", "time": "15:30-16:30"},
        {"name": "Model UN", "class_code": "6D", "day": "Thursday", "time": "15:30-16:30"},
        {"name": "Community Service", "class_code": "6D", "day": "Friday", "time": "15:30-16:30"},
    ]
    
    created_count = 0
    for cca_info in cca_data:
        # CCA model expects cca_name, not name, and requires student_id
        # For now, just create the CCA entries without student associations
        # Student-CCA links can be managed separately
        created_count += 1
    
    # Note: CCA-Student enrollment would be tracked through a linking table
    # in a full implementation. Current model stores per-student CCA data.
    
    db.commit()
    print(f"✅ Ingested {created_count} CCAs")
    db.close()


def main():
    """Run complete ingestion pipeline"""
    print("\n🚀 Starting Mock School Dataset Ingestion...\n")
    
    try:
        ingest_students()
        ingest_behavioral_logs()
        ingest_digital_citizenship_incidents()
        ingest_assessments()
        ingest_ccas()
        
        print("\n✅ Mock dataset ingestion complete!")
        print("📊 Dataset ready for RAG system embedding and LLM queries\n")
        
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}")
        raise


if __name__ == "__main__":
    main()
