"""
Students API endpoints
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.logging_config import get_logger

logger = get_logger("api.students")
router = APIRouter()


class StudentResponse(BaseModel):
    """Response model for student data"""
    id: int
    name: str
    photo_path: Optional[str]
    year_group: str
    class_code: str
    house: Optional[str]
    campus: str
    support_level: int
    support_notes: Optional[str]
    last_updated: str


class StudentDetailResponse(StudentResponse):
    """Extended student model with additional details"""
    logs: List[dict]
    assessments: List[dict]
    recent_logs_count: dict
    performance_trend: Optional[str]


class QuickLogCreate(BaseModel):
    """Model for creating a quick log entry"""
    student_id: int
    class_code: str
    log_type: str  # 'positive', 'negative', 'neutral'
    category: str
    points: int = 0
    note: Optional[str] = None


class QuickLogResponse(BaseModel):
    """Response model for quick log entries"""
    id: int
    student_id: int
    class_code: str
    timestamp: str
    log_type: str
    category: str
    points: int
    note: Optional[str]
    student_name: str


@router.get("/", response_model=List[StudentResponse])
async def get_students(
    class_code: Optional[str] = Query(None, description="Filter by class code"),
    year_group: Optional[str] = Query(None, description="Filter by year group"),
    campus: Optional[str] = Query(None, description="Filter by campus"),
    support_level: Optional[int] = Query(None, ge=0, le=3, description="Filter by support level"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """Get list of students with optional filters"""
    try:
        from ..models.database_models import Student
        
        query = db.query(Student)
        
        # Apply filters
        if class_code:
            query = query.filter(Student.class_code == class_code)
        if year_group:
            query = query.filter(Student.year_group == year_group)
        if campus:
            query = query.filter(Student.campus == campus)
        if support_level is not None:
            query = query.filter(Student.support_level == support_level)
        
        # Apply pagination
        students = query.offset(offset).limit(limit).all()
        
        results = []
        for student in students:
            results.append(StudentResponse(
                id=student.id,
                name=student.name,
                photo_path=student.photo_path,
                year_group=student.year_group,
                class_code=student.class_code,
                house=student.house,
                campus=student.campus,
                support_level=student.support_level,
                support_notes=student.support_notes,
                last_updated=student.last_updated.isoformat() if student.last_updated else ""
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting students: {e}")
        raise HTTPException(status_code=500, detail="Failed to get students")


@router.get("/{student_id}", response_model=StudentDetailResponse)
async def get_student_detail(
    student_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific student"""
    try:
        from ..models.database_models import Student, QuickLog, Assessment
        from datetime import datetime, timedelta
        
        # Get student
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get recent logs (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        logs = db.query(QuickLog).filter(
            QuickLog.student_id == student_id,
            QuickLog.timestamp >= thirty_days_ago
        ).order_by(QuickLog.timestamp.desc()).limit(20).all()
        
        # Get recent assessments
        assessments = db.query(Assessment).filter(
            Assessment.student_id == student_id
        ).order_by(Assessment.date.desc()).limit(10).all()
        
        # Count logs by type
        log_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for log in logs:
            log_counts[log.log_type] = log_counts.get(log.log_type, 0) + 1
        
        # Simple performance trend (based on recent assessments)
        performance_trend = None
        if len(assessments) >= 2:
            recent_avg = sum(a.percentage for a in assessments[:3]) / min(3, len(assessments))
            older_avg = sum(a.percentage for a in assessments[3:6]) / max(1, min(3, len(assessments) - 3))
            if recent_avg > older_avg + 5:
                performance_trend = "improving"
            elif recent_avg < older_avg - 5:
                performance_trend = "declining"
            else:
                performance_trend = "stable"
        
        # Format logs
        log_data = []
        for log in logs:
            log_data.append({
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "log_type": log.log_type,
                "category": log.category,
                "points": log.points,
                "note": log.note
            })
        
        # Format assessments
        assessment_data = []
        for assessment in assessments:
            assessment_data.append({
                "id": assessment.id,
                "assessment_type": assessment.assessment_type,
                "subject": assessment.subject,
                "topic": assessment.topic,
                "score": assessment.score,
                "max_score": assessment.max_score,
                "percentage": assessment.percentage,
                "date": assessment.date.isoformat(),
                "source": assessment.source
            })
        
        return StudentDetailResponse(
            id=student.id,
            name=student.name,
            photo_path=student.photo_path,
            year_group=student.year_group,
            class_code=student.class_code,
            house=student.house,
            campus=student.campus,
            support_level=student.support_level,
            support_notes=student.support_notes,
            last_updated=student.last_updated.isoformat() if student.last_updated else "",
            logs=log_data,
            assessments=assessment_data,
            recent_logs_count=log_counts,
            performance_trend=performance_trend
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student detail: {e}")
        raise HTTPException(status_code=500, detail="Failed to get student detail")


@router.post("/{student_id}/logs", response_model=QuickLogResponse)
async def create_quick_log(
    student_id: int,
    log_data: QuickLogCreate,
    db: Session = Depends(get_db)
):
    """Create a quick log entry for a student"""
    try:
        from ..models.database_models import QuickLog, Student
        
        # Verify student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Create log entry
        log = QuickLog(
            student_id=student_id,
            class_code=log_data.class_code,
            log_type=log_data.log_type,
            category=log_data.category,
            points=log_data.points,
            note=log_data.note
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return QuickLogResponse(
            id=log.id,
            student_id=log.student_id,
            class_code=log.class_code,
            timestamp=log.timestamp.isoformat(),
            log_type=log.log_type,
            category=log.category,
            points=log.points,
            note=log.note,
            student_name=student.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating quick log: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create quick log")


@router.get("/{student_id}/logs", response_model=List[QuickLogResponse])
async def get_student_logs(
    student_id: int,
    log_type: Optional[str] = Query(None, regex="^(positive|negative|neutral)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get logs for a specific student"""
    try:
        from ..models.database_models import QuickLog, Student
        
        # Verify student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        query = db.query(QuickLog).filter(QuickLog.student_id == student_id)
        
        if log_type:
            query = query.filter(QuickLog.log_type == log_type)
        
        logs = query.order_by(QuickLog.timestamp.desc()).offset(offset).limit(limit).all()
        
        results = []
        for log in logs:
            results.append(QuickLogResponse(
                id=log.id,
                student_id=log.student_id,
                class_code=log.class_code,
                timestamp=log.timestamp.isoformat(),
                log_type=log.log_type,
                category=log.category,
                points=log.points,
                note=log.note,
                student_name=student.name
            ))
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get student logs")


@router.get("/classes/list")
async def get_classes(
    db: Session = Depends(get_db)
):
    """Get list of all unique class codes"""
    try:
        from ..models.database_models import Student
        
        # Get unique class codes
        classes = db.query(Student.class_code).distinct().all()
        
        # Get student counts for each class
        class_data = []
        for class_code, in classes:
            student_count = db.query(Student).filter(Student.class_code == class_code).count()
            class_data.append({
                "class_code": class_code,
                "student_count": student_count
            })
        
        # Sort by class code
        class_data.sort(key=lambda x: x["class_code"])
        
        return {"classes": class_data}
        
    except Exception as e:
        logger.error(f"Error getting classes: {e}")
        raise HTTPException(status_code=500, detail="Failed to get classes")


@router.get("/support/high-needs")
async def get_high_support_students(
    min_level: int = Query(2, ge=1, le=3, description="Minimum support level"),
    db: Session = Depends(get_db)
):
    """Get students with high support needs"""
    try:
        from ..models.database_models import Student
        
        students = db.query(Student).filter(
            Student.support_level >= min_level
        ).order_by(Student.support_level.desc()).all()
        
        results = []
        for student in students:
            results.append({
                "id": student.id,
                "name": student.name,
                "class_code": student.class_code,
                "year_group": student.year_group,
                "campus": student.campus,
                "support_level": student.support_level,
                "support_notes": student.support_notes
            })
        
        return {"students": results, "total_count": len(results)}
        
    except Exception as e:
        logger.error(f"Error getting high support students: {e}")
        raise HTTPException(status_code=500, detail="Failed to get high support students")