"""
Communication data models
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class CommunicationSource(str, Enum):
    """Sources of communications"""
    EMAIL = "email"
    GOOGLE_DOC = "google_doc"
    MANUAL = "manual"


class CommunicationCategory(str, Enum):
    """Categories of communications"""
    URGENT = "urgent"
    CALENDAR = "calendar"
    FYI = "fyi"
    ACTION_REQUIRED = "action_required"


class CommunicationBase(BaseModel):
    """Base communication model"""
    source: CommunicationSource = Field(..., description="Source of communication")
    campus: Optional[str] = Field(None, description="Campus (A, B, or Both)")
    subject: str = Field(..., description="Communication subject")
    sender: Optional[str] = Field(None, description="Sender name")
    content: str = Field(..., description="Communication content")
    category: CommunicationCategory = Field(..., description="Communication category")
    action_required: bool = Field(False, description="Whether action is required")


class CommunicationCreate(CommunicationBase):
    """Model for creating communications"""
    pass


class Communication(CommunicationBase):
    """Complete communication model"""
    id: int
    received_date: datetime
    read: bool = Field(False, description="Whether communication has been read")
    archived: bool = Field(False, description="Whether communication is archived")

    class Config:
        from_attributes = True


class CommunicationInbox(BaseModel):
    """Inbox view of communications"""
    total_count: int
    unread_count: int
    urgent_count: int
    communications: List[Communication] = Field(default_factory=list)


class ReminderBase(BaseModel):
    """Base reminder model"""
    title: str = Field(..., description="Reminder title")
    message: str = Field(..., description="Reminder message")
    reminder_type: str = Field(..., description="daily/weekly/once/before_class")
    trigger_time: Optional[str] = Field(None, description="Time to trigger (HH:MM)")
    days: Optional[str] = Field(None, description="Days for weekly reminders")
    active: bool = Field(True, description="Whether reminder is active")


class ReminderCreate(ReminderBase):
    """Model for creating reminders"""
    pass


class Reminder(ReminderBase):
    """Complete reminder model"""
    id: int
    last_triggered: Optional[datetime] = None

    class Config:
        from_attributes = True


class ActionItemBase(BaseModel):
    """Base action item model"""
    assignee: str = Field(..., description="Person assigned")
    task: str = Field(..., description="Task description")
    source: str = Field(..., description="Source of action item")
    due_date: Optional[str] = Field(None, description="Due date (YYYY-MM-DD)")
    status: str = Field("pending", description="pending/in_progress/done")


class ActionItemCreate(ActionItemBase):
    """Model for creating action items"""
    pass


class ActionItem(ActionItemBase):
    """Complete action item model"""
    id: int
    created_date: str
    completed_date: Optional[str] = None

    class Config:
        from_attributes = True