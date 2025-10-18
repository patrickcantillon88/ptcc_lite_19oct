"""
Import student accommodations data from PDF dataset
Run: python -m backend.ingestion.import_accommodations_data
"""

from datetime import date
from backend.core.database import SessionLocal
from backend.models.database_models import Student, StudentAccommodation

# Accommodations data extracted from PDF student profiles
ACCOMMODATIONS_DATA = [
    # 3A - Marcus Thompson
    {
        "student_name": "Marcus Thompson",
        "class_code": "3A",
        "accommodation_type": "behavioral",
        "description": "Impulsivity, attention-seeking, responds well to movement breaks",
        "implementation_details": "Offer movement break at 10:30 & 2:00 (proactive intervention)"
    },
    # 3A - Sophie Chen
    {
        "student_name": "Sophie Chen",
        "class_code": "3A",
        "accommodation_type": "behavioral",
        "description": "Perfectionist, avoids risk-taking, benefits from reassurance",
        "implementation_details": "Reassurance buddy check at 11:00 & 1:30 (anxiety management)"
    },
    # 3A - Liam O'Brien
    {
        "student_name": "Liam O'Brien",
        "class_code": "3A",
        "accommodation_type": "communication",
        "description": "Delayed speech, working with SLT, very social despite difficulties",
        "implementation_details": "1:1 speech/language support; encourage peer interaction"
    },
    # 3A - Zoe Martinez
    {
        "student_name": "Zoe Martinez",
        "class_code": "3A",
        "accommodation_type": "sensory",
        "description": "Noise sensitivity, wears ear defenders in assemblies",
        "implementation_details": "Ear defenders available; low-distraction seating; quiet workspace offered"
    },
    # 3A - James Park
    {
        "student_name": "James Park",
        "class_code": "3A",
        "accommodation_type": "behavioral",
        "description": "Difficulty with transitions, needs advance warning of changes",
        "implementation_details": "Visual schedule at transitions; 5-min warning before changes"
    },
    
    # 4B - Kai Tanaka
    {
        "student_name": "Kai Tanaka",
        "class_code": "4B",
        "accommodation_type": "behavioral",
        "description": "School refusal behavior emerging, working with parents/counselor",
        "implementation_details": "Physical activity (Basketball CCA) helps anxiety; monitor for school refusal signs"
    },
    # 4B - Joshua Finch
    {
        "student_name": "Joshua Finch",
        "class_code": "4B",
        "accommodation_type": "behavioral",
        "description": "Emotional dysregulation, recent family changes, increased incidents",
        "implementation_details": "Morning & afternoon emotional check-in; access to cool-down space; de-escalation strategy"
    },
    # 4B - Natalia Kowalski
    {
        "student_name": "Natalia Kowalski",
        "class_code": "4B",
        "accommodation_type": "social",
        "description": "Withdrawn, difficulty making friends, self-isolating",
        "implementation_details": "Peer buddy assigned; structured peer pairing for group work; teacher-facilitated inclusion"
    },
    # 4B - Ravi Gupta
    {
        "student_name": "Ravi Gupta",
        "class_code": "4B",
        "accommodation_type": "behavioral",
        "description": "Impulsive, risk-taking, boundary-testing with peers and adults",
        "implementation_details": "Proximity to teacher during non-preferred tasks; immediate positive feedback for compliance"
    },
    
    # 5C - Grace Pham
    {
        "student_name": "Grace Pham",
        "class_code": "5C",
        "accommodation_type": "behavioral",
        "description": "Academic pressure anxiety, perfectionism, needs to build resilience around mistakes",
        "implementation_details": "Anxiety/perfectionism support; perspective-building; reassurance around mistakes"
    },
    # 5C - Freya Nielsen
    {
        "student_name": "Freya Nielsen",
        "class_code": "5C",
        "accommodation_type": "sensory",
        "description": "Light sensitivity, uses blue-light filter on screens, prefers dim classroom lighting",
        "implementation_details": "Blue-light filter on all screen devices; low-stimulation seating area available; dim lighting offered"
    },
    # 5C - Mohammed Al-Rashid
    {
        "student_name": "Mohammed Al-Rashid",
        "class_code": "5C",
        "accommodation_type": "behavioral",
        "description": "Recent behavioral escalation, safeguarding concerns flagged",
        "implementation_details": "Key Worker (Ms Fiona Liu) - weekly 1:1 check-ins; assigned key worker for relationship-building"
    },
    # 5C - Ethan Hughes
    {
        "student_name": "Ethan Hughes",
        "class_code": "5C",
        "accommodation_type": "behavioral",
        "description": "ADHD diagnosis, medication compliance sometimes inconsistent, benefits from movement breaks",
        "implementation_details": "Movement break offers at 10:00 & 1:15; fidget tools available; medication monitoring check"
    },
    # 5C - Sofia Delgado
    {
        "student_name": "Sofia Delgado",
        "class_code": "5C",
        "accommodation_type": "social",
        "description": "Friendship difficulties, peer conflict incidents, needs conflict resolution support",
        "implementation_details": "Conflict resolution support; careful peer pairing in group work; teacher mediation"
    },
    
    # 6D - Amal Al-Noor
    {
        "student_name": "Amal Al-Noor",
        "class_code": "6D",
        "accommodation_type": "behavioral",
        "description": "Social anxiety in new situations, transition to secondary causing concern",
        "implementation_details": "Individual check-ins Mon/Wed; transition anxiety exposure plan; gradual secondary environment exposure"
    },
    # 6D - Lars Andersen
    {
        "student_name": "Lars Andersen",
        "class_code": "6D",
        "accommodation_type": "sensory",
        "description": "Auditory processing issues, benefits from visual supports",
        "implementation_details": "Visual supports for instructions; one-to-one instructions offered; minimize auditory overload"
    },
    # 6D - Cairo Lopez
    {
        "student_name": "Cairo Lopez",
        "class_code": "6D",
        "accommodation_type": "behavioral",
        "description": "Peer relationship difficulties, occasional physical aggression under stress",
        "implementation_details": "Frustration de-escalation strategies; conflict resolution practiced; proximity to adults during frustration"
    },
    # 6D - Priya Verma
    {
        "student_name": "Priya Verma",
        "class_code": "6D",
        "accommodation_type": "behavioral",
        "description": "Anxiety about secondary transition, perfectionism affecting enjoyment",
        "implementation_details": "Transition support + reassurance; reframe perfectionism; group anxiety management"
    },
    # 6D - Sienna Brown
    {
        "student_name": "Sienna Brown",
        "class_code": "6D",
        "accommodation_type": "behavioral",
        "description": "Disengagement in core subjects, home instability being monitored",
        "implementation_details": "Daily check-in with Ms Rebecca (emotional support); no academic pressure; flexible approach"
    },
]

def import_accommodations():
    """Import accommodations data"""
    db = SessionLocal()
    try:
        # Clear existing accommodations
        db.query(StudentAccommodation).delete()
        db.commit()
        
        imported_count = 0
        skipped_count = 0
        
        # Import new accommodations
        for accom_data in ACCOMMODATIONS_DATA:
            student_name = accom_data.pop("student_name")
            class_code = accom_data.pop("class_code")
            
            # Find student
            student = db.query(Student).filter(
                Student.name == student_name,
                Student.class_code == class_code
            ).first()
            
            if student:
                accommodation = StudentAccommodation(
                    student_id=student.id,
                    effective_date=date.today(),
                    **accom_data
                )
                db.add(accommodation)
                imported_count += 1
            else:
                print(f"⚠️ Student not found: {student_name} ({class_code})")
                skipped_count += 1
        
        db.commit()
        print(f"✅ Imported {imported_count} accommodations ({skipped_count} skipped due to student not found)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error importing accommodations: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_accommodations()
