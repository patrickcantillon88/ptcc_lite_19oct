"""
Staff API endpoints
GET /api/staff/by-class/{class_code}
GET /api/staff/{staff_id}
GET /api/staff/search
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.database_models import Staff

router = APIRouter(prefix="/api/staff", tags=["staff"])


class StaffResponse:
    def __init__(self, staff):
        self.id = staff.id
        self.name = staff.name
        self.role = staff.role
        self.class_code = staff.class_code
        self.term = staff.term
        self.active = staff.active


@router.get("/by-class/{class_code}", response_model=List[dict])
def get_staff_by_class(class_code: str, db: Session = Depends(get_db)):
    """Get all staff assigned to a class"""
    staff = db.query(Staff).filter(Staff.class_code == class_code).all()
    if not staff:
        raise HTTPException(status_code=404, detail="No staff found for this class")
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "role": s.role,
            "class_code": s.class_code,
            "term": s.term,
            "active": s.active
        }
        for s in staff
    ]


@router.get("/{staff_id}", response_model=dict)
def get_staff(staff_id: int, db: Session = Depends(get_db)):
    """Get individual staff member by ID"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    return {
        "id": staff.id,
        "name": staff.name,
        "role": staff.role,
        "class_code": staff.class_code,
        "term": staff.term,
        "active": staff.active
    }


@router.get("/search/", response_model=List[dict])
def search_staff(name: str = None, role: str = None, db: Session = Depends(get_db)):
    """Search staff by name or role"""
    query = db.query(Staff)
    
    if name:
        query = query.filter(Staff.name.ilike(f"%{name}%"))
    
    if role:
        query = query.filter(Staff.role.ilike(f"%{role}%"))
    
    staff = query.all()
    
    if not staff:
        raise HTTPException(status_code=404, detail="No staff found matching criteria")
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "role": s.role,
            "class_code": s.class_code,
            "term": s.term,
            "active": s.active
        }
        for s in staff
    ]
