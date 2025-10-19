"""
PTCC Lite API Endpoints

Core features:
- GET /api/lite/classes - List all classes
- GET /api/lite/class/{class_code} - Class roster with student data
- POST /api/lite/incident - Log an incident
- GET /api/lite/incidents - Get incidents by student/class/time
- GET /api/lite/patterns/weekly - Weekly incident patterns
- GET /api/lite/briefing/{class_code} - Pre-lesson briefing
"""

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json

from ..core.database import SessionLocal
from ..models.database_models import Student, QuickLog, Assessment, Timetable

router = APIRouter(prefix="/api/lite", tags=["lite"])


@router.get("/classes")
def get_all_classes():
    """Get list of YOUR ICT classes (from timetable)"""
    db = SessionLocal()
    try:
        # Get only classes YOU teach (from timetable where subject='ICT')
        your_classes = db.query(Timetable.class_code).filter(
            Timetable.subject.ilike('%ICT%')
        ).distinct().all()
        class_list = sorted([c[0] for c in your_classes if c[0]])
        return {"classes": class_list, "count": len(class_list)}
    finally:
        db.close()


@router.get("/class/{class_code}")
def get_class_roster(class_code: str):
    """Get full roster for a class with student data"""
    db = SessionLocal()
    try:
        students = db.query(Student).filter_by(class_code=class_code).all()
        
        roster = []
        for student in students:
            # Parse CAT4 data from support_notes
            support_data = {}
            if student.support_notes:
                try:
                    support_data = json.loads(student.support_notes)
                except:
                    pass
            
            # Get latest assessment
            latest_assessment = db.query(Assessment).filter_by(student_id=student.id).order_by(Assessment.date.desc()).first()
            latest_score = None
            if latest_assessment:
                latest_score = {
                    "topic": latest_assessment.topic,
                    "percentage": latest_assessment.percentage,
                    "date": latest_assessment.date.isoformat()
                }
            
            # Get incident count this week
            week_ago = datetime.now() - timedelta(days=7)
            incident_count = db.query(QuickLog).filter(
                QuickLog.student_id == student.id,
                QuickLog.timestamp >= week_ago
            ).count()
            
            roster.append({
                "id": student.id,
                "name": student.name,
                "year_group": student.year_group,
                "class_code": student.class_code,
                "house": student.house,
                "support_level": student.support_level,
                "cat4_data": {
                    "verbal": support_data.get('cat4_verbal'),
                    "quantitative": support_data.get('cat4_quantitative'),
                    "nonverbal": support_data.get('cat4_nonverbal'),
                    "spatial": support_data.get('cat4_spatial'),
                    "mean": support_data.get('cat4_mean'),
                },
                "flags": {
                    "ls": support_data.get('ls_flag'),
                    "eal": support_data.get('eal_flag'),
                    "eal_tier": support_data.get('eal_tier'),
                },
                "latest_assessment": latest_score,
                "incidents_this_week": incident_count,
            })
        
        return {
            "class_code": class_code,
            "student_count": len(roster),
            "students": sorted(roster, key=lambda x: x['name'])
        }
    finally:
        db.close()


@router.post("/incident")
def log_incident(
    student_id: int,
    class_code: str,
    log_type: str,  # 'positive', 'negative', 'neutral'
    category: str,  # 'excellent_contribution', 'off_task', etc.
    note: Optional[str] = None,
    points: int = 0
):
    """Log an incident for a student"""
    db = SessionLocal()
    try:
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        incident = QuickLog(
            student_id=student_id,
            class_code=class_code,
            timestamp=datetime.now(),
            log_type=log_type,
            category=category,
            note=note,
            points=points,
        )
        db.add(incident)
        db.commit()
        
        return {
            "success": True,
            "incident_id": incident.id,
            "student": student.name,
            "timestamp": incident.timestamp.isoformat()
        }
    finally:
        db.close()


@router.get("/incidents")
def get_incidents(
    student_id: Optional[int] = None,
    class_code: Optional[str] = None,
    days: int = 7,
    log_type: Optional[str] = None
):
    """Get incidents filtered by student, class, time, and type"""
    db = SessionLocal()
    try:
        time_ago = datetime.now() - timedelta(days=days)
        query = db.query(QuickLog).filter(QuickLog.timestamp >= time_ago)
        
        if student_id:
            query = query.filter_by(student_id=student_id)
        if class_code:
            query = query.filter_by(class_code=class_code)
        if log_type:
            query = query.filter_by(log_type=log_type)
        
        incidents = query.order_by(QuickLog.timestamp.desc()).all()
        
        result = []
        for incident in incidents:
            student = db.query(Student).filter_by(id=incident.student_id).first()
            result.append({
                "id": incident.id,
                "student_name": student.name if student else "Unknown",
                "student_id": incident.student_id,
                "class_code": incident.class_code,
                "type": incident.log_type,
                "category": incident.category,
                "note": incident.note,
                "points": incident.points,
                "timestamp": incident.timestamp.isoformat(),
            })
        
        return {
            "count": len(result),
            "days": days,
            "incidents": result
        }
    finally:
        db.close()


@router.get("/patterns/weekly")
def get_weekly_patterns(class_code: Optional[str] = None):
    """Get weekly incident patterns"""
    db = SessionLocal()
    try:
        week_ago = datetime.now() - timedelta(days=7)
        query = db.query(QuickLog).filter(QuickLog.timestamp >= week_ago)
        
        if class_code:
            query = query.filter_by(class_code=class_code)
        
        incidents = query.all()
        
        # Count by student
        student_incidents: Dict[int, int] = {}
        negative_by_student: Dict[int, int] = {}
        
        for incident in incidents:
            student_incidents[incident.student_id] = student_incidents.get(incident.student_id, 0) + 1
            if incident.log_type == 'negative':
                negative_by_student[incident.student_id] = negative_by_student.get(incident.student_id, 0) + 1
        
        # Build response
        patterns = []
        for student_id, count in sorted(student_incidents.items(), key=lambda x: x[1], reverse=True):
            student = db.query(Student).filter_by(id=student_id).first()
            patterns.append({
                "student_id": student_id,
                "student_name": student.name if student else "Unknown",
                "total_incidents": count,
                "negative_incidents": negative_by_student.get(student_id, 0),
                "positive_incidents": count - negative_by_student.get(student_id, 0),
                "trend": "concerning" if negative_by_student.get(student_id, 0) > count / 2 else "stable"
            })
        
        return {
            "period": "7_days",
            "total_incidents": len(incidents),
            "student_count": len(student_incidents),
            "patterns": patterns
        }
    finally:
        db.close()


@router.get("/briefing/{class_code}")
def get_pre_lesson_briefing(class_code: str):
    """Get pre-lesson briefing for a class"""
    db = SessionLocal()
    try:
        # Get students
        students = db.query(Student).filter_by(class_code=class_code).all()
        
        week_ago = datetime.now() - timedelta(days=7)
        
        # Collect data
        briefing = {
            "class_code": class_code,
            "student_count": len(students),
            "last_week_incidents": [],
            "at_risk_students": [],
            "high_performers": [],
            "cca_participation": []
        }
        
        for student in students:
            # Last week incidents
            incidents = db.query(QuickLog).filter(
                QuickLog.student_id == student.id,
                QuickLog.timestamp >= week_ago
            ).all()
            
            if len(incidents) > 3:
                briefing["last_week_incidents"].append({
                    "student_name": student.name,
                    "count": len(incidents),
                    "types": [i.log_type for i in incidents[-3:]]
                })
            
            # At-risk (high negative incident count)
            negative_count = sum(1 for i in incidents if i.log_type == 'negative')
            if negative_count >= 2:
                briefing["at_risk_students"].append({
                    "student_name": student.name,
                    "negative_incidents": negative_count,
                    "support_level": student.support_level,
                    "support_notes": student.support_notes[:100] if student.support_notes else None
                })
            
            # High performers (high assessment scores)
            latest_assessment = db.query(Assessment).filter_by(student_id=student.id).order_by(Assessment.date.desc()).first()
            if latest_assessment and latest_assessment.percentage >= 85:
                briefing["high_performers"].append({
                    "student_name": student.name,
                    "topic": latest_assessment.topic,
                    "percentage": latest_assessment.percentage
                })
        
        # Sort
        briefing["last_week_incidents"].sort(key=lambda x: x['count'], reverse=True)
        briefing["at_risk_students"].sort(key=lambda x: x['negative_incidents'], reverse=True)
        
        return briefing
    finally:
        db.close()


@router.get("/health")
def health_check():
    """Health check endpoint"""
    db = SessionLocal()
    try:
        student_count = db.query(Student).count()
        incident_count = db.query(QuickLog).count()
        assessment_count = db.query(Assessment).count()
        
        return {
            "status": "healthy",
            "database": {
                "students": student_count,
                "incidents": incident_count,
                "assessments": assessment_count
            }
        }
    finally:
        db.close()
