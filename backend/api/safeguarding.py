"""
Safeguarding API Endpoints

Provides REST endpoints for privacy-preserving student safeguarding analysis.
All endpoints use tokenization and maintain complete privacy guarantees.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Request models
class BehavioralIncident(BaseModel):
    type: str
    timestamp: datetime
    description: Optional[str] = None

class Assessment(BaseModel):
    subject: str
    performance_level: str  # "below", "at", "above", "advanced"
    timestamp: datetime
    assessment_type: Optional[str] = "formative"

class Communication(BaseModel):
    source: str  # "parent", "teacher", "admin"
    urgency_level: str  # "routine", "important", "urgent"
    timestamp: datetime
    content: Optional[str] = None

class AttendanceRecord(BaseModel):
    status: str  # "present", "absent", "late"
    timestamp: datetime

class StudentDataRequest(BaseModel):
    student_id: str
    behavioral_incidents: Optional[List[BehavioralIncident]] = []
    assessments: Optional[List[Assessment]] = []
    communications: Optional[List[Communication]] = []
    attendance: Optional[List[AttendanceRecord]] = []

# Create router
router = APIRouter(tags=["safeguarding"])


@router.post("/analyze")
async def analyze_student(request: StudentDataRequest, req: Request):
    """
    Analyze a student's safeguarding status with complete privacy preservation.
    
    All data is tokenized locally. Only anonymized tokens are used externally.
    Returns comprehensive analysis with privacy guarantees.
    """
    try:
        # Get safeguarding orchestrator from app state
        if not hasattr(req.app.state, "safeguarding") or req.app.state.safeguarding is None:
            raise HTTPException(
                status_code=503,
                detail="Safeguarding system not initialized"
            )
        
        orchestrator = req.app.state.safeguarding
        
        # Convert Pydantic models to dicts for analysis
        student_data = {
            "behavioral_incidents": [
                {
                    "type": incident.type,
                    "timestamp": incident.timestamp,
                    "description": incident.description
                }
                for incident in request.behavioral_incidents or []
            ],
            "assessments": [
                {
                    "subject": assessment.subject,
                    "performance_level": assessment.performance_level,
                    "timestamp": assessment.timestamp,
                    "type": assessment.assessment_type
                }
                for assessment in request.assessments or []
            ],
            "communications": [
                {
                    "source": comm.source,
                    "urgency_level": comm.urgency_level,
                    "timestamp": comm.timestamp,
                    "content": comm.content
                }
                for comm in request.communications or []
            ],
            "attendance": [
                {
                    "status": record.status,
                    "timestamp": record.timestamp
                }
                for record in request.attendance or []
            ]
        }
        
        # Run analysis (6-stage privacy-preserving process)
        report = orchestrator.analyze_student_safeguarding(
            student_id=request.student_id,
            student_data=student_data
        )
        
        logger.info(f"Safeguarding analysis completed for {request.student_id}")
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Safeguarding analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Safeguarding analysis failed: {str(e)}"
        )


@router.get("/summary/{student_id}")
async def get_analysis_summary(student_id: str, req: Request):
    """
    Get summary of recent analyses for a student.
    
    Returns most recent analysis, risk trend, and summary.
    """
    try:
        if not hasattr(req.app.state, "safeguarding"):
            raise HTTPException(
                status_code=503,
                detail="Safeguarding system not initialized"
            )
        
        orchestrator = req.app.state.safeguarding
        summary = orchestrator.get_analysis_summary(student_id)
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting safeguarding summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get summary: {str(e)}"
        )


@router.get("/compliance")
async def get_compliance_report(req: Request):
    """
    Get privacy compliance report for all safeguarding analyses.
    
    Shows total analyses, privacy assertions, and risk statistics.
    Useful for auditing and compliance verification.
    """
    try:
        if not hasattr(req.app.state, "safeguarding"):
            raise HTTPException(
                status_code=503,
                detail="Safeguarding system not initialized"
            )
        
        orchestrator = req.app.state.safeguarding
        compliance_report = orchestrator.get_privacy_compliance_report()
        
        return compliance_report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate compliance report: {str(e)}"
        )


@router.get("/health")
async def safeguarding_health(req: Request):
    """
    Check safeguarding system health status.
    """
    try:
        if not hasattr(req.app.state, "safeguarding"):
            return {
                "status": "not_initialized",
                "message": "Safeguarding system not initialized"
            }
        
        return {
            "status": "operational",
            "system": "privacy-preserving-safeguarding",
            "version": "1.0.0",
            "privacy_guarantees": [
                "All PII converted to tokens",
                "Token mappings stored locally only",
                "External communication uses tokens only",
                "Comprehensive audit trail maintained"
            ]
        }
        
    except Exception as e:
        logger.error(f"Safeguarding health check error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
