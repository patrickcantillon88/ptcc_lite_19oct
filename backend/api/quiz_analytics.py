#!/usr/bin/env python3
"""
Quiz Analytics API for PTCC

Handles CSV uploads, processes quiz results, and provides analytics
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from pydantic import BaseModel
import pandas as pd
import io
import logging

from ..core.database import get_db
from ..core.logging_config import get_logger
from ..models.database_models import Student, Assessment

logger = get_logger("api.quiz_analytics")
router = APIRouter()


class QuizUploadResponse(BaseModel):
    """Response model for quiz upload"""
    success: bool
    records_processed: int
    records_inserted: int
    errors: List[str]
    warnings: List[str]
    quiz_name: str
    upload_date: str


class ProgressLevel(BaseModel):
    """Progress level classification"""
    level: str  # "Exceeding", "Meeting", "Working Towards"
    student_count: int
    percentage: float
    students: List[str]


@router.post("/upload", response_model=QuizUploadResponse)
async def upload_quiz_csv(
    file: UploadFile = File(...),
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    quiz_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Upload and process quiz CSV file
    
    Flexible format support:
    - Expects columns: Student Name (or similar), Score/Percentage
    - Automatically detects format and matches students
    """
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        logger.info(f"Processing quiz CSV: {file.filename}, {len(df)} rows")
        
        # Parse quiz date
        if quiz_date:
            try:
                quiz_date_obj = datetime.fromisoformat(quiz_date).date()
            except:
                quiz_date_obj = date.today()
        else:
            quiz_date_obj = date.today()
        
        # Process the CSV
        result = await _process_quiz_csv(
            df, 
            file.filename, 
            subject, 
            topic, 
            quiz_date_obj,
            db
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error uploading quiz CSV: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process quiz CSV: {str(e)}")


async def _process_quiz_csv(
    df: pd.DataFrame,
    filename: str,
    subject: Optional[str],
    topic: Optional[str],
    quiz_date: date,
    db: Session
) -> QuizUploadResponse:
    """Process quiz CSV and insert into database"""
    
    errors = []
    warnings = []
    records_processed = 0
    records_inserted = 0
    
    # Detect student name column
    name_column = _detect_name_column(df)
    if not name_column:
        raise ValueError("Could not detect student name column. Expected columns like 'Student Name', 'Name', etc.")
    
    # Detect score/percentage columns
    score_column, max_score_column, percentage_column = _detect_score_columns(df)
    if not (score_column or percentage_column):
        raise ValueError("Could not detect score/percentage column")
    
    # Get all students from database
    students = db.query(Student).all()
    student_lookup = {student.name.lower().strip(): student for student in students}
    
    # Process each row
    for idx, row in df.iterrows():
        records_processed += 1
        
        try:
            # Extract student name
            student_name = str(row[name_column]).strip()
            if not student_name or student_name.lower() in ['nan', 'none', '']:
                warnings.append(f"Row {idx + 2}: Empty student name")
                continue
            
            # Match student
            student = _match_student(student_name, student_lookup)
            if not student:
                warnings.append(f"Row {idx + 2}: Student '{student_name}' not found in roster")
                continue
            
            # Extract score data
            score = None
            max_score = 100.0  # Default
            percentage = None
            
            if score_column:
                try:
                    score = float(row[score_column])
                except:
                    pass
            
            if max_score_column:
                try:
                    max_score = float(row[max_score_column])
                except:
                    pass
            
            if percentage_column:
                try:
                    percentage = float(row[percentage_column])
                except:
                    pass
            
            # Calculate percentage if not provided
            if percentage is None and score is not None and max_score and max_score > 0:
                percentage = (score / max_score) * 100
            elif percentage is None and score is not None and score <= 100:
                # Assume score is already a percentage
                percentage = score
                max_score = 100.0
            
            if percentage is None:
                warnings.append(f"Row {idx + 2}: Could not determine percentage for {student_name}")
                continue
            
            # Ensure percentage is in valid range
            percentage = max(0, min(100, percentage))
            
            # Create assessment record
            assessment = Assessment(
                student_id=student.id,
                assessment_type="Quiz",
                subject=subject or "General",
                topic=topic or filename.replace('.csv', ''),
                score=score,
                max_score=max_score,
                percentage=percentage,
                date=quiz_date,
                source=filename
            )
            
            db.add(assessment)
            records_inserted += 1
            
        except Exception as e:
            errors.append(f"Row {idx + 2}: {str(e)}")
            continue
    
    # Commit all changes
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(f"Database error: {str(e)}")
    
    return QuizUploadResponse(
        success=True,
        records_processed=records_processed,
        records_inserted=records_inserted,
        errors=errors,
        warnings=warnings,
        quiz_name=filename.replace('.csv', ''),
        upload_date=datetime.now().isoformat()
    )


def _detect_name_column(df: pd.DataFrame) -> Optional[str]:
    """Detect which column contains student names"""
    name_indicators = [
        "student name", "name", "student", "full name", 
        "participant", "learner", "pupil"
    ]
    
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if any(indicator in col_lower for indicator in name_indicators):
            return col
    
    # Fallback: first column if it looks like names
    if len(df) > 0:
        first_col = df.columns[0]
        # Check if first column contains text that looks like names
        sample = str(df[first_col].iloc[0])
        if len(sample.split()) >= 2:  # Likely a name (has spaces)
            return first_col
    
    return None


def _detect_score_columns(df: pd.DataFrame) -> tuple:
    """Detect score, max_score, and percentage columns"""
    score_col = None
    max_score_col = None
    percentage_col = None
    
    for col in df.columns:
        col_lower = str(col).lower().strip()
        
        # Percentage indicators
        if any(indicator in col_lower for indicator in ["percentage", "percent", "%", "accuracy"]):
            percentage_col = col
        
        # Score indicators
        elif any(indicator in col_lower for indicator in ["score", "points", "mark", "total score"]):
            if "max" not in col_lower:
                score_col = col
        
        # Max score indicators
        elif any(indicator in col_lower for indicator in ["max score", "maximum", "out of"]):
            max_score_col = col
    
    return score_col, max_score_col, percentage_col


def _match_student(student_name: str, student_lookup: Dict[str, Student]) -> Optional[Student]:
    """Match student name to database using exact and fuzzy matching"""
    # Try exact match first
    student_key = student_name.lower().strip()
    if student_key in student_lookup:
        return student_lookup[student_key]
    
    # Try fuzzy matching
    from difflib import SequenceMatcher
    
    best_match = None
    best_ratio = 0.0
    
    for db_name, student in student_lookup.items():
        ratio = SequenceMatcher(None, student_key, db_name).ratio()
        if ratio > best_ratio and ratio > 0.8:  # 80% similarity threshold
            best_ratio = ratio
            best_match = student
    
    return best_match


@router.get("/analytics/overview")
async def get_quiz_analytics_overview(
    subject: Optional[str] = None,
    class_code: Optional[str] = None,
    days: int = 90,
    db: Session = Depends(get_db)
):
    """Get overall quiz analytics"""
    try:
        # Build query
        query = db.query(Assessment).filter(
            Assessment.assessment_type == "Quiz",
            Assessment.date >= (date.today() - timedelta(days=days))
        )
        
        if subject:
            query = query.filter(Assessment.subject == subject)
        
        if class_code:
            query = query.join(Student).filter(Student.class_code == class_code)
        
        assessments = query.all()
        
        if not assessments:
            return {
                "total_quizzes": 0,
                "total_attempts": 0,
                "average_score": 0,
                "message": "No quiz data found"
            }
        
        # Calculate statistics
        percentages = [a.percentage for a in assessments if a.percentage is not None]
        
        return {
            "total_quizzes": len(set(a.topic for a in assessments)),
            "total_attempts": len(assessments),
            "average_score": round(sum(percentages) / len(percentages), 2) if percentages else 0,
            "highest_score": max(percentages) if percentages else 0,
            "lowest_score": min(percentages) if percentages else 0,
            "date_range": {
                "start": (date.today() - timedelta(days=days)).isoformat(),
                "end": date.today().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching quiz analytics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/student-trends")
async def get_student_quiz_trends(
    subject: Optional[str] = None,
    class_code: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get student performance trends"""
    try:
        # Build query
        query = db.query(
            Student.id,
            Student.name,
            Student.class_code,
            func.count(Assessment.id).label('quiz_count'),
            func.avg(Assessment.percentage).label('avg_percentage'),
            func.min(Assessment.percentage).label('min_percentage'),
            func.max(Assessment.percentage).label('max_percentage')
        ).join(Assessment).filter(
            Assessment.assessment_type == "Quiz"
        ).group_by(Student.id, Student.name, Student.class_code)
        
        if subject:
            query = query.filter(Assessment.subject == subject)
        
        if class_code:
            query = query.filter(Student.class_code == class_code)
        
        results = query.order_by(desc('avg_percentage')).limit(limit).all()
        
        student_trends = []
        for result in results:
            # Get recent trend
            recent_assessments = db.query(Assessment).filter(
                Assessment.student_id == result.id,
                Assessment.assessment_type == "Quiz"
            ).order_by(desc(Assessment.date)).limit(5).all()
            
            recent_scores = [a.percentage for a in recent_assessments if a.percentage is not None]
            
            # Determine trend
            if len(recent_scores) >= 2:
                if recent_scores[0] > recent_scores[-1] + 5:
                    trend = "improving"
                elif recent_scores[0] < recent_scores[-1] - 5:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            # Classify progress level
            avg_pct = float(result.avg_percentage)
            if avg_pct >= 85:
                progress_level = "Exceeding"
            elif avg_pct >= 70:
                progress_level = "Meeting"
            else:
                progress_level = "Working Towards"
            
            student_trends.append({
                "student_id": result.id,
                "student_name": result.name,
                "class_code": result.class_code,
                "quiz_count": result.quiz_count,
                "average_percentage": round(float(result.avg_percentage), 2),
                "score_range": {
                    "min": float(result.min_percentage),
                    "max": float(result.max_percentage)
                },
                "progress_level": progress_level,
                "trend": trend,
                "recent_scores": recent_scores
            })
        
        return {"students": student_trends, "total": len(student_trends)}
        
    except Exception as e:
        logger.error(f"Error fetching student trends: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/progress-levels")
async def get_progress_level_distribution(
    subject: Optional[str] = None,
    class_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get distribution of students across progress levels"""
    try:
        # Get average performance for each student
        query = db.query(
            Student.id,
            Student.name,
            func.avg(Assessment.percentage).label('avg_percentage')
        ).join(Assessment).filter(
            Assessment.assessment_type == "Quiz"
        ).group_by(Student.id, Student.name)
        
        if subject:
            query = query.filter(Assessment.subject == subject)
        
        if class_code:
            query = query.filter(Student.class_code == class_code)
        
        results = query.all()
        
        # Classify into progress levels
        exceeding = []
        meeting = []
        working_towards = []
        
        for result in results:
            avg_pct = float(result.avg_percentage)
            if avg_pct >= 85:
                exceeding.append(result.name)
            elif avg_pct >= 70:
                meeting.append(result.name)
            else:
                working_towards.append(result.name)
        
        total = len(results)
        
        return {
            "exceeding": {
                "count": len(exceeding),
                "percentage": round((len(exceeding) / total * 100), 2) if total > 0 else 0,
                "students": exceeding
            },
            "meeting": {
                "count": len(meeting),
                "percentage": round((len(meeting) / total * 100), 2) if total > 0 else 0,
                "students": meeting
            },
            "working_towards": {
                "count": len(working_towards),
                "percentage": round((len(working_towards) / total * 100), 2) if total > 0 else 0,
                "students": working_towards
            },
            "total_students": total
        }
        
    except Exception as e:
        logger.error(f"Error fetching progress levels: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/at-risk")
async def get_at_risk_students(
    threshold: float = 60.0,
    min_quizzes: int = 2,
    db: Session = Depends(get_db)
):
    """Identify students at risk (low or declining performance)"""
    try:
        # Get students with recent quiz data
        students = db.query(Student).all()
        
        at_risk_students = []
        
        for student in students:
            # Get recent assessments
            recent_assessments = db.query(Assessment).filter(
                Assessment.student_id == student.id,
                Assessment.assessment_type == "Quiz"
            ).order_by(desc(Assessment.date)).limit(5).all()
            
            if len(recent_assessments) < min_quizzes:
                continue
            
            recent_scores = [a.percentage for a in recent_assessments if a.percentage is not None]
            if not recent_scores:
                continue
            
            avg_score = sum(recent_scores) / len(recent_scores)
            
            # Check if declining
            declining = False
            if len(recent_scores) >= 3:
                if recent_scores[0] < recent_scores[-1] - 10:
                    declining = True
            
            # Flag if below threshold or declining
            if avg_score < threshold or declining:
                at_risk_students.append({
                    "student_id": student.id,
                    "student_name": student.name,
                    "class_code": student.class_code,
                    "average_score": round(avg_score, 2),
                    "recent_scores": recent_scores,
                    "reason": "declining_performance" if declining else "low_performance",
                    "quiz_count": len(recent_scores)
                })
        
        # Sort by average score (lowest first)
        at_risk_students.sort(key=lambda x: x['average_score'])
        
        return {
            "at_risk_count": len(at_risk_students),
            "students": at_risk_students,
            "threshold_used": threshold
        }
        
    except Exception as e:
        logger.error(f"Error fetching at-risk students: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
