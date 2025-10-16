"""
Activity log data models
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class LogType(str, Enum):
    """Types of activity logs"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class LogCategory(str, Enum):
    """Categories of logged activities"""
    EXCELLENT_CONTRIBUTION = "excellent_contribution"
    HELPING_OTHERS = "helping_others"
    OFF_TASK = "off_task"
    DISRUPTING_OTHERS = "disrupting_others"
    ANXIETY = "anxiety"
    LOGIN_ISSUES = "login_issues"
    MISSING_EQUIPMENT = "missing_equipment"
    CUSTOM = "custom"


class QuickLogBase(BaseModel):
    """Base quick log model"""
    student_id: int = Field(..., description="Student ID")
    class_code: str = Field(..., description="Class code")
    log_type: LogType = Field(..., description="Type of log entry")
    category: LogCategory = Field(..., description="Category of activity")
    points: int = Field(0, description="House points awarded/deducted")
    note: Optional[str] = Field(None, description="Optional custom note")


class QuickLogCreate(QuickLogBase):
    """Model for creating quick logs"""
    pass


class QuickLog(QuickLogBase):
    """Complete quick log model"""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class ClassSummary(BaseModel):
    """Summary of class activity"""
    class_code: str
    date: str
    total_logs: int
    positive_logs: int
    negative_logs: int
    neutral_logs: int
    total_points: int
    top_contributors: List[dict] = Field(default_factory=list)
    needs_followup: List[dict] = Field(default_factory=list)


class StudentLogSummary(BaseModel):
    """Summary of student's recent activity"""
    student_id: int
    student_name: str
    total_logs: int
    positive_logs: int
    negative_logs: int
    recent_trend: str = Field(..., description="improving/declining/stable")
    last_activity: Optional[datetime] = None
    categories: dict = Field(default_factory=dict, description="Count by category")