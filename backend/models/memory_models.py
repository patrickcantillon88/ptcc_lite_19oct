"""
Memory System Database Models for PTCC

Implements personalized AI memory structures including user profiles,
context layers, interaction history, and teaching preferences.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float, Date,
    ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship

from ..core.database import Base


class UserProfile(Base):
    """User profile for personalized AI memory"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, default="teacher")  # teacher, admin, etc.
    
    # Teaching preferences
    instructional_style = Column(Text)
    subject_expertise = Column(JSON)  # List of subjects
    classroom_management_approach = Column(Text)
    
    # Curriculum context
    grade_levels = Column(JSON)  # List of grade levels taught
    subjects = Column(JSON)  # List of subjects taught
    standards = Column(JSON)  # Educational standards followed
    school_specific_requirements = Column(Text)
    
    # Professional profile
    years_experience = Column(Integer)
    certifications = Column(JSON)
    professional_interests = Column(JSON)
    teaching_philosophy = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    context_layers = relationship("ContextLayer", back_populates="user_profile")
    interaction_history = relationship("InteractionHistory", back_populates="user_profile")
    teaching_preferences = relationship("TeachingPreference", back_populates="user_profile")

    __table_args__ = (
        Index('idx_user_profiles_user_id', 'user_id'),
    )


class ContextLayer(Base):
    """Context layers for Context Engineering system"""
    __tablename__ = "context_layers"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    layer_type = Column(String, nullable=False)  # base, dynamic, historical, situational, environmental, philosophical
    layer_name = Column(String, nullable=False)
    layer_data = Column(JSON, nullable=False)
    priority = Column(Integer, default=5)  # 1-10 scale
    active = Column(Boolean, default=True)
    
    # Temporal tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    access_count = Column(Integer, default=0)
    
    # Relationships
    user_profile = relationship("UserProfile", back_populates="context_layers")

    __table_args__ = (
        Index('idx_context_layers_user', 'user_profile_id'),
        Index('idx_context_layers_type', 'layer_type'),
    )


class InteractionHistory(Base):
    """Interaction history for memory evolution"""
    __tablename__ = "interaction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # Interaction details
    interaction_type = Column(String, nullable=False)  # query, command, feedback, etc.
    query_text = Column(Text)
    response_text = Column(Text)
    agent_used = Column(String)
    context_used = Column(JSON)  # Context layers applied
    
    # Feedback and learning
    user_feedback = Column(String)  # positive, negative, neutral
    feedback_note = Column(Text)
    successful = Column(Boolean, default=True)
    
    # Performance metrics
    response_time_ms = Column(Integer)
    relevance_score = Column(Float)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user_profile = relationship("UserProfile", back_populates="interaction_history")

    __table_args__ = (
        Index('idx_interaction_history_user', 'user_profile_id'),
        Index('idx_interaction_history_timestamp', 'timestamp'),
        Index('idx_interaction_history_type', 'interaction_type'),
    )


class TeachingPreference(Base):
    """Specific teaching preferences and patterns"""
    __tablename__ = "teaching_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    preference_category = Column(String, nullable=False)  # communication, assessment, behavior_management, etc.
    preference_key = Column(String, nullable=False)
    preference_value = Column(JSON, nullable=False)
    confidence_score = Column(Float, default=0.5)  # How confident the system is about this preference
    
    learned_from_interactions = Column(Boolean, default=False)
    explicitly_set = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_profile = relationship("UserProfile", back_populates="teaching_preferences")

    __table_args__ = (
        Index('idx_teaching_preferences_user', 'user_profile_id'),
        Index('idx_teaching_preferences_category', 'preference_category'),
    )


class StudentDemographic(Base):
    """Student demographic context for personalized AI"""
    __tablename__ = "student_demographics"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # Demographics tracked by teacher
    age_ranges = Column(JSON)  # List of age ranges
    learning_needs = Column(JSON)  # Types of learning needs in classes
    language_requirements = Column(JSON)  # Languages spoken by students
    cultural_considerations = Column(JSON)  # Cultural backgrounds
    
    # Class characteristics
    typical_class_size = Column(Integer)
    support_level_distribution = Column(JSON)  # Distribution of support levels
    
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_student_demographics_user', 'user_profile_id'),
    )


class CurriculumContext(Base):
    """Curriculum context tracking"""
    __tablename__ = "curriculum_context"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    subject = Column(String, nullable=False)
    grade_level = Column(String, nullable=False)
    
    # Current curriculum state
    current_unit = Column(String)
    current_topics = Column(JSON)
    upcoming_topics = Column(JSON)
    completed_topics = Column(JSON)
    
    # Standards and objectives
    standards_covered = Column(JSON)
    learning_objectives = Column(JSON)
    
    # Resources and materials
    preferred_resources = Column(JSON)
    available_materials = Column(JSON)
    
    # Assessment context
    assessment_schedule = Column(JSON)
    grading_preferences = Column(JSON)
    
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_curriculum_context_user', 'user_profile_id'),
        Index('idx_curriculum_context_subject_grade', 'subject', 'grade_level'),
    )
