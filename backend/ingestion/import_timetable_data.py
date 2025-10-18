"""
Import timetable data from PDF dataset into Timetable table
Run: python -m backend.ingestion.import_timetable_data
"""

from backend.core.database import SessionLocal
from backend.models.database_models import Timetable

# Timetable data extracted from PDF (Y3-Y6 timetables)
TIMETABLE_DATA = [
    # Y3 CLASS (3A) - Monday
    {"class_code": "3A", "day_of_week": "Monday", "period": 1, "start_time": "8:30", "end_time": "9:00", "subject": "Arrival & Transitions", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Monday", "period": 2, "start_time": "9:00", "end_time": "9:45", "subject": "Literacy (Phonics)", "lesson_type": "Literacy"},
    {"class_code": "3A", "day_of_week": "Monday", "period": 3, "start_time": "9:45", "end_time": "10:15", "subject": "ICT", "lesson_type": "Specialist", "specialist_name": "Unknown"},
    {"class_code": "3A", "day_of_week": "Monday", "period": 4, "start_time": "10:15", "end_time": "10:45", "subject": "Break", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Monday", "period": 5, "start_time": "10:45", "end_time": "11:30", "subject": "Numeracy", "lesson_type": "Numeracy"},
    {"class_code": "3A", "day_of_week": "Monday", "period": 6, "start_time": "11:30", "end_time": "12:15", "subject": "Foundation Learning (Choice Time)", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Monday", "period": 7, "start_time": "12:15", "end_time": "1:00", "subject": "Lunch", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Monday", "period": 8, "start_time": "1:00", "end_time": "1:30", "subject": "Guided Reading (Small Group rotation)", "lesson_type": "Literacy"},
    {"class_code": "3A", "day_of_week": "Monday", "period": 9, "start_time": "1:30", "end_time": "2:15", "subject": "Topic/Science", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Monday", "period": 10, "start_time": "2:15", "end_time": "2:45", "subject": "Story & Reflection", "lesson_type": "Foundation"},
    
    # Y3 CLASS (3A) - Tuesday
    {"class_code": "3A", "day_of_week": "Tuesday", "period": 1, "start_time": "8:30", "end_time": "9:00", "subject": "Arrival & Transitions", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Tuesday", "period": 2, "start_time": "9:00", "end_time": "9:45", "subject": "Literacy (Reading)", "lesson_type": "Literacy"},
    {"class_code": "3A", "day_of_week": "Tuesday", "period": 3, "start_time": "9:45", "end_time": "10:15", "subject": "Break", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Tuesday", "period": 4, "start_time": "10:15", "end_time": "10:45", "subject": "Numeracy", "lesson_type": "Numeracy"},
    {"class_code": "3A", "day_of_week": "Tuesday", "period": 5, "start_time": "10:45", "end_time": "11:30", "subject": "Numeracy & Mastery", "lesson_type": "Numeracy"},
    {"class_code": "3A", "day_of_week": "Tuesday", "period": 6, "start_time": "11:30", "end_time": "12:15", "subject": "Foundation Learning", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Tuesday", "period": 7, "start_time": "12:15", "end_time": "1:00", "subject": "Lunch", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Tuesday", "period": 8, "start_time": "1:00", "end_time": "1:30", "subject": "PE Specialist", "lesson_type": "Specialist", "specialist_name": "Unknown"},
    {"class_code": "3A", "day_of_week": "Tuesday", "period": 9, "start_time": "1:30", "end_time": "2:15", "subject": "Topic/Science", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Tuesday", "period": 10, "start_time": "2:15", "end_time": "2:45", "subject": "Story & Reflection", "lesson_type": "Foundation"},
    
    # Y3 CLASS (3A) - Wednesday
    {"class_code": "3A", "day_of_week": "Wednesday", "period": 1, "start_time": "8:30", "end_time": "9:00", "subject": "Arrival & Transitions", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Wednesday", "period": 2, "start_time": "9:00", "end_time": "9:45", "subject": "Literacy (Writing)", "lesson_type": "Literacy"},
    {"class_code": "3A", "day_of_week": "Wednesday", "period": 3, "start_time": "9:45", "end_time": "10:15", "subject": "ICT Specialist", "lesson_type": "Specialist", "specialist_name": "Unknown"},
    {"class_code": "3A", "day_of_week": "Wednesday", "period": 4, "start_time": "10:15", "end_time": "10:45", "subject": "Break", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Wednesday", "period": 5, "start_time": "10:45", "end_time": "11:30", "subject": "Numeracy & Mastery", "lesson_type": "Numeracy"},
    {"class_code": "3A", "day_of_week": "Wednesday", "period": 6, "start_time": "11:30", "end_time": "12:15", "subject": "Foundation Learning", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Wednesday", "period": 7, "start_time": "12:15", "end_time": "1:00", "subject": "Lunch", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Wednesday", "period": 8, "start_time": "1:00", "end_time": "1:30", "subject": "Music Specialist", "lesson_type": "Specialist", "specialist_name": "Unknown"},
    {"class_code": "3A", "day_of_week": "Wednesday", "period": 9, "start_time": "1:30", "end_time": "2:15", "subject": "Topic/Science", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Wednesday", "period": 10, "start_time": "2:15", "end_time": "2:45", "subject": "Story & Reflection", "lesson_type": "Foundation"},
    
    # Y3 CLASS (3A) - Thursday
    {"class_code": "3A", "day_of_week": "Thursday", "period": 1, "start_time": "8:30", "end_time": "9:00", "subject": "Arrival & Transitions", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Thursday", "period": 2, "start_time": "9:00", "end_time": "9:45", "subject": "Literacy (Phonics)", "lesson_type": "Literacy"},
    {"class_code": "3A", "day_of_week": "Thursday", "period": 3, "start_time": "9:45", "end_time": "10:15", "subject": "Break", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Thursday", "period": 4, "start_time": "10:15", "end_time": "10:45", "subject": "PE Specialist", "lesson_type": "Specialist", "specialist_name": "Unknown"},
    {"class_code": "3A", "day_of_week": "Thursday", "period": 5, "start_time": "10:45", "end_time": "11:30", "subject": "Numeracy", "lesson_type": "Numeracy"},
    {"class_code": "3A", "day_of_week": "Thursday", "period": 6, "start_time": "11:30", "end_time": "12:15", "subject": "Foundation Learning", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Thursday", "period": 7, "start_time": "12:15", "end_time": "1:00", "subject": "Lunch", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Thursday", "period": 8, "start_time": "1:00", "end_time": "1:30", "subject": "Guided Reading", "lesson_type": "Literacy"},
    {"class_code": "3A", "day_of_week": "Thursday", "period": 9, "start_time": "1:30", "end_time": "2:15", "subject": "Topic/Science", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Thursday", "period": 10, "start_time": "2:15", "end_time": "2:45", "subject": "Story & Reflection", "lesson_type": "Foundation"},
    
    # Y3 CLASS (3A) - Friday
    {"class_code": "3A", "day_of_week": "Friday", "period": 1, "start_time": "8:30", "end_time": "9:00", "subject": "Arrival & Transitions", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Friday", "period": 2, "start_time": "9:00", "end_time": "9:45", "subject": "Literacy (Shared Text)", "lesson_type": "Literacy"},
    {"class_code": "3A", "day_of_week": "Friday", "period": 3, "start_time": "9:45", "end_time": "10:15", "subject": "Art", "lesson_type": "Specialist", "specialist_name": "Unknown"},
    {"class_code": "3A", "day_of_week": "Friday", "period": 4, "start_time": "10:15", "end_time": "10:45", "subject": "Break", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Friday", "period": 5, "start_time": "10:45", "end_time": "11:30", "subject": "Numeracy", "lesson_type": "Numeracy"},
    {"class_code": "3A", "day_of_week": "Friday", "period": 6, "start_time": "11:30", "end_time": "12:15", "subject": "Foundation Learning", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Friday", "period": 7, "start_time": "12:15", "end_time": "1:00", "subject": "Lunch", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Friday", "period": 8, "start_time": "1:00", "end_time": "1:30", "subject": "Guided Reading", "lesson_type": "Literacy"},
    {"class_code": "3A", "day_of_week": "Friday", "period": 9, "start_time": "1:30", "end_time": "2:15", "subject": "Topic/Science", "lesson_type": "Foundation"},
    {"class_code": "3A", "day_of_week": "Friday", "period": 10, "start_time": "2:15", "end_time": "2:45", "subject": "Story & Reflection", "lesson_type": "Foundation"},
]

def import_timetable():
    """Import timetable data"""
    db = SessionLocal()
    try:
        # Clear existing timetable
        db.query(Timetable).delete()
        db.commit()
        
        # Import new timetable
        for timetable_data in TIMETABLE_DATA:
            timetable = Timetable(**timetable_data)
            db.add(timetable)
        
        db.commit()
        print(f"✅ Imported {len(TIMETABLE_DATA)} timetable entries")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error importing timetable: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_timetable()
