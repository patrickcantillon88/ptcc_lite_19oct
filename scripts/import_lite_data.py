#!/usr/bin/env python3
"""
PTCC Lite Data Import Script

Imports:
- CAT4 student data (720 students)
- Class rosters (Primary Class List)
- ICT timetable
- Quizziz assessment data (10 quiz files)

Run: python scripts/import_lite_data.py
"""

import pandas as pd
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.database import SessionLocal, engine
from backend.models.database_models import (
    Student, Schedule, Timetable, Assessment, Base
)

# Database
db = SessionLocal()

# Data paths
DOWNLOADS = os.path.expanduser("~/Downloads")
DATA_DIR = os.path.expanduser("~/Desktop/ptcc_lite_19oct/data")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def get_your_ict_classes():
    """Get list of YOUR ICT classes from class roster"""
    # Your ICT classes based on actual timetable
    # These are the classes you actually teach
    return ['3A', '3C', '4A', '4B', '5A', '5B', '6A', '6C']  # Adjust based on your actual schedule

def import_cat4_data():
    """Import CAT4 student data ONLY for YOUR ICT classes"""
    print("\n📚 Importing CAT4 data (YOUR ICT classes only)...")
    
    cat4_file = f"{DOWNLOADS}/data (1).xlsx"
    if not os.path.exists(cat4_file):
        print(f"❌ CAT4 file not found: {cat4_file}")
        return 0
    
    your_classes = get_your_ict_classes()
    print(f"  Filtering for classes: {your_classes}")
    
    try:
        df = pd.read_excel(cat4_file)
        print(f"  Found {len(df)} total student records")
        
        imported = 0
        for idx, row in df.iterrows():
            form = str(row.get('Form', '')).strip()
            
            # ONLY import if in your ICT classes
            if form not in your_classes:
                continue
            
            # Skip if student already exists
            existing = db.query(Student).filter_by(name=str(row.get('Name', ''))).first()
            if existing:
                continue
            
            # Create student record
            student = Student(
                name=str(row.get('Name', '')).strip(),
                year_group=form[0] if form else 'Unknown',  # Extract year from form (e.g., '3' from '3A')
                class_code=form if form else 'Unknown',
                campus='A',  # Default campus
                support_level=0,
                support_notes=json.dumps({
                    'ls_flag': str(row.get('LS Flag', '')),
                    'eal_flag': str(row.get('EAL Flag', '')),
                    'cat4_verbal': row.get('Verbal', 0),
                    'cat4_quantitative': row.get('Quantitative', 0),
                    'cat4_nonverbal': row.get('Non-Verbal', 0),
                    'cat4_spatial': row.get('Spatial', 0),
                    'cat4_mean': row.get('Mean', 0)
                })
            )
            db.add(student)
            imported += 1
            
            if imported % 10 == 0:
                print(f"  ✓ Imported {imported} students...")
        
        db.commit()
        print(f"✅ CAT4 import complete: {imported} students from YOUR classes")
        return imported
    except Exception as e:
        print(f"❌ Error importing CAT4 data: {e}")
        db.rollback()
        return 0

def import_class_roster():
    """Import class roster from Primary Class List"""
    print("\n📋 Importing class roster...")
    
    roster_file = os.path.expanduser("~/Desktop/ptcc_lite_19oct/data/GDRIVE/Primary Class List 2025-2026 (1).xlsx")
    if not os.path.exists(roster_file):
        print(f"❌ Class roster file not found: {roster_file}")
        return 0
    
    try:
        df = pd.read_excel(roster_file)
        print(f"  Found {len(df)} records in class roster")
        
        # Update existing students with class roster data
        imported = 0
        for idx, row in df.iterrows():
            name = str(row.get('Student Name', '')).strip() if 'Student Name' in df.columns else None
            if not name:
                continue
            
            student = db.query(Student).filter_by(name=name).first()
            if not student:
                continue
            
            # Update with roster data
            form = str(row.get('Form', '')).strip() if 'Form' in df.columns else student.class_code
            student.class_code = form
            student.year_group = form[0] if form else student.year_group
            
            # Nationality, EAL tier
            if 'EAL Tier' in df.columns:
                eal_tier = str(row.get('EAL Tier', ''))
                notes = json.loads(student.support_notes or '{}')
                notes['eal_tier'] = eal_tier
                student.support_notes = json.dumps(notes)
            
            db.add(student)
            imported += 1
        
        db.commit()
        print(f"✅ Class roster import complete: {imported} students updated")
        return imported
    except Exception as e:
        print(f"❌ Error importing class roster: {e}")
        db.rollback()
        return 0

def import_timetable():
    """Import ICT timetable"""
    print("\n⏰ Importing ICT timetable...")
    
    timetable_file = os.path.expanduser("~/Desktop/ptcc_lite_19oct/data/GDRIVE/Timetables/ICT Timetable 25_26.xlsx")
    if not os.path.exists(timetable_file):
        print(f"❌ Timetable file not found: {timetable_file}")
        return 0
    
    try:
        df = pd.read_excel(timetable_file)
        print(f"  Found {len(df)} timetable entries")
        
        imported = 0
        for idx, row in df.iterrows():
            # Extract period info
            period_info = str(row.get('Period', '') or '').strip()
            if not period_info:
                continue
            
            # Create timetable entry
            timetable = Timetable(
                class_code=str(row.get('Class', '')).strip() or 'Unknown',
                day_of_week=str(row.get('Day', '')).strip() or 'Monday',
                period=int(row.get('Period', 1)) if 'Period' in df.columns else 1,
                start_time=str(row.get('Start Time', '')).strip() or '09:00',
                end_time=str(row.get('End Time', '')).strip() or '09:45',
                subject=str(row.get('Subject', '')).strip() or 'ICT',
                lesson_type='Specialist' if 'specialist' in str(row).lower() else 'Foundation',
                room=str(row.get('Room', '')).strip() or 'ICT Lab'
            )
            db.add(timetable)
            imported += 1
        
        db.commit()
        print(f"✅ Timetable import complete: {imported} entries")
        return imported
    except Exception as e:
        print(f"❌ Error importing timetable: {e}")
        db.rollback()
        return 0

def import_quizziz_data():
    """Import Quizziz data from Downloads"""
    print("\n📊 Importing Quizziz data...")
    
    # Find all Quizziz files
    quizziz_files = [
        f"{DOWNLOADS}/Y4TinkerCadCheckIN-2025-10-19T07_53_41_090876-62911f.xlsx",
        f"{DOWNLOADS}/Y4TinkerCadCheckIN-2025-10-19T07_53_31_356884-12868a.xlsx",
        f"{DOWNLOADS}/Y6SpheroCheckIN-2025-10-19T07_53_24_734693-b54282.xlsx",
        f"{DOWNLOADS}/Y6SpheroCheckIN-2025-10-19T07_53_16_676644-4c674e.xlsx",
        f"{DOWNLOADS}/Y4TinkerCadCheckIN-2025-10-19T07_53_09_150169-b61114.xlsx",
        f"{DOWNLOADS}/DelightExQuiz-2025-10-19T07_53_02_278888-6017a3.xlsx",
        f"{DOWNLOADS}/DelightExQuiz-2025-10-19T07_52_45_195054-3541a8.xlsx",
        f"{DOWNLOADS}/DelightExCheckIn-2025-10-19T07_52_39_264484-caa0b3.xlsx",
        f"{DOWNLOADS}/SpheroBOLTProgrammingQuiz6C-2025-10-19T07_52_32_542933-d91dee.xlsx",
        f"{DOWNLOADS}/Y5DelightExSpace-2025-10-19T07_52_25_809638-6ba9e0.xlsx",
    ]
    
    imported = 0
    for quiz_file in quizziz_files:
        if not os.path.exists(quiz_file):
            continue
        
        try:
            df = pd.read_excel(quiz_file)
            filename = os.path.basename(quiz_file)
            print(f"  Processing {filename}...")
            
            # Extract quiz metadata
            quiz_name = filename.replace('.xlsx', '').split('-')[0]
            
            # Parse student performance data (columns are typically student names)
            for col in df.columns:
                if col in ['Question', 'Topic', 'Difficulty']:  # Skip metadata columns
                    continue
                
                # This column is likely a student name
                student_name = str(col).strip()
                student = db.query(Student).filter_by(name=student_name).first()
                if not student:
                    continue
                
                # Calculate performance from this quiz
                col_data = df[col]
                correct = (col_data == 'Correct').sum() if 'Correct' in col_data.values else 0
                total = len(col_data.dropna())
                
                if total > 0:
                    percentage = (correct / total) * 100
                    
                    assessment = Assessment(
                        student_id=student.id,
                        assessment_type='Quizziz',
                        subject='ICT',
                        topic=quiz_name,
                        score=correct,
                        max_score=total,
                        percentage=percentage,
                        date=datetime.now().date(),
                        source=filename
                    )
                    db.add(assessment)
                    imported += 1
            
            db.commit()
        except Exception as e:
            print(f"  ⚠️ Error processing {quiz_file}: {e}")
            db.rollback()
            continue
    
    print(f"✅ Quizziz import complete: {imported} assessments")
    return imported

def create_tables():
    """Create all database tables"""
    print("\n🗂️ Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

def main():
    """Run all imports"""
    print("=" * 60)
    print("🚀 PTCC LITE DATA IMPORT")
    print("=" * 60)
    
    # Create tables
    create_tables()
    
    # Import data
    try:
        cat4_count = import_cat4_data()
        roster_count = import_class_roster()
        timetable_count = import_timetable()
        quizziz_count = import_quizziz_data()
        
        print("\n" + "=" * 60)
        print("📊 IMPORT SUMMARY")
        print("=" * 60)
        print(f"  Students: {cat4_count} imported")
        print(f"  Class Roster: {roster_count} updated")
        print(f"  Timetable: {timetable_count} entries")
        print(f"  Quizziz: {quizziz_count} assessments")
        print("=" * 60)
        print("✅ Data import complete!")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
