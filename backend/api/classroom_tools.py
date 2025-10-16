#!/usr/bin/env python3
"""
Classroom Management Tools API for PTCC

Data-driven classroom management tools for teachers.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..core.database import get_db
from ..core.logging_config import get_logger
from ..models.database_models import Student, QuickLog, Assessment

logger = get_logger("api.classroom_tools")
router = APIRouter()


class InterventionStudent(BaseModel):
    """Model for intervention priority student"""
    student_id: int
    student_name: str
    class_code: str
    priority_score: float
    risk_factors: List[str]
    recommended_actions: List[str]
    days_since_positive: Optional[int]
    recent_incidents: int
    assessment_trend: Optional[str]
    support_level: int


@router.get("/intervention-priority")
async def get_intervention_priority_list(
    class_code: Optional[str] = None,
    limit: int = 20,
    behavior_type: str = "all",  # all, classroom, cca
    db: Session = Depends(get_db)
):
    """
    Get prioritized list of students needing intervention.
    
    Analyzes:
    - Behavior patterns from quick_logs
    - Assessment trends
    - Support level changes
    - Days since last positive interaction
    - Multiple risk factors
    
    Can filter by behavior_type: all, classroom, cca
    
    Returns ranked list with action items.
    """
    try:
        # Get all students or filter by class
        query = db.query(Student)
        if class_code:
            query = query.filter(Student.class_code == class_code)
        students = query.all()
        
        intervention_list = []
        current_date = datetime.now()
        
        for student in students:
            # Calculate risk factors
            risk_factors = []
            recommended_actions = []
            priority_score = 0.0
            
            # 1. Check behavior logs (last 30 days)
            thirty_days_ago = current_date - timedelta(days=30)
            recent_logs_query = db.query(QuickLog).filter(
                QuickLog.student_id == student.id,
                QuickLog.timestamp >= thirty_days_ago
            )
            
            # Apply behavior_type filter
            if behavior_type == "classroom":
                recent_logs_query = recent_logs_query.filter(QuickLog.cca_subject.is_(None))
            elif behavior_type == "cca":
                recent_logs_query = recent_logs_query.filter(QuickLog.cca_subject.isnot(None))
            
            recent_logs = recent_logs_query.all()
            
            negative_count = sum(1 for log in recent_logs if log.log_type in ['negative', 'incident'])
            positive_count = sum(1 for log in recent_logs if log.log_type == 'positive')
            
            if negative_count > 3:
                risk_factors.append(f"{negative_count} negative incidents in 30 days")
                recommended_actions.append("Schedule behavior intervention meeting")
                priority_score += negative_count * 2
            
            # 2. Days since last positive interaction
            positive_logs_query = db.query(QuickLog).filter(
                QuickLog.student_id == student.id,
                QuickLog.log_type == 'positive'
            )
            
            # Apply behavior_type filter
            if behavior_type == "classroom":
                positive_logs_query = positive_logs_query.filter(QuickLog.cca_subject.is_(None))
            elif behavior_type == "cca":
                positive_logs_query = positive_logs_query.filter(QuickLog.cca_subject.isnot(None))
            
            positive_logs = positive_logs_query.order_by(desc(QuickLog.timestamp)).first()
            
            days_since_positive = None
            if positive_logs:
                days_since_positive = (current_date - positive_logs.timestamp).days
                if days_since_positive > 14:
                    risk_factors.append(f"{days_since_positive} days since positive interaction")
                    recommended_actions.append("Catch student doing something right")
                    priority_score += days_since_positive * 0.5
            else:
                days_since_positive = 999
                risk_factors.append("No positive interactions recorded")
                recommended_actions.append("Build positive relationship")
                priority_score += 20
            
            # 3. Assessment trends (last 5 assessments)
            recent_assessments = db.query(Assessment).filter(
                Assessment.student_id == student.id
            ).order_by(desc(Assessment.date)).limit(5).all()
            
            assessment_trend = None
            if len(recent_assessments) >= 3:
                scores = [a.percentage for a in reversed(recent_assessments) if a.percentage is not None]
                if len(scores) >= 3:
                    # Simple trend analysis
                    if scores[-1] < scores[0] - 10:
                        assessment_trend = "declining"
                        risk_factors.append("Assessment scores declining")
                        recommended_actions.append("Review learning strategies")
                        priority_score += 15
                    elif all(s < 50 for s in scores[-3:]):
                        assessment_trend = "consistently_low"
                        risk_factors.append("Consistently low assessment scores")
                        recommended_actions.append("Academic intervention needed")
                        priority_score += 20
            
            # 4. Support level
            if student.support_level >= 2:
                risk_factors.append(f"High support level ({student.support_level})")
                recommended_actions.append("Review support strategies")
                priority_score += student.support_level * 5
            
            # 5. Performance trend indicator (computed from assessment trend above)
            # Note: performance_trend is not stored in DB, we use assessment_trend instead
            if assessment_trend == 'declining':
                # Already added to risk_factors above
                pass
            
            # 6. Check for multiple concurrent issues
            if len(risk_factors) >= 3:
                risk_factors.append("Multiple concurrent issues")
                recommended_actions.insert(0, "URGENT: Coordinate comprehensive intervention")
                priority_score += 25
            
            # Only include students with risk factors
            if risk_factors:
                intervention_list.append(InterventionStudent(
                    student_id=student.id,
                    student_name=student.name,
                    class_code=student.class_code,
                    priority_score=priority_score,
                    risk_factors=risk_factors,
                    recommended_actions=list(set(recommended_actions)),  # Remove duplicates
                    days_since_positive=days_since_positive if days_since_positive != 999 else None,
                    recent_incidents=negative_count,
                    assessment_trend=assessment_trend,
                    support_level=student.support_level
                ))
        
        # Sort by priority score (highest first)
        intervention_list.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Limit results
        intervention_list = intervention_list[:limit]
        
        return {
            "students": [s.dict() for s in intervention_list],
            "total_count": len(intervention_list),
            "filtered_by_class": class_code,
            "behavior_type": behavior_type,
            "analysis_date": current_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating intervention priority list: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate intervention list: {str(e)}")


@router.get("/classes")
async def get_available_classes(db: Session = Depends(get_db)):
    """Get list of all available classes"""
    try:
        classes = db.query(Student.class_code).distinct().order_by(Student.class_code).all()
        return {
            "classes": [c[0] for c in classes if c[0]],
            "total": len(classes)
        }
    except Exception as e:
        logger.error(f"Error fetching classes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress-dashboard")
async def get_progress_dashboard(
    class_code: Optional[str] = None,
    days: int = 30,
    behavior_type: str = "all",  # all, classroom, cca
    db: Session = Depends(get_db)
):
    """
    Get progress dashboard data showing trends over time.
    
    Analyzes:
    - Behavior trends (positive/negative logs over time)
    - Assessment score trends
    - Support level distribution
    - Class-level statistics
    
    Can filter by behavior_type: all, classroom, cca
    
    Returns data suitable for visualization.
    """
    try:
        from collections import defaultdict
        
        # Get students
        query = db.query(Student)
        if class_code:
            query = query.filter(Student.class_code == class_code)
        students = query.all()
        
        if not students:
            return {
                "error": "No students found",
                "class_code": class_code
            }
        
        student_ids = [s.id for s in students]
        
        # Time range
        start_date = datetime.now() - timedelta(days=days)
        
        # 1. Behavior trends over time
        logs_query = db.query(QuickLog).filter(
            QuickLog.student_id.in_(student_ids),
            QuickLog.timestamp >= start_date
        )
        
        # Apply behavior_type filter
        if behavior_type == "classroom":
            logs_query = logs_query.filter(QuickLog.cca_subject.is_(None))
        elif behavior_type == "cca":
            logs_query = logs_query.filter(QuickLog.cca_subject.isnot(None))
        # else: "all" - no additional filter
        
        logs = logs_query.order_by(QuickLog.timestamp).all()
        
        # Group logs by date and type
        behavior_by_date = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0})
        for log in logs:
            date_key = log.timestamp.date().isoformat()
            behavior_by_date[date_key][log.log_type] += 1
        
        behavior_trend = [
            {
                "date": date,
                "positive": counts["positive"],
                "negative": counts["negative"],
                "neutral": counts["neutral"]
            }
            for date, counts in sorted(behavior_by_date.items())
        ]
        
        # 2. Assessment trends
        assessments = db.query(Assessment).filter(
            Assessment.student_id.in_(student_ids),
            Assessment.date >= start_date.date()
        ).order_by(Assessment.date).all()
        
        # Group assessments by date and subject
        assessments_by_date = defaultdict(lambda: defaultdict(list))
        for assessment in assessments:
            if assessment.percentage is not None:
                date_key = assessment.date.isoformat()
                subject = assessment.subject or "General"
                assessments_by_date[date_key][subject].append(assessment.percentage)
        
        assessment_trend = []
        for date, subjects in sorted(assessments_by_date.items()):
            entry = {"date": date}
            for subject, scores in subjects.items():
                entry[subject] = sum(scores) / len(scores) if scores else 0
            assessment_trend.append(entry)
        
        # 3. Support level distribution
        support_distribution = defaultdict(int)
        for student in students:
            support_distribution[student.support_level] += 1
        
        # 4. Individual student progress (top performers and those needing support)
        student_summaries = []
        for student in students:
            # Get student's recent logs
            student_logs = [log for log in logs if log.student_id == student.id]
            positive_count = sum(1 for log in student_logs if log.log_type == "positive")
            negative_count = sum(1 for log in student_logs if log.log_type == "negative")
            
            # Get student's recent assessments
            student_assessments = [a for a in assessments if a.student_id == student.id]
            avg_score = None
            if student_assessments:
                scores = [a.percentage for a in student_assessments if a.percentage is not None]
                if scores:
                    avg_score = sum(scores) / len(scores)
            
            student_summaries.append({
                "student_id": student.id,
                "student_name": student.name,
                "class_code": student.class_code,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "net_behavior": positive_count - negative_count,
                "average_score": round(avg_score, 1) if avg_score else None,
                "support_level": student.support_level
            })
        
        # Sort by net behavior (for highlighting)
        student_summaries.sort(key=lambda x: x["net_behavior"], reverse=True)
        
        # 5. Class-level statistics
        total_positive = sum(1 for log in logs if log.log_type == "positive")
        total_negative = sum(1 for log in logs if log.log_type == "negative")
        total_assessments = len(assessments)
        avg_class_score = None
        if assessments:
            scores = [a.percentage for a in assessments if a.percentage is not None]
            if scores:
                avg_class_score = sum(scores) / len(scores)
        
        return {
            "class_code": class_code or "All Classes",
            "behavior_type": behavior_type,
            "student_count": len(students),
            "date_range": {
                "start": start_date.date().isoformat(),
                "end": datetime.now().date().isoformat(),
                "days": days
            },
            "summary": {
                "total_positive_logs": total_positive,
                "total_negative_logs": total_negative,
                "net_behavior_score": total_positive - total_negative,
                "total_assessments": total_assessments,
                "average_class_score": round(avg_class_score, 1) if avg_class_score else None
            },
            "behavior_trend": behavior_trend,
            "assessment_trend": assessment_trend,
            "support_distribution": dict(support_distribution),
            "student_summaries": student_summaries,
            "top_performers": student_summaries[:5],
            "needs_attention": [s for s in student_summaries if s["net_behavior"] < -3][:5]
        }
        
    except Exception as e:
        logger.error(f"Error generating progress dashboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")


@router.get("/group-formation")
async def get_group_formation_suggestions(
    class_code: str,
    group_size: int = 4,
    strategy: str = "mixed_ability",
    db: Session = Depends(get_db)
):
    """
    Generate optimal student groupings based on various strategies.
    
    Strategies:
    - mixed_ability: Mix high and low performers
    - similar_ability: Group similar performers together
    - behavioral_balance: Minimize behavior conflicts
    - support_aware: Distribute support needs evenly
    
    Returns suggested groups with rationale.
    """
    try:
        import random
        from collections import defaultdict
        
        # Get students in class
        students = db.query(Student).filter(Student.class_code == class_code).all()
        
        if not students:
            raise HTTPException(status_code=404, detail="No students found in class")
        
        if len(students) < group_size:
            raise HTTPException(status_code=400, detail="Not enough students for requested group size")
        
        # Get recent data for each student
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        student_profiles = []
        for student in students:
            # Get behavior data
            logs = db.query(QuickLog).filter(
                QuickLog.student_id == student.id,
                QuickLog.timestamp >= thirty_days_ago
            ).all()
            
            positive_count = sum(1 for log in logs if log.log_type == "positive")
            negative_count = sum(1 for log in logs if log.log_type == "negative")
            behavior_score = positive_count - negative_count
            
            # Get assessment data
            assessments = db.query(Assessment).filter(
                Assessment.student_id == student.id
            ).order_by(desc(Assessment.date)).limit(5).all()
            
            avg_score = None
            if assessments:
                scores = [a.percentage for a in assessments if a.percentage is not None]
                if scores:
                    avg_score = sum(scores) / len(scores)
            
            student_profiles.append({
                "id": student.id,
                "name": student.name,
                "support_level": student.support_level,
                "behavior_score": behavior_score,
                "avg_assessment_score": avg_score or 50.0,  # Default if no data
                "positive_count": positive_count,
                "negative_count": negative_count
            })
        
        # Sort students based on strategy
        if strategy == "mixed_ability":
            # Sort by assessment score
            student_profiles.sort(key=lambda x: x["avg_assessment_score"], reverse=True)
            
            # Create groups by snake draft
            num_groups = len(students) // group_size
            groups = [[] for _ in range(num_groups)]
            
            for i, student in enumerate(student_profiles[:num_groups * group_size]):
                group_idx = i % num_groups if (i // num_groups) % 2 == 0 else num_groups - 1 - (i % num_groups)
                groups[group_idx].append(student)
            
            # Add remaining students
            for student in student_profiles[num_groups * group_size:]:
                # Add to smallest group
                smallest_group = min(groups, key=len)
                smallest_group.append(student)
            
            rationale = "Groups formed using snake draft to mix high and low performers evenly."
        
        elif strategy == "similar_ability":
            # Sort by assessment score and group consecutively
            student_profiles.sort(key=lambda x: x["avg_assessment_score"], reverse=True)
            
            groups = []
            for i in range(0, len(student_profiles), group_size):
                groups.append(student_profiles[i:i + group_size])
            
            rationale = "Groups formed with similar ability levels for targeted instruction."
        
        elif strategy == "behavioral_balance":
            # Sort by behavior score
            student_profiles.sort(key=lambda x: x["behavior_score"], reverse=True)
            
            # Distribute high and low behavior students evenly
            num_groups = len(students) // group_size
            groups = [[] for _ in range(num_groups)]
            
            for i, student in enumerate(student_profiles[:num_groups * group_size]):
                group_idx = i % num_groups
                groups[group_idx].append(student)
            
            # Add remaining students
            for student in student_profiles[num_groups * group_size:]:
                smallest_group = min(groups, key=len)
                smallest_group.append(student)
            
            rationale = "Groups balanced to distribute behavioral dynamics evenly."
        
        elif strategy == "support_aware":
            # Sort by support level, then by assessment score
            student_profiles.sort(key=lambda x: (x["support_level"], -x["avg_assessment_score"]))
            
            # Distribute support needs across groups
            num_groups = len(students) // group_size
            groups = [[] for _ in range(num_groups)]
            
            for i, student in enumerate(student_profiles[:num_groups * group_size]):
                group_idx = i % num_groups if (i // num_groups) % 2 == 0 else num_groups - 1 - (i % num_groups)
                groups[group_idx].append(student)
            
            # Add remaining students
            for student in student_profiles[num_groups * group_size:]:
                smallest_group = min(groups, key=len)
                smallest_group.append(student)
            
            rationale = "Groups formed to distribute support needs evenly across teams."
        
        else:
            raise HTTPException(status_code=400, detail="Invalid strategy")
        
        # Format groups for response
        formatted_groups = []
        for i, group in enumerate(groups, 1):
            if not group:
                continue
                
            avg_score = sum(s["avg_assessment_score"] for s in group) / len(group)
            total_support = sum(s["support_level"] for s in group)
            avg_behavior = sum(s["behavior_score"] for s in group) / len(group)
            
            formatted_groups.append({
                "group_number": i,
                "members": [
                    {
                        "name": s["name"],
                        "avg_score": round(s["avg_assessment_score"], 1),
                        "support_level": s["support_level"],
                        "behavior_score": s["behavior_score"]
                    }
                    for s in group
                ],
                "group_stats": {
                    "size": len(group),
                    "avg_assessment_score": round(avg_score, 1),
                    "total_support_level": total_support,
                    "avg_behavior_score": round(avg_behavior, 1)
                }
            })
        
        return {
            "class_code": class_code,
            "strategy": strategy,
            "group_size": group_size,
            "total_students": len(students),
            "num_groups": len(formatted_groups),
            "groups": formatted_groups,
            "rationale": rationale
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating group formations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate groups: {str(e)}")


@router.get("/seating-chart")
async def generate_seating_chart(
    class_code: str,
    rows: int = 5,
    cols: int = 6,
    strategy: str = "behavior_optimized",
    db: Session = Depends(get_db)
):
    """
    Generate optimal seating chart for a class.
    
    Strategies:
    - behavior_optimized: Minimize behavioral conflicts
    - support_distributed: Distribute support needs evenly
    - mixed_ability: Mix high and low performers
    - random: Random assignment (baseline)
    
    Returns seating arrangement with reasoning.
    """
    try:
        import math
        
        # Get students in class
        students = db.query(Student).filter(Student.class_code == class_code).all()
        
        if not students:
            raise HTTPException(status_code=404, detail="No students found in class")
        
        total_seats = rows * cols
        if len(students) > total_seats:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough seats ({total_seats}) for {len(students)} students"
            )
        
        # Get student data
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        student_profiles = []
        for student in students:
            # Get behavior data
            logs = db.query(QuickLog).filter(
                QuickLog.student_id == student.id,
                QuickLog.timestamp >= thirty_days_ago
            ).all()
            
            positive_count = sum(1 for log in logs if log.log_type == "positive")
            negative_count = sum(1 for log in logs if log.log_type == "negative")
            behavior_score = positive_count - negative_count
            
            # Get assessment data
            assessments = db.query(Assessment).filter(
                Assessment.student_id == student.id
            ).order_by(desc(Assessment.date)).limit(5).all()
            
            avg_score = None
            if assessments:
                scores = [a.percentage for a in assessments if a.percentage is not None]
                if scores:
                    avg_score = sum(scores) / len(scores)
            
            student_profiles.append({
                "id": student.id,
                "name": student.name,
                "support_level": student.support_level,
                "behavior_score": behavior_score,
                "avg_assessment_score": avg_score or 50.0,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "has_high_incidents": negative_count > 5
            })
        
        # Initialize seating grid
        seating_grid = [[None for _ in range(cols)] for _ in range(rows)]
        
        if strategy == "behavior_optimized":
            # Separate students by behavior
            high_incident_students = [s for s in student_profiles if s["has_high_incidents"]]
            regular_students = [s for s in student_profiles if not s["has_high_incidents"]]
            
            # Sort by behavior score (lower/more negative first for high incidents)
            high_incident_students.sort(key=lambda x: x["behavior_score"])
            regular_students.sort(key=lambda x: -x["behavior_score"])  # Higher scores first
            
            # Place high-incident students in front corners and dispersed
            priority_positions = [
                (0, 0), (0, cols-1),  # Front corners
                (1, 0), (1, cols-1),  # Second row corners
                (0, cols//2),          # Front center
            ]
            
            # Assign high-incident students to priority positions
            for i, student in enumerate(high_incident_students):
                if i < len(priority_positions):
                    row, col = priority_positions[i]
                    seating_grid[row][col] = student
            
            # Distribute remaining high-incident students
            high_incident_idx = len(priority_positions)
            for row in range(rows):
                for col in range(cols):
                    if seating_grid[row][col] is None and high_incident_idx < len(high_incident_students):
                        # Skip adjacent seats to spread them out
                        if row % 2 == 0 and col % 2 == 0:
                            seating_grid[row][col] = high_incident_students[high_incident_idx]
                            high_incident_idx += 1
            
            # Fill remaining seats with regular students
            regular_idx = 0
            for row in range(rows):
                for col in range(cols):
                    if seating_grid[row][col] is None:
                        if regular_idx < len(regular_students):
                            seating_grid[row][col] = regular_students[regular_idx]
                            regular_idx += 1
            
            rationale = "Students with behavioral incidents placed strategically at front/corners for easy monitoring. Regular students fill remaining seats."
        
        elif strategy == "support_distributed":
            # Sort by support level (highest first)
            student_profiles.sort(key=lambda x: -x["support_level"])
            
            # Distribute evenly across rows
            student_idx = 0
            for col in range(cols):
                for row in range(rows):
                    if student_idx < len(student_profiles):
                        seating_grid[row][col] = student_profiles[student_idx]
                        student_idx += 1
            
            rationale = "Students with high support needs distributed evenly across the room for balanced teacher attention."
        
        elif strategy == "mixed_ability":
            # Sort by assessment scores
            student_profiles.sort(key=lambda x: x["avg_assessment_score"], reverse=True)
            
            # Snake pattern distribution
            student_idx = 0
            for row in range(rows):
                if row % 2 == 0:
                    # Left to right
                    for col in range(cols):
                        if student_idx < len(student_profiles):
                            seating_grid[row][col] = student_profiles[student_idx]
                            student_idx += 1
                else:
                    # Right to left
                    for col in range(cols-1, -1, -1):
                        if student_idx < len(student_profiles):
                            seating_grid[row][col] = student_profiles[student_idx]
                            student_idx += 1
            
            rationale = "Students arranged in snake pattern to mix high and low performers for peer learning opportunities."
        
        else:  # random
            import random
            shuffled = student_profiles.copy()
            random.shuffle(shuffled)
            
            student_idx = 0
            for row in range(rows):
                for col in range(cols):
                    if student_idx < len(shuffled):
                        seating_grid[row][col] = shuffled[student_idx]
                        student_idx += 1
            
            rationale = "Random seating arrangement for baseline comparison."
        
        # Format response
        formatted_grid = []
        for row_idx, row in enumerate(seating_grid):
            formatted_row = []
            for col_idx, student in enumerate(row):
                if student:
                    formatted_row.append({
                        "name": student["name"],
                        "student_id": student["id"],
                        "support_level": student["support_level"],
                        "behavior_score": student["behavior_score"],
                        "avg_score": round(student["avg_assessment_score"], 1),
                        "has_incidents": student["has_high_incidents"]
                    })
                else:
                    formatted_row.append(None)  # Empty seat
            formatted_grid.append(formatted_row)
        
        # Calculate statistics
        total_support = sum(s["support_level"] for s in student_profiles)
        avg_support_per_row = []
        for row in seating_grid:
            row_support = sum(s["support_level"] for s in row if s is not None)
            avg_support_per_row.append(row_support)
        
        return {
            "class_code": class_code,
            "strategy": strategy,
            "dimensions": {"rows": rows, "cols": cols, "total_seats": total_seats},
            "student_count": len(students),
            "empty_seats": total_seats - len(students),
            "seating_grid": formatted_grid,
            "rationale": rationale,
            "stats": {
                "total_support_needs": total_support,
                "support_per_row": avg_support_per_row,
                "high_incident_count": sum(1 for s in student_profiles if s["has_high_incidents"])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating seating chart: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate seating chart: {str(e)}")


@router.get("/differentiation-support")
async def get_differentiation_support(
    class_code: str,
    subject: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze students for differentiation needs.
    
    Groups students by:
    - Performance level (extension, on-level, support needed)
    - Assessment gaps and trends
    - Support levels
    
    Returns actionable groupings for differentiated instruction.
    """
    try:
        # Get students in class
        students = db.query(Student).filter(Student.class_code == class_code).all()
        
        if not students:
            raise HTTPException(status_code=404, detail="No students found in class")
        
        # Analyze each student
        student_analysis = []
        
        for student in students:
            # Get assessment data
            assessments_query = db.query(Assessment).filter(
                Assessment.student_id == student.id
            )
            
            # Filter by subject if provided
            if subject:
                assessments_query = assessments_query.filter(Assessment.subject == subject)
            
            assessments = assessments_query.order_by(desc(Assessment.date)).limit(10).all()
            
            if not assessments:
                # No assessment data - use support level as proxy
                avg_score = None
                trend = "unknown"
                recent_scores = []
            else:
                # Calculate average and trend
                scores = [a.percentage for a in assessments if a.percentage is not None]
                
                if scores:
                    avg_score = sum(scores) / len(scores)
                    recent_scores = scores[:5]  # Last 5 assessments
                    
                    # Calculate trend
                    if len(scores) >= 3:
                        recent_avg = sum(scores[:3]) / 3
                        older_avg = sum(scores[3:6]) / max(1, len(scores[3:6]))
                        
                        if recent_avg > older_avg + 5:
                            trend = "improving"
                        elif recent_avg < older_avg - 5:
                            trend = "declining"
                        else:
                            trend = "stable"
                    else:
                        trend = "insufficient_data"
                else:
                    avg_score = None
                    trend = "no_scores"
                    recent_scores = []
            
            # Classify performance level
            if avg_score is None:
                if student.support_level >= 2:
                    performance_level = "support_needed"
                else:
                    performance_level = "unknown"
            elif avg_score >= 80:
                performance_level = "extension"
            elif avg_score >= 60:
                performance_level = "on_level"
            else:
                performance_level = "support_needed"
            
            # Identify specific needs
            needs = []
            recommendations = []
            
            if performance_level == "extension":
                needs.append("Challenge and enrichment")
                recommendations.append("Provide extension activities and deeper inquiry tasks")
                if trend == "stable":
                    recommendations.append("Consider acceleration or independent projects")
            
            elif performance_level == "support_needed":
                needs.append("Additional instruction and practice")
                recommendations.append("Small group targeted instruction")
                
                if student.support_level >= 2:
                    needs.append("High support needs")
                    recommendations.append("1-on-1 or very small group support")
                
                if trend == "declining":
                    needs.append("Declining performance")
                    recommendations.append("Urgent intervention required")
            
            else:  # on_level
                needs.append("Grade-level instruction with scaffolding")
                recommendations.append("Mix of independent and supported work")
                
                if trend == "improving":
                    recommendations.append("Ready for more challenge")
                elif trend == "declining":
                    needs.append("At risk of falling behind")
                    recommendations.append("Monitor closely and provide extra support")
            
            # Identify subject-specific gaps (if assessment data available)
            gaps = []
            if assessments:
                # Group by topic if available
                topic_scores = {}
                for assessment in assessments[:10]:
                    if assessment.topic and assessment.percentage is not None:
                        if assessment.topic not in topic_scores:
                            topic_scores[assessment.topic] = []
                        topic_scores[assessment.topic].append(assessment.percentage)
                
                # Find weak topics
                for topic, scores in topic_scores.items():
                    avg_topic_score = sum(scores) / len(scores)
                    if avg_topic_score < 60:
                        gaps.append(f"{topic}: {avg_topic_score:.1f}% avg")
            
            student_analysis.append({
                "student_id": student.id,
                "student_name": student.name,
                "support_level": student.support_level,
                "performance_level": performance_level,
                "avg_score": round(avg_score, 1) if avg_score else None,
                "trend": trend,
                "recent_scores": recent_scores,
                "needs": needs,
                "recommendations": recommendations,
                "gaps": gaps,
                "assessment_count": len(assessments)
            })
        
        # Group by performance level
        extension_students = [s for s in student_analysis if s["performance_level"] == "extension"]
        on_level_students = [s for s in student_analysis if s["performance_level"] == "on_level"]
        support_students = [s for s in student_analysis if s["performance_level"] == "support_needed"]
        unknown_students = [s for s in student_analysis if s["performance_level"] == "unknown"]
        
        # Sort each group by average score
        for group in [extension_students, on_level_students, support_students]:
            group.sort(key=lambda x: x["avg_score"] or 0, reverse=True)
        
        # Generate suggested groupings for instruction
        suggested_groups = []
        
        # Extension group
        if extension_students:
            suggested_groups.append({
                "group_name": "Extension/Enrichment Group",
                "level": "extension",
                "student_count": len(extension_students),
                "students": [s["student_name"] for s in extension_students],
                "focus": "Challenge, enrichment, and independent inquiry",
                "strategies": [
                    "Provide open-ended extension tasks",
                    "Encourage peer teaching opportunities",
                    "Offer choice in how to demonstrate learning",
                    "Connect to real-world applications"
                ]
            })
        
        # On-level students - can work independently or in mixed groups
        if on_level_students:
            suggested_groups.append({
                "group_name": "Core Instruction Group",
                "level": "on_level",
                "student_count": len(on_level_students),
                "students": [s["student_name"] for s in on_level_students],
                "focus": "Grade-level curriculum with scaffolding",
                "strategies": [
                    "Mix of independent and collaborative work",
                    "Provide graphic organizers and guides",
                    "Check for understanding regularly",
                    "Pair with extension students for peer support"
                ]
            })
        
        # Support needed - prioritize by urgency
        if support_students:
            # Split into high priority (declining or high support level) and standard support
            high_priority = [
                s for s in support_students 
                if s["trend"] == "declining" or s["support_level"] >= 2
            ]
            standard_support = [
                s for s in support_students 
                if s not in high_priority
            ]
            
            if high_priority:
                suggested_groups.append({
                    "group_name": "Intensive Support Group (Priority)",
                    "level": "high_support",
                    "student_count": len(high_priority),
                    "students": [s["student_name"] for s in high_priority],
                    "focus": "Foundational skills and targeted intervention",
                    "strategies": [
                        "Small group (2-4 students) or 1-on-1 instruction",
                        "Break concepts into smaller steps",
                        "Use manipulatives and visual supports",
                        "Frequent formative assessment",
                        "Daily targeted practice"
                    ]
                })
            
            if standard_support:
                suggested_groups.append({
                    "group_name": "Support & Scaffolding Group",
                    "level": "support",
                    "student_count": len(standard_support),
                    "students": [s["student_name"] for s in standard_support],
                    "focus": "Building to grade-level expectations",
                    "strategies": [
                        "Small group instruction (4-6 students)",
                        "Pre-teach key concepts",
                        "Provide additional practice opportunities",
                        "Use peer tutoring with on-level students"
                    ]
                })
        
        # Summary statistics
        total_students = len(student_analysis)
        avg_class_score = None
        scores_available = [s["avg_score"] for s in student_analysis if s["avg_score"] is not None]
        if scores_available:
            avg_class_score = sum(scores_available) / len(scores_available)
        
        return {
            "class_code": class_code,
            "subject": subject or "All Subjects",
            "total_students": total_students,
            "summary": {
                "extension_count": len(extension_students),
                "on_level_count": len(on_level_students),
                "support_count": len(support_students),
                "unknown_count": len(unknown_students),
                "avg_class_score": round(avg_class_score, 1) if avg_class_score else None,
                "students_with_data": len(scores_available)
            },
            "students_by_level": {
                "extension": extension_students,
                "on_level": on_level_students,
                "support_needed": support_students,
                "unknown": unknown_students
            },
            "suggested_groups": suggested_groups
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating differentiation support: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate differentiation support: {str(e)}")
