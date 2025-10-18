#!/usr/bin/env python3
"""
Behavior Management API for PTCC

Tracks strikes, consequences, and behavior during lessons
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import uuid

from ..core.database import get_db
from ..core.logging_config import get_logger
from ..models.database_models import Student, QuickLog

logger = get_logger("api.behavior_management")
router = APIRouter()

# Strike consequences
STRIKE_CONSEQUENCES = {
    1: "Verbal Warning Issued.",
    2: "Final Warning. Next strike is a time-out.",
    3: "Time-out from device. Unplugged activity assigned."
}


class LessonStartRequest(BaseModel):
    """Request to start a new lesson"""
    class_code: str
    lesson_name: Optional[str] = None


class LessonResponse(BaseModel):
    """Response for lesson operations"""
    session_id: str
    class_code: str
    started_at: str
    student_count: int
    message: str


class StrikeRequest(BaseModel):
    """Request to add a strike"""
    student_id: int
    class_code: str
    description: str
    strike_level: int  # 1, 2, or 3
    admin_notified: bool = False
    hod_consulted: bool = False
    parent_meeting_scheduled: bool = False


class PositiveBehaviorRequest(BaseModel):
    """Request to log positive behavior"""
    student_id: int
    class_code: str
    description: str
    house_points: int = 1


class StudentLessonState(BaseModel):
    """Current state of a student in the lesson"""
    student_id: int
    student_name: str
    house: Optional[str]
    current_strikes: int
    strike_history: List[Dict[str, Any]]
    positive_count: int
    total_house_points: int


@router.post("/lesson/start", response_model=LessonResponse)
async def start_lesson(
    request: LessonStartRequest,
    db: Session = Depends(get_db)
):
    """
    Start a new lesson session
    
    Creates a unique session ID and returns student count
    """
    try:
        # Generate unique session ID
        session_id = f"lesson-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        # Get students in class
        students = db.query(Student).filter(
            Student.class_code == request.class_code
        ).all()
        
        if not students:
            raise HTTPException(
                status_code=404,
                detail=f"No students found in class {request.class_code}"
            )
        
        logger.info(f"Started lesson session {session_id} for class {request.class_code}")
        
        return LessonResponse(
            session_id=session_id,
            class_code=request.class_code,
            started_at=datetime.now().isoformat(),
            student_count=len(students),
            message=f"Lesson started for {len(students)} students"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting lesson: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start lesson: {str(e)}")


@router.post("/lesson/end")
async def end_lesson(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    End a lesson session
    
    Archives all logs for the session (already persisted in DB)
    Resets strike counters (handled client-side for next lesson)
    """
    try:
        # Count logs in this session
        log_count = db.query(func.count(QuickLog.id)).filter(
            QuickLog.lesson_session_id == session_id
        ).scalar()
        
        logger.info(f"Ended lesson session {session_id} with {log_count} logs")
        
        return {
            "session_id": session_id,
            "ended_at": datetime.now().isoformat(),
            "total_logs": log_count,
            "message": "Lesson ended successfully. Data archived."
        }
        
    except Exception as e:
        logger.error(f"Error ending lesson: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to end lesson: {str(e)}")


@router.post("/strike")
async def add_strike(
    request: StrikeRequest,
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Add a strike to a student with automatic consequence assignment
    """
    try:
        # Validate strike level
        if request.strike_level not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="Strike level must be 1, 2, or 3")
        
        # Validate student exists
        student = db.query(Student).filter(Student.id == request.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get consequence text
        consequence = STRIKE_CONSEQUENCES[request.strike_level]
        
        # Create quick log entry
        log = QuickLog(
            student_id=request.student_id,
            class_code=request.class_code,
            timestamp=datetime.now(),
            log_type="negative",
            category="behavior_strike",
            points=0,  # No house point deduction
            note=request.description,
            lesson_session_id=session_id,
            strike_level=request.strike_level,
            consequence_text=consequence,
            admin_notified=request.admin_notified,
            hod_consulted=request.hod_consulted,
            parent_meeting_scheduled=request.parent_meeting_scheduled
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        logger.info(f"Added strike {request.strike_level} for student {student.name} (ID: {request.student_id})")
        
        return {
            "log_id": log.id,
            "student_id": request.student_id,
            "student_name": student.name,
            "strike_level": request.strike_level,
            "consequence": consequence,
            "timestamp": log.timestamp.isoformat(),
            "session_id": session_id,
            "message": f"Strike {request.strike_level} recorded: {consequence}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding strike: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to add strike: {str(e)}")


@router.post("/positive")
async def add_positive_behavior(
    request: PositiveBehaviorRequest,
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Log positive behavior and award house points
    """
    try:
        # Validate student exists
        student = db.query(Student).filter(Student.id == request.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Create quick log entry
        log = QuickLog(
            student_id=request.student_id,
            class_code=request.class_code,
            timestamp=datetime.now(),
            log_type="positive",
            category="behavior_positive",
            points=request.house_points,
            note=request.description,
            lesson_session_id=session_id
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        logger.info(f"Added positive behavior for student {student.name}, +{request.house_points} house points")
        
        return {
            "log_id": log.id,
            "student_id": request.student_id,
            "student_name": student.name,
            "house": student.house,
            "house_points_awarded": request.house_points,
            "timestamp": log.timestamp.isoformat(),
            "message": f"Positive behavior logged. +{request.house_points} house points for {student.house}!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding positive behavior: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to log positive behavior: {str(e)}")


@router.get("/lesson/current")
async def get_current_lesson_state(
    session_id: str,
    class_code: str,
    db: Session = Depends(get_db)
):
    """
    Get current state of all students in the lesson
    
    Returns strike counts, history, and positive behavior for each student
    """
    try:
        # Get all students in class
        students = db.query(Student).filter(
            Student.class_code == class_code
        ).order_by(Student.name).all()
        
        if not students:
            raise HTTPException(status_code=404, detail="No students found in class")
        
        # Get all logs for this session
        session_logs = db.query(QuickLog).filter(
            QuickLog.lesson_session_id == session_id
        ).all()
        
        # Group logs by student
        logs_by_student = {}
        for log in session_logs:
            if log.student_id not in logs_by_student:
                logs_by_student[log.student_id] = []
            logs_by_student[log.student_id].append(log)
        
        # Build student states
        student_states = []
        for student in students:
            student_logs = logs_by_student.get(student.id, [])
            
            # Count strikes
            strikes = [log for log in student_logs if log.strike_level is not None]
            current_strikes = len(strikes)
            
            # Count positives
            positives = [log for log in student_logs if log.log_type == "positive"]
            positive_count = len(positives)
            
            # Sum house points
            total_house_points = sum(log.points for log in positives if log.points)
            
            # Format strike history
            strike_history = []
            for log in strikes:
                strike_history.append({
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "strike_level": log.strike_level,
                    "description": log.note,
                    "consequence": log.consequence_text,
                    "admin_notified": bool(log.admin_notified),
                    "hod_consulted": bool(log.hod_consulted),
                    "parent_meeting_scheduled": bool(log.parent_meeting_scheduled)
                })
            
            student_states.append(StudentLessonState(
                student_id=student.id,
                student_name=student.name,
                house=student.house,
                current_strikes=current_strikes,
                strike_history=strike_history,
                positive_count=positive_count,
                total_house_points=total_house_points
            ))
        
        return {
            "session_id": session_id,
            "class_code": class_code,
            "student_count": len(students),
            "students": [s.dict() for s in student_states]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lesson state: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get lesson state: {str(e)}")


@router.get("/history/{student_id}")
async def get_student_behavior_history(
    student_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get full behavior history for a student across all lessons
    """
    try:
        # Validate student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get all behavior logs (strikes and positives)
        logs = db.query(QuickLog).filter(
            QuickLog.student_id == student_id,
            QuickLog.category.in_(["behavior_strike", "behavior_positive"])
        ).order_by(desc(QuickLog.timestamp)).limit(limit).all()
        
        # Format history
        history = []
        for log in logs:
            entry = {
                "id": log.id,
                "date": log.timestamp.isoformat(),
                "type": log.log_type,
                "description": log.note,
                "lesson_session_id": log.lesson_session_id
            }
            
            if log.strike_level:
                entry["strike_level"] = log.strike_level
                entry["consequence"] = log.consequence_text
                entry["admin_notified"] = bool(log.admin_notified)
                entry["hod_consulted"] = bool(log.hod_consulted)
                entry["parent_meeting_scheduled"] = bool(log.parent_meeting_scheduled)
            
            if log.log_type == "positive":
                entry["house_points"] = log.points
            
            history.append(entry)
        
        return {
            "student_id": student_id,
            "student_name": student.name,
            "total_logs": len(history),
            "history": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.patch("/history/{log_id}")
async def update_behavior_log(
    log_id: int,
    admin_notified: Optional[bool] = None,
    hod_consulted: Optional[bool] = None,
    parent_meeting_scheduled: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Update administrative flags on a behavior log
    """
    try:
        log = db.query(QuickLog).filter(QuickLog.id == log_id).first()
        if not log:
            raise HTTPException(status_code=404, detail="Log entry not found")
        
        # Update flags
        if admin_notified is not None:
            log.admin_notified = admin_notified
        if hod_consulted is not None:
            log.hod_consulted = hod_consulted
        if parent_meeting_scheduled is not None:
            log.parent_meeting_scheduled = parent_meeting_scheduled
        
        db.commit()
        db.refresh(log)
        
        return {
            "log_id": log_id,
            "admin_notified": bool(log.admin_notified),
            "hod_consulted": bool(log.hod_consulted),
            "parent_meeting_scheduled": bool(log.parent_meeting_scheduled),
            "message": "Log updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update log: {str(e)}")
