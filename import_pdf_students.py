#!/usr/bin/env python3
"""
Import the 40 students from the PDF dataset into the SQL database.
This creates the authoritative student records for 3A, 4B, 5C, 6D classes.
"""

import sys
from pathlib import Path
from datetime import datetime, date

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.core.database import SessionLocal
from backend.models.database_models import Student

# The 40 students from the PDF dataset
STUDENTS_DATA = [
    # Y3 Class (3A)
    {"name": "Aisha Kumar", "class_code": "3A", "year_group": "3", "campus": "JC", "support_level": 0},
    {"name": "Marcus Thompson", "class_code": "3A", "year_group": "3", "campus": "JC", "support_level": 1},
    {"name": "Sophie Chen", "class_code": "3A", "year_group": "3", "campus": "JC", "support_level": 1},
    {"name": "Liam O'Brien", "class_code": "3A", "year_group": "3", "campus": "JC", "support_level": 1},
    {"name": "Priya Patel", "class_code": "3A", "year_group": "3", "campus": "JC", "support_level": 0},
    {"name": "Noah Williams", "class_code": "3A", "year_group": "3", "campus": "JC", "support_level": 2},
    {"name": "Zoe Martinez", "class_code": "3A", "year_group": "3", "campus": "JC", "support_level": 1},
    {"name": "James Park", "class_code": "3A", "year_group": "3", "campus": "JC", "support_level": 1},
    {"name": "Emma Novak", "class_code": "3A", "year_group": "3", "campus": "JC", "support_level": 0},
    {"name": "Oliver Grant", "class_code": "3A", "year_group": "3", "campus": "JC", "support_level": 1},
    
    # Y4 Class (4B)
    {"name": "Isabella Rossi", "class_code": "4B", "year_group": "4", "campus": "JC", "support_level": 0},
    {"name": "Kai Tanaka", "class_code": "4B", "year_group": "4", "campus": "JC", "support_level": 1},
    {"name": "Thomas Bradley", "class_code": "4B", "year_group": "4", "campus": "JC", "support_level": 1},
    {"name": "Amelia Hassan", "class_code": "4B", "year_group": "4", "campus": "JC", "support_level": 0},
    {"name": "Dylan Murphy", "class_code": "4B", "year_group": "4", "campus": "JC", "support_level": 1},
    {"name": "Marta Silva", "class_code": "4B", "year_group": "4", "campus": "JC", "support_level": 1},
    {"name": "Joshua Finch", "class_code": "4B", "year_group": "4", "campus": "JC", "support_level": 2},
    {"name": "Natalia Kowalski", "class_code": "4B", "year_group": "4", "campus": "JC", "support_level": 1},
    {"name": "Ravi Gupta", "class_code": "4B", "year_group": "4", "campus": "JC", "support_level": 1},
    {"name": "Lucia Fernandez", "class_code": "4B", "year_group": "4", "campus": "JC", "support_level": 0},
    
    # Y5 Class (5C)
    {"name": "Lucas Santos", "class_code": "5C", "year_group": "5", "campus": "JC", "support_level": 0},
    {"name": "Grace Pham", "class_code": "5C", "year_group": "5", "campus": "JC", "support_level": 1},
    {"name": "Sebastian White", "class_code": "5C", "year_group": "5", "campus": "JC", "support_level": 1},
    {"name": "Yuki Yamamoto", "class_code": "5C", "year_group": "5", "campus": "JC", "support_level": 0},
    {"name": "Freya Nielsen", "class_code": "5C", "year_group": "5", "campus": "JC", "support_level": 1},
    {"name": "Mohammed Al-Rashid", "class_code": "5C", "year_group": "5", "campus": "JC", "support_level": 2},
    {"name": "Ivy Chen", "class_code": "5C", "year_group": "5", "campus": "JC", "support_level": 0},
    {"name": "Ethan Hughes", "class_code": "5C", "year_group": "5", "campus": "JC", "support_level": 1},
    {"name": "Sofia Delgado", "class_code": "5C", "year_group": "5", "campus": "JC", "support_level": 1},
    {"name": "Alexander Petrov", "class_code": "5C", "year_group": "5", "campus": "JC", "support_level": 0},
    
    # Y6 Class (6D)
    {"name": "Charlotte Webb", "class_code": "6D", "year_group": "6", "campus": "JC", "support_level": 0},
    {"name": "Dmitri Sokolov", "class_code": "6D", "year_group": "6", "campus": "JC", "support_level": 1},
    {"name": "Amal Al-Noor", "class_code": "6D", "year_group": "6", "campus": "JC", "support_level": 1},
    {"name": "Kenji Nakamura", "class_code": "6D", "year_group": "6", "campus": "JC", "support_level": 0},
    {"name": "Sienna Brown", "class_code": "6D", "year_group": "6", "campus": "JC", "support_level": 2},
    {"name": "Lars Andersen", "class_code": "6D", "year_group": "6", "campus": "JC", "support_level": 1},
    {"name": "Maya Goldstein", "class_code": "6D", "year_group": "6", "campus": "JC", "support_level": 0},
    {"name": "Cairo Lopez", "class_code": "6D", "year_group": "6", "campus": "JC", "support_level": 1},
    {"name": "Priya Verma", "class_code": "6D", "year_group": "6", "campus": "JC", "support_level": 1},
    {"name": "Harry Chen", "class_code": "6D", "year_group": "6", "campus": "JC", "support_level": 0},
]

def import_students():
    """Import all 40 students into the database"""
    db = SessionLocal()
    try:
        print("Importing 40 students from PDF dataset...")
        
        students = []
        for data in STUDENTS_DATA:
            student = Student(
                name=data["name"],
                class_code=data["class_code"],
                year_group=data["year_group"],
                campus=data["campus"],
                support_level=data["support_level"],
                support_notes=None,
                house=None
            )
            students.append(student)
        
        db.add_all(students)
        db.commit()
        
        # Verify import
        count = db.query(Student).count()
        by_class = {}
        for cls in ["3A", "4B", "5C", "6D"]:
            by_class[cls] = db.query(Student).filter(Student.class_code == cls).count()
        
        print(f"✓ Successfully imported {count} students")
        print(f"  - 3A: {by_class['3A']} students")
        print(f"  - 4B: {by_class['4B']} students")
        print(f"  - 5C: {by_class['5C']} students")
        print(f"  - 6D: {by_class['6D']} students")
        
        return True
        
    except Exception as e:
        print(f"✗ Error importing students: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = import_students()
    sys.exit(0 if success else 1)
