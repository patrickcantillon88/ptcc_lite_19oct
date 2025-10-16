"""
Assessment data models
"""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class AssessmentBase(BaseModel):
    """Base assessment model"""
    student_id: int = Field(..., description="Student ID")
    assessment_type: str = Field(..., description="Type of assessment (CAT4, Quizizz, Formative)")
    subject: Optional[str] = Field(None, description="Subject area")
    topic: Optional[str] = Field(None, description="Specific topic")
    score: Optional[float] = Field(None, description="Raw score")
    max_score: Optional[float] = Field(None, description="Maximum possible score")
    percentage: Optional[float] = Field(None, description="Percentage score")
    source: str = Field(..., description="Source file or URL")


class AssessmentCreate(AssessmentBase):
    """Model for creating assessments"""
    pass


class Assessment(AssessmentBase):
    """Complete assessment model"""
    id: int
    date: date

    class Config:
        from_attributes = True


class AssessmentSummary(BaseModel):
    """Summary of student assessment data"""
    student_id: int
    student_name: str
    recent_assessments: List[Assessment] = Field(default_factory=list)
    average_score: Optional[float] = None
    trend: str = Field(..., description="improving/declining/stable")
    subjects: List[str] = Field(default_factory=list)


class CAT4Data(BaseModel):
    """CAT4 specific assessment data"""
    student_id: int
    verbal: Optional[int] = None
    quantitative: Optional[int] = None
    non_verbal: Optional[int] = None
    spatial: Optional[int] = None
    overall_score: Optional[int] = None
    date: date