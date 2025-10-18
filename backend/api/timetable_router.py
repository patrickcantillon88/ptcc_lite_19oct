"""
Timetable API endpoints
GET /api/timetable/class/{class_code}
GET /api/timetable/today/{class_code}
GET /api/timetable/period/{class_code}/{day}/{period}
GET /api/timetable/specialist-lessons/{class_code}
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.database_models import Timetable

router = APIRouter(prefix="/api/timetable", tags=["timetable"])

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


@router.get("/class/{class_code}", response_model=List[dict])
def get_class_timetable(class_code: str, db: Session = Depends(get_db)):
    """Get full weekly timetable for a class"""
    timetables = db.query(Timetable).filter(Timetable.class_code == class_code).all()
    
    if not timetables:
        raise HTTPException(status_code=404, detail="No timetable found for this class")
    
    return [
        {
            "id": t.id,
            "class_code": t.class_code,
            "day_of_week": t.day_of_week,
            "period": t.period,
            "start_time": t.start_time,
            "end_time": t.end_time,
            "subject": t.subject,
            "lesson_type": t.lesson_type,
            "specialist_name": t.specialist_name,
            "room": t.room,
            "notes": t.notes
        }
        for t in timetables
    ]


@router.get("/today/{class_code}", response_model=List[dict])
def get_today_timetable(class_code: str, db: Session = Depends(get_db)):
    """Get today's lessons for a class"""
    today_name = DAYS_OF_WEEK[datetime.now().weekday()] if datetime.now().weekday() < 5 else None
    
    if not today_name:
        raise HTTPException(status_code=400, detail="Today is not a school day (weekend)")
    
    timetables = db.query(Timetable).filter(
        Timetable.class_code == class_code,
        Timetable.day_of_week == today_name
    ).order_by(Timetable.period).all()
    
    if not timetables:
        raise HTTPException(status_code=404, detail="No timetable found for today")
    
    return [
        {
            "id": t.id,
            "class_code": t.class_code,
            "day_of_week": t.day_of_week,
            "period": t.period,
            "start_time": t.start_time,
            "end_time": t.end_time,
            "subject": t.subject,
            "lesson_type": t.lesson_type,
            "specialist_name": t.specialist_name,
            "room": t.room,
            "notes": t.notes
        }
        for t in timetables
    ]


@router.get("/period/{class_code}/{day}/{period}", response_model=dict)
def get_period_details(class_code: str, day: str, period: int, db: Session = Depends(get_db)):
    """Get details for a specific period"""
    timetable = db.query(Timetable).filter(
        Timetable.class_code == class_code,
        Timetable.day_of_week == day,
        Timetable.period == period
    ).first()
    
    if not timetable:
        raise HTTPException(status_code=404, detail="Period not found")
    
    return {
        "id": timetable.id,
        "class_code": timetable.class_code,
        "day_of_week": timetable.day_of_week,
        "period": timetable.period,
        "start_time": timetable.start_time,
        "end_time": timetable.end_time,
        "subject": timetable.subject,
        "lesson_type": timetable.lesson_type,
        "specialist_name": timetable.specialist_name,
        "room": timetable.room,
        "notes": timetable.notes
    }


@router.get("/specialist-lessons/{class_code}", response_model=List[dict])
def get_specialist_lessons(class_code: str, db: Session = Depends(get_db)):
    """Get all specialist lessons for a class"""
    timetables = db.query(Timetable).filter(
        Timetable.class_code == class_code,
        Timetable.lesson_type == "Specialist"
    ).all()
    
    if not timetables:
        raise HTTPException(status_code=404, detail="No specialist lessons found")
    
    return [
        {
            "id": t.id,
            "class_code": t.class_code,
            "day_of_week": t.day_of_week,
            "period": t.period,
            "start_time": t.start_time,
            "end_time": t.end_time,
            "subject": t.subject,
            "lesson_type": t.lesson_type,
            "specialist_name": t.specialist_name,
            "room": t.room,
            "notes": t.notes
        }
        for t in timetables
    ]
