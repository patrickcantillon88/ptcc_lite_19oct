"""
SQLAlchemy database models
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float, Date,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from ..core.database import Base


class Student(Base):
    """Student table"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    photo_path = Column(String)
    year_group = Column(String, nullable=False)
    class_code = Column(String, nullable=False)
    house = Column(String)
    campus = Column(String, nullable=False)
    support_level = Column(Integer, default=0)  # 0=none, 1=low, 2=medium, 3=high
    support_notes = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)

    # Relationships
    logs = relationship("QuickLog", back_populates="student")
    assessments = relationship("Assessment", back_populates="student")

    __table_args__ = (
        Index('idx_students_class', 'class_code'),
        Index('idx_students_name', 'name'),
    )


class Schedule(Base):
    """Schedule table"""
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String, nullable=False)  # 'Monday', 'Tuesday', etc.
    period = Column(Integer, nullable=False)
    start_time = Column(String)  # '08:30'
    end_time = Column(String)    # '09:15'
    class_code = Column(String, nullable=False)
    subject = Column(String)
    room = Column(String)

    __table_args__ = (
        UniqueConstraint('day_of_week', 'period', name='unique_period_per_day'),
    )


class ClassRoster(Base):
    """Class roster table"""
    __tablename__ = "class_rosters"

    class_code = Column(String, primary_key=True, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True, nullable=False)


class QuickLog(Base):
    """Quick logs table - supports both classroom and CCA behavior"""
    __tablename__ = "quick_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_code = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    log_type = Column(String, nullable=False)  # 'positive', 'negative', 'neutral'
    category = Column(String, nullable=False)  # 'excellent_contribution', 'off_task', 'cca_pe', 'cca_music', etc.
    points = Column(Integer, default=0)  # House points awarded/deducted
    note = Column(Text)  # Optional custom text
    cca_subject = Column(String)  # For CCA logs: 'PE', 'Music/PA', 'ICT/STEAM', 'MFL', etc. NULL for classroom logs
    
    # ICT Behavior Management fields
    strike_level = Column(Integer)  # 1, 2, or 3 (NULL for non-strike logs)
    consequence_text = Column(String)  # Auto-generated consequence text
    admin_notified = Column(Boolean, default=False)  # Admin escalation flag
    hod_consulted = Column(Boolean, default=False)  # HOD consultation flag
    parent_meeting_scheduled = Column(Boolean, default=False)  # Parent meeting flag
    lesson_session_id = Column(String)  # Groups logs by lesson session

    # Relationships
    student = relationship("Student", back_populates="logs")

    __table_args__ = (
        Index('idx_quick_logs_student', 'student_id'),
        Index('idx_quick_logs_timestamp', 'timestamp'),
        Index('idx_quick_logs_cca_subject', 'cca_subject'),
    )


class Assessment(Base):
    """Assessments table"""
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    assessment_type = Column(String, nullable=False)  # 'CAT4', 'Quizizz', 'Formative'
    subject = Column(String)
    topic = Column(String)
    score = Column(Float)
    max_score = Column(Float)
    percentage = Column(Float)
    date = Column(Date, nullable=False)
    source = Column(String)  # Filename or URL

    # Relationships
    student = relationship("Student", back_populates="assessments")

    __table_args__ = (
        Index('idx_assessments_student', 'student_id'),
    )


class Reminder(Base):
    """Reminders table"""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    reminder_type = Column(String, nullable=False)  # 'daily', 'weekly', 'once', 'before_class'
    trigger_time = Column(String)  # '07:00' or 'before_period_2'
    days = Column(String)  # 'Monday,Wednesday,Friday' or NULL for daily
    message = Column(Text)
    active = Column(Boolean, default=True)
    last_triggered = Column(DateTime)


class DutyRota(Base):
    """Duty rotas table"""
    __tablename__ = "duty_rotas"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    duty_type = Column(String, nullable=False)  # 'Gate Supervision', 'CCA', 'Assembly'
    location = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    notes = Column(Text)

    __table_args__ = (
        Index('idx_duty_date', 'date'),
    )


class Communication(Base):
    """Communications table"""
    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)  # 'email', 'google_doc', 'manual'
    campus = Column(String)  # 'A', 'B', 'Both', NULL
    subject = Column(String)
    sender = Column(String)
    content = Column(Text)
    category = Column(String)  # 'urgent', 'calendar', 'fyi', 'action_required'
    received_date = Column(DateTime, nullable=False)
    action_required = Column(Boolean, default=False)
    read = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)

    __table_args__ = (
        Index('idx_comms_date', 'received_date'),
        Index('idx_comms_unread', 'read'),
    )


class CCA(Base):
    """Co-curricular activities table"""
    __tablename__ = "ccas"

    id = Column(Integer, primary_key=True, index=True)
    cca_name = Column(String, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    term = Column(String)  # 'Term 1', 'Term 2', etc.
    leader = Column(String)
    day = Column(String)
    time = Column(String)


class NameDrillProgress(Base):
    """Name learning progress table"""
    __tablename__ = "name_drill_progress"

    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    last_shown = Column(DateTime)
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0


class ActionItem(Base):
    """Action items table (from meeting notes)"""
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    assignee = Column(String, nullable=False)
    task = Column(String, nullable=False)
    source = Column(String)  # e.g., "ICT Meeting Sept 24"
    due_date = Column(Date)
    status = Column(String, default='pending')  # 'pending', 'in_progress', 'done'
    created_date = Column(Date, nullable=False)
    completed_date = Column(Date)


class Staff(Base):
    """Staff members table"""
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # 'Class Teacher', 'Learning Support Teacher', 'TA', 'Specialist'
    class_code = Column(String)  # FK to class (optional for specialists)
    specialties = Column(Text)  # JSON: ['ICT', 'PE', 'Music']
    term = Column(String)  # 'Term 1', 'Term 2', etc.
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_staff_class', 'class_code'),
        Index('idx_staff_role', 'role'),
    )


class Timetable(Base):
    """Timetable (enhanced Schedule table)"""
    __tablename__ = "timetables"

    id = Column(Integer, primary_key=True, index=True)
    class_code = Column(String, nullable=False, index=True)
    day_of_week = Column(String, nullable=False)  # 'Monday', 'Tuesday', etc.
    period = Column(Integer, nullable=False)  # 1-6
    start_time = Column(String, nullable=False)  # '08:30'
    end_time = Column(String, nullable=False)  # '09:15'
    subject = Column(String, nullable=False)
    lesson_type = Column(String)  # 'Literacy', 'Numeracy', 'Foundation', 'Specialist', 'CCA'
    specialist_name = Column(String)  # Name of specialist if applicable
    room = Column(String)
    notes = Column(Text)
    created_date = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_timetable_class_day', 'class_code', 'day_of_week'),
        Index('idx_timetable_period', 'period'),
    )


class SpecialistLessonSchedule(Base):
    """Specialist lesson schedule"""
    __tablename__ = "specialist_lesson_schedules"

    id = Column(Integer, primary_key=True, index=True)
    class_code = Column(String, nullable=False, index=True)
    day_of_week = Column(String, nullable=False)
    period = Column(Integer, nullable=False)
    specialist_type = Column(String, nullable=False)  # 'ICT', 'PE', 'Music', 'Drama', 'Art', 'Robotics'
    instructor_name = Column(String)
    notes = Column(Text)
    created_date = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_specialist_class', 'class_code'),
        Index('idx_specialist_type', 'specialist_type'),
    )


class StudentAccommodation(Base):
    """Student accommodations table"""
    __tablename__ = "student_accommodations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    accommodation_type = Column(String, nullable=False)  # 'sensory', 'seating', 'schedule', 'equipment', 'behavioral'
    description = Column(String, nullable=False)
    implementation_details = Column(Text)
    active = Column(Boolean, default=True)
    effective_date = Column(Date, nullable=False)
    notes = Column(Text)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_student_accommodations_student', 'student_id'),
        Index('idx_student_accommodations_type', 'accommodation_type'),
    )
