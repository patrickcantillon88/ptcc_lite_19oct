"""
Student Accommodations API endpoints
GET /api/accommodations/student/{student_id}
GET /api/accommodations/active/{student_id}
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.database_models import StudentAccommodation, Student

router = APIRouter(prefix="/api/accommodations", tags=["accommodations"])


@router.get("/student/{student_id}", response_model=List[dict])
def get_student_accommodations(student_id: int, db: Session = Depends(get_db)):
    """Get all accommodations for a student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    accommodations = db.query(StudentAccommodation).filter(
        StudentAccommodation.student_id == student_id
    ).all()
    
    if not accommodations:
        raise HTTPException(status_code=404, detail="No accommodations found for this student")
    
    return [
        {
            "id": a.id,
            "student_id": a.student_id,
            "student_name": student.name,
            "accommodation_type": a.accommodation_type,
            "description": a.description,
            "implementation_details": a.implementation_details,
            "active": a.active,
            "effective_date": str(a.effective_date),
            "notes": a.notes
        }
        for a in accommodations
    ]


@router.get("/active/{student_id}", response_model=List[dict])
def get_active_accommodations(student_id: int, db: Session = Depends(get_db)):
    """Get active accommodations for a student (for today)"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    accommodations = db.query(StudentAccommodation).filter(
        StudentAccommodation.student_id == student_id,
        StudentAccommodation.active == True
    ).all()
    
    if not accommodations:
        raise HTTPException(status_code=404, detail="No active accommodations for this student")
    
    return [
        {
            "id": a.id,
            "student_id": a.student_id,
            "student_name": student.name,
            "accommodation_type": a.accommodation_type,
            "description": a.description,
            "implementation_details": a.implementation_details,
            "active": a.active,
            "effective_date": str(a.effective_date),
            "notes": a.notes
        }
        for a in accommodations
    ]
