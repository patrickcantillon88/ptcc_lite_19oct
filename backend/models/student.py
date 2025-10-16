"""
Student data models
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class StudentBase(BaseModel):
    """Base student model"""
    name: str = Field(..., description="Student full name")
    year_group: str = Field(..., description="Year group (7, 8, 9, etc.)")
    class_code: str = Field(..., description="Class code (e.g., 7B, 9A)")
    house: Optional[str] = Field(None, description="House name")
    campus: str = Field(..., description="Campus code (A or B)")
    photo_path: Optional[str] = Field(None, description="Path to student photo")


class StudentCreate(StudentBase):
    """Model for creating students"""
    pass


class StudentUpdate(BaseModel):
    """Model for updating students"""
    name: Optional[str] = None
    year_group: Optional[str] = None
    class_code: Optional[str] = None
    house: Optional[str] = None
    campus: Optional[str] = None
    photo_path: Optional[str] = None
    support_level: Optional[int] = None
    support_notes: Optional[str] = None


class Student(StudentBase):
    """Complete student model"""
    id: int
    support_level: int = Field(0, description="Support level (0=none, 1=low, 2=medium, 3=high)")
    support_notes: Optional[str] = Field(None, description="Support plan summary")
    last_updated: datetime

    class Config:
        from_attributes = True


class StudentWithLogs(Student):
    """Student with recent activity logs"""
    recent_logs: List["QuickLog"] = Field(default_factory=list, description="Recent activity logs")
    assessment_summary: Optional[dict] = Field(None, description="Recent assessment data")


class ClassRoster(BaseModel):
    """Class roster information"""
    class_code: str
    students: List[Student] = Field(default_factory=list)
    student_count: int = 0


class StudentSearchResult(BaseModel):
    """Search result for students"""
    student: Student
    relevance_score: float = Field(0.0, description="Search relevance score")
    matched_field: Optional[str] = Field(None, description="Field that matched the search")