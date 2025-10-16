#!/usr/bin/env python3
"""
CCA Comments API for PTCC

API endpoints for managing Co-Curricular Activities (CCA) behavior comments.
Integrates with existing quick_logs table with CCA-specific categorization.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel
import csv
import io

from ..core.database import get_db
from ..core.logging_config import get_logger
from ..models.database_models import Student, QuickLog

logger = get_logger("api.cca")
router = APIRouter()

# CCA Subject categories based on the CSV structure
CCA_SUBJECTS = [
    "PE",
    "Music/PA",
    "ICT/STEAM",
    "MFL",
    "Vietnamese Culture",
    "Vietnamese Language",
    "Art",
    "Maths",
    "CCAs/Other"
]


class CCACommentCreate(BaseModel):
    """Model for creating CCA comment"""
    student_id: int
    cca_subject: str
    comment: str
    comment_type: str = "neutral"  # positive, neutral, concern


class CCACommentResponse(BaseModel):
    """Model for CCA comment response"""
    id: int
    student_id: int
    student_name: str
    class_code: str
    cca_subject: str
    comment: str
    comment_type: str
    timestamp: str


class StudentCCAComments(BaseModel):
    """Model for student with all CCA comments"""
    student_id: int
    student_name: str
    form: str
    comments_by_subject: Dict[str, Optional[dict]]


@router.get("/subjects")
async def list_cca_subjects():
    """Get list of available CCA subjects"""
    return {"subjects": CCA_SUBJECTS}


@router.get("/students/search")
async def search_students_for_cca(
    q: str = "",
    db: Session = Depends(get_db)
):
    """
    Search students for CCA comment entry.
    Returns students grouped by form/class.
    """
    try:
        query = db.query(Student)
        
        if q:
            search_term = f"%{q}%"
            query = query.filter(
                (Student.name.ilike(search_term)) | 
                (Student.class_code.ilike(search_term))
            )
        
        students = query.order_by(Student.class_code, Student.name).all()
        
        # Group by form
        students_by_form = {}
        for student in students:
            form = student.class_code
            if form not in students_by_form:
                students_by_form[form] = []
            
            # Get comment count for this student
            comment_count = db.query(QuickLog).filter(
                QuickLog.student_id == student.id,
                QuickLog.cca_subject.isnot(None)
            ).count()
            
            students_by_form[form].append({
                "id": student.id,
                "name": student.name,
                "form": form,
                "comment_count": comment_count
            })
        
        return {
            "students_by_form": students_by_form,
            "total": len(students)
        }
        
    except Exception as e:
        logger.error(f"Error searching students for CCA: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students/{student_id}/comments")
async def get_student_cca_comments(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all CCA comments for a student, organized by subject.
    """
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get all CCA comments for this student
        cca_logs = db.query(QuickLog).filter(
            QuickLog.student_id == student_id,
            QuickLog.cca_subject.isnot(None)
        ).order_by(desc(QuickLog.timestamp)).all()
        
        # Organize by subject
        comments_by_subject = {}
        for subject in CCA_SUBJECTS:
            # Find most recent comment for this subject
            subject_comments = [log for log in cca_logs if log.cca_subject == subject]
            if subject_comments:
                latest = subject_comments[0]
                comments_by_subject[subject] = {
                    "id": latest.id,
                    "comment": latest.note,
                    "type": latest.log_type,
                    "timestamp": latest.timestamp.isoformat(),
                    "category": latest.category
                }
            else:
                comments_by_subject[subject] = None
        
        return {
            "student_id": student.id,
            "student_name": student.name,
            "form": student.class_code,
            "comments_by_subject": comments_by_subject
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CCA comments for student {student_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/comments")
async def create_cca_comment(
    comment: CCACommentCreate,
    db: Session = Depends(get_db)
):
    """
    Create or update a CCA comment for a student.
    """
    try:
        # Verify student exists
        student = db.query(Student).filter(Student.id == comment.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Verify subject is valid
        if comment.cca_subject not in CCA_SUBJECTS:
            raise HTTPException(status_code=400, detail=f"Invalid CCA subject. Must be one of: {CCA_SUBJECTS}")
        
        # Create new log entry
        new_log = QuickLog(
            student_id=comment.student_id,
            class_code=student.class_code,
            log_type=comment.comment_type,
            category=f"cca_{comment.cca_subject.lower().replace('/', '_').replace(' ', '_')}",
            note=comment.comment,
            cca_subject=comment.cca_subject,
            timestamp=datetime.now()
        )
        
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        
        return {
            "id": new_log.id,
            "student_id": new_log.student_id,
            "student_name": student.name,
            "class_code": new_log.class_code,
            "cca_subject": new_log.cca_subject,
            "comment": new_log.note,
            "comment_type": new_log.log_type,
            "timestamp": new_log.timestamp.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating CCA comment: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/comments/{comment_id}")
async def update_cca_comment(
    comment_id: int,
    comment: str,
    comment_type: str,
    db: Session = Depends(get_db)
):
    """Update an existing CCA comment"""
    try:
        log = db.query(QuickLog).filter(QuickLog.id == comment_id).first()
        if not log or log.cca_subject is None:
            raise HTTPException(status_code=404, detail="CCA comment not found")
        
        log.note = comment
        log.log_type = comment_type
        log.timestamp = datetime.now()
        
        db.commit()
        
        return {"message": "Comment updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating CCA comment {comment_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/comments/{comment_id}")
async def delete_cca_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """Delete a CCA comment"""
    try:
        log = db.query(QuickLog).filter(QuickLog.id == comment_id).first()
        if not log or log.cca_subject is None:
            raise HTTPException(status_code=404, detail="CCA comment not found")
        
        db.delete(log)
        db.commit()
        
        return {"message": "Comment deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting CCA comment {comment_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import/csv")
async def import_cca_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Import CCA comments from CSV file.
    Expected format: Surname, Forename, Preferred Name, Form, [CCA Subject columns...]
    """
    try:
        # Read CSV content
        contents = await file.read()
        csv_text = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is 1)
            try:
                # Extract student info
                surname = row.get('Surname', '').strip()
                forename = row.get('Forename (Firstname)', '').split('(')[0].strip() if row.get('Forename (Firstname)') else row.get('Forename', '').strip()
                form = row.get('Form', '').strip()
                
                if not surname or not forename or not form:
                    skipped_count += 1
                    continue
                
                # Find student by name and form
                full_name = f"{forename} {surname}"
                student = db.query(Student).filter(
                    Student.name.ilike(f"%{forename}%"),
                    Student.name.ilike(f"%{surname}%"),
                    Student.class_code == form
                ).first()
                
                if not student:
                    errors.append(f"Row {row_num}: Student not found: {full_name} ({form})")
                    skipped_count += 1
                    continue
                
                # Process each CCA subject column
                for subject in CCA_SUBJECTS:
                    comment_text = row.get(subject, '').strip()
                    
                    if comment_text:
                        # Determine comment type based on content
                        comment_type = "neutral"
                        if any(word in comment_text.lower() for word in ['outstanding', 'excellent', 'top', 'great']):
                            comment_type = "positive"
                        elif any(word in comment_text.lower() for word in ['concern', 'issue', 'problem']):
                            comment_type = "concern"
                        
                        # Create log entry
                        new_log = QuickLog(
                            student_id=student.id,
                            class_code=student.class_code,
                            log_type=comment_type,
                            category=f"cca_{subject.lower().replace('/', '_').replace(' ', '_')}",
                            note=comment_text,
                            cca_subject=subject,
                            timestamp=datetime.now()
                        )
                        
                        db.add(new_log)
                        imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                skipped_count += 1
                continue
        
        db.commit()
        
        return {
            "message": "CSV import completed",
            "imported": imported_count,
            "skipped": skipped_count,
            "errors": errors[:10]  # Return first 10 errors
        }
        
    except Exception as e:
        logger.error(f"Error importing CCA CSV: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"CSV import failed: {str(e)}")


@router.get("/export/csv")
async def export_cca_csv(
    db: Session = Depends(get_db)
):
    """
    Export all CCA comments to CSV format.
    Returns CSV matching the import format.
    """
    try:
        # Get all students
        students = db.query(Student).order_by(Student.class_code, Student.name).all()
        
        # Build CSV
        output = io.StringIO()
        fieldnames = ['Surname', 'Forename (Firstname)', 'Preferred Name', 'Form'] + CCA_SUBJECTS
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for student in students:
            # Get latest CCA comments for this student
            cca_logs = db.query(QuickLog).filter(
                QuickLog.student_id == student.id,
                QuickLog.cca_subject.isnot(None)
            ).order_by(desc(QuickLog.timestamp)).all()
            
            # Build row
            name_parts = student.name.split()
            surname = name_parts[-1] if name_parts else ""
            forename = " ".join(name_parts[:-1]) if len(name_parts) > 1 else name_parts[0] if name_parts else ""
            
            row = {
                'Surname': surname,
                'Forename (Firstname)': forename,
                'Preferred Name': '',
                'Form': student.class_code
            }
            
            # Add comments for each subject
            for subject in CCA_SUBJECTS:
                subject_logs = [log for log in cca_logs if log.cca_subject == subject]
                row[subject] = subject_logs[0].note if subject_logs else ''
            
            writer.writerow(row)
        
        return {
            "csv_content": output.getvalue(),
            "filename": f"cca_comments_{datetime.now().strftime('%Y%m%d')}.csv"
        }
        
    except Exception as e:
        logger.error(f"Error exporting CCA CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))
