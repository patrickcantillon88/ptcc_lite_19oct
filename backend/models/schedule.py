"""
Schedule and timetable data models
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ScheduleEntryBase(BaseModel):
    """Base schedule entry model"""
    day_of_week: str = Field(..., description="Day of week")
    period: int = Field(..., description="Period number")
    start_time: str = Field(..., description="Start time (HH:MM)")
    end_time: str = Field(..., description="End time (HH:MM)")
    class_code: str = Field(..., description="Class code")
    subject: Optional[str] = Field(None, description="Subject name")
    room: Optional[str] = Field(None, description="Room/location")


class ScheduleEntryCreate(ScheduleEntryBase):
    """Model for creating schedule entries"""
    pass


class ScheduleEntry(ScheduleEntryBase):
    """Complete schedule entry model"""
    id: int

    class Config:
        from_attributes = True


class DailySchedule(BaseModel):
    """Complete daily schedule"""
    date: str
    day_name: str
    entries: List[ScheduleEntry] = Field(default_factory=list)
    has_classes: bool = True


class ClassSchedule(BaseModel):
    """Schedule for a specific class"""
    class_code: str
    schedule: List[ScheduleEntry] = Field(default_factory=list)


class DutyRotaBase(BaseModel):
    """Base duty rota model"""
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    duty_type: str = Field(..., description="Type of duty")
    location: Optional[str] = Field(None, description="Location")
    start_time: Optional[str] = Field(None, description="Start time")
    end_time: Optional[str] = Field(None, description="End time")
    notes: Optional[str] = Field(None, description="Additional notes")


class DutyRotaCreate(DutyRotaBase):
    """Model for creating duty rota entries"""
    pass


class DutyRota(DutyRotaBase):
    """Complete duty rota model"""
    id: int

    class Config:
        from_attributes = True


class DailyDuties(BaseModel):
    """Daily duty assignments"""
    date: str
    duties: List[DutyRota] = Field(default_factory=list)