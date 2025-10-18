"""
Import staff data from PDF dataset into Staff table
Run: python -m backend.ingestion.import_staff_data
"""

import json
from backend.core.database import SessionLocal
from backend.models.database_models import Staff

# Staff data extracted from PDF
STAFF_DATA = [
    # 3A
    {
        "name": "Ms Elena Rodriguez",
        "role": "Class Teacher",
        "class_code": "3A",
        "specialties": json.dumps([]),
        "term": "Term 1"
    },
    {
        "name": "Mr David Chen",
        "role": "Learning Support Teacher",
        "class_code": "3A",
        "specialties": json.dumps([]),
        "term": "Term 1"
    },
    {
        "name": "Ms Linh Tran",
        "role": "TA",
        "class_code": "3A",
        "specialties": json.dumps([]),
        "term": "Term 1"
    },
    
    # 4B
    {
        "name": "Mr Tariq Hassan",
        "role": "Class Teacher",
        "class_code": "4B",
        "specialties": json.dumps([]),
        "term": "Term 1"
    },
    {
        "name": "Ms Catherine Okafor",
        "role": "Learning Support Teacher",
        "class_code": "4B",
        "specialties": json.dumps([]),
        "term": "Term 1"
    },
    {
        "name": "Mr Duc Nguyen",
        "role": "TA",
        "class_code": "4B",
        "specialties": json.dumps([]),
        "term": "Term 1"
    },
    
    # 5C
    {
        "name": "Mr James Watson",
        "role": "Class Teacher",
        "class_code": "5C",
        "specialties": json.dumps([]),
        "term": "Term 1"
    },
    {
        "name": "Ms Fiona Liu",
        "role": "Learning Support Teacher",
        "class_code": "5C",
        "specialties": json.dumps([]),
        "term": "Term 1"
    },
    {
        "name": "Ms Anh Vo",
        "role": "TA",
        "class_code": "5C",
        "specialties": json.dumps([]),
        "term": "Term 1"
    },
    
    # 6D
    {
        "name": "Ms Rebecca Singh",
        "role": "Class Teacher",
        "class_code": "6D",
        "specialties": json.dumps([]),
        "term": "Term 1"
    },
    {
        "name": "Mr Michael O'Connor",
        "role": "Learning Support Teacher",
        "class_code": "6D",
        "specialties": json.dumps([]),
        "term": "Term 1"
    },
    {
        "name": "Ms Hoa Tran",
        "role": "TA",
        "class_code": "6D",
        "specialties": json.dumps([]),
        "term": "Term 1"
    },
]

def import_staff():
    """Import staff data"""
    db = SessionLocal()
    try:
        # Clear existing staff (optional)
        db.query(Staff).delete()
        db.commit()
        
        # Import new staff
        for staff_data in STAFF_DATA:
            staff = Staff(**staff_data)
            db.add(staff)
        
        db.commit()
        print(f"✅ Imported {len(STAFF_DATA)} staff members")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error importing staff: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_staff()
