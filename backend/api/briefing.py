"""
Briefing API endpoints
"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.briefing_engine import generate_daily_briefing, format_briefing_text
from ..models.database_models import ClassRoster
from ..core.database import get_db
from ..core.logging_config import get_logger

logger = get_logger("api.briefing")
router = APIRouter()


class BriefingResponse(BaseModel):
    """Response model for briefing data"""
    date: str
    day_name: str
    schedule: list
    student_alerts: dict
    duty_assignments: list
    reminders: list
    communications: list
    insights: list
    metadata: dict


@router.get("/today")
async def get_today_briefing(
    format: Optional[str] = Query("json", regex="^(json|text)$"),
    db: Session = Depends(get_db)
):
    """Get today's briefing"""
    try:
        briefing_date = date.today()
        briefing = generate_daily_briefing(briefing_date)

        if format == "text":
            # Return text format without validation
            return {"text": format_briefing_text(briefing)}
        else:
            return briefing.to_dict()

    except Exception as e:
        logger.error(f"Error generating briefing: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate briefing")


@router.get("/date/{briefing_date}", response_model=BriefingResponse)
async def get_briefing_by_date(
    briefing_date: str,
    format: Optional[str] = Query("json", regex="^(json|text)$"),
    db: Session = Depends(get_db)
):
    """Get briefing for a specific date"""
    try:
        # Parse date from string
        try:
            parsed_date = datetime.strptime(briefing_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        briefing = generate_daily_briefing(parsed_date)
        
        if format == "text":
            return {"text": format_briefing_text(briefing)}
        else:
            return briefing.to_dict()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating briefing for date {briefing_date}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate briefing")


@router.get("/schedule/{day}")
async def get_schedule_for_day(
    day: str,
    db: Session = Depends(get_db)
):
    """Get schedule for a specific day of the week"""
    try:
        from ..models.database_models import Schedule
        
        schedule = db.query(Schedule).filter(
            Schedule.day_of_week == day.capitalize()
        ).order_by(Schedule.period).all()
        
        if not schedule:
            return {"schedule": [], "message": f"No schedule found for {day}"}
        
        result = []
        for entry in schedule:
            result.append({
                "period": entry.period,
                "start_time": entry.start_time,
                "end_time": entry.end_time,
                "class_code": entry.class_code,
                "subject": entry.subject,
                "room": entry.room
            })
        
        return {"day": day.capitalize(), "schedule": result}
        
    except Exception as e:
        logger.error(f"Error getting schedule for {day}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get schedule")


@router.get("/insights")
async def get_insights(
    days: Optional[int] = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get insights for the last N days"""
    try:
        from datetime import timedelta
        from ..models.database_models import QuickLog, Student
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get recent logs
        recent_logs = db.query(QuickLog).filter(
            QuickLog.timestamp >= datetime.combine(start_date, datetime.min.time())
        ).all()
        
        # Get student counts
        total_students = db.query(Student).count()
        high_support_students = db.query(Student).filter(Student.support_level >= 2).count()
        
        # Analyze logs
        positive_logs = len([log for log in recent_logs if log.log_type == "positive"])
        negative_logs = len([log for log in recent_logs if log.log_type == "negative"])
        neutral_logs = len([log for log in recent_logs if log.log_type == "neutral"])
        
        # Calculate insights
        insights = []
        if negative_logs > positive_logs * 2:
            insights.append("Higher than usual negative incidents detected")
        if high_support_students > 0:
            insights.append(f"{high_support_students} high-support students need attention")
        if total_students > 0:
            interaction_rate = len(recent_logs) / total_students
            if interaction_rate < 0.5:
                insights.append("Low student interaction rate detected")
        
        return {
            "period": f"Last {days} days",
            "total_logs": len(recent_logs),
            "positive_logs": positive_logs,
            "negative_logs": negative_logs,
            "neutral_logs": neutral_logs,
            "total_students": total_students,
            "high_support_students": high_support_students,
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights")