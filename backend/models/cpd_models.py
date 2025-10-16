"""
CPD (Continuing Professional Development) Database Models for PTCC

Implements CPD records, recommendations, skill assessments, and development goals
for tracking and enhancing teacher professional development.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float, Date,
    ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship

from ..core.database import Base


class CPDRecord(Base):
    """Records of professional development activities"""
    __tablename__ = "cpd_records"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # CPD identification
    cpd_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    cpd_type = Column(String, nullable=False)  # course, workshop, conference, reading, observation, collaboration, self_study
    
    # Provider
    provider = Column(String)  # Who provided this CPD
    provider_type = Column(String)  # internal, external, online, self_directed
    accreditation_body = Column(String)  # If accredited
    
    # Details
    description = Column(Text)
    learning_objectives = Column(JSON)  # What was supposed to be learned
    content_areas = Column(JSON)  # Subject areas covered
    topics = Column(JSON)  # Specific topics
    
    # Dates and duration
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    duration_hours = Column(Float)  # Total hours
    
    # Status
    status = Column(String, default="planned")  # planned, in_progress, completed, cancelled
    completion_date = Column(Date)
    completion_percentage = Column(Integer, default=0)
    
    # Certification
    certification_awarded = Column(Boolean, default=False)
    certification_title = Column(String)
    certification_number = Column(String)
    certification_expiry = Column(Date)
    certificate_path = Column(String)  # Path to certificate file
    
    # Requirements
    was_mandatory = Column(Boolean, default=False)
    required_by = Column(String)  # School, district, certification body
    requirement_category = Column(String)  # safeguarding, subject_knowledge, pedagogy, etc.
    
    # Quality and relevance
    quality_rating = Column(Integer)  # 1-5 stars
    relevance_to_practice = Column(Integer)  # 1-5 scale
    would_recommend = Column(Boolean)
    
    # Learning outcomes
    skills_acquired = Column(JSON)  # Skills learned
    knowledge_gained = Column(JSON)  # Knowledge areas
    competencies_improved = Column(JSON)  # Competencies enhanced
    
    # Application
    applied_in_practice = Column(Boolean, default=False)
    application_examples = Column(JSON)  # How it was applied
    impact_on_teaching = Column(Text)  # Impact description
    impact_rating = Column(Integer)  # 1-5 scale
    
    # Evidence
    evidence_of_completion = Column(JSON)  # Documents, certificates, etc.
    evidence_of_impact = Column(JSON)  # Evidence of impact on practice
    
    # Follow-up
    requires_follow_up = Column(Boolean, default=False)
    follow_up_actions = Column(JSON)
    follow_up_date = Column(Date)
    
    # Cost and logistics
    cost = Column(Float)
    funded_by = Column(String)  # Self, school, grant, etc.
    location = Column(String)
    delivery_mode = Column(String)  # in_person, online, hybrid, self_paced
    
    # Metadata
    tags = Column(JSON)
    related_goals = Column(JSON)  # Related development goal IDs
    related_assessments = Column(JSON)  # Related skill assessment IDs
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recommendations = relationship("CPDRecommendation", back_populates="cpd_record")

    __table_args__ = (
        Index('idx_cpd_records_user', 'user_profile_id'),
        Index('idx_cpd_records_type', 'cpd_type'),
        Index('idx_cpd_records_status', 'status'),
        Index('idx_cpd_records_start_date', 'start_date'),
    )


class CPDRecommendation(Base):
    """AI-generated recommendations for professional development"""
    __tablename__ = "cpd_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # Recommendation identification
    recommendation_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    
    # Recommendation details
    recommendation_type = Column(String, nullable=False)  # skill_gap, career_advancement, curriculum_change, emerging_practice
    priority = Column(Integer, default=5)  # 1-10, higher = more important
    urgency = Column(String)  # low, medium, high, urgent
    
    # Rationale
    rationale = Column(Text, nullable=False)  # Why this is recommended
    identified_need = Column(Text)  # What need this addresses
    expected_benefit = Column(Text)  # Expected outcomes
    
    # Gap analysis
    current_skill_level = Column(Integer)  # Current level 1-5
    target_skill_level = Column(Integer)  # Target level 1-5
    skill_gap_areas = Column(JSON)  # Specific areas to develop
    
    # Context
    based_on_assessments = Column(JSON)  # Skill assessment IDs
    based_on_context = Column(JSON)  # Context layers considered
    based_on_goals = Column(JSON)  # Development goal IDs
    curriculum_alignment = Column(JSON)  # How it aligns with curriculum
    
    # Suggested CPD activities
    suggested_cpd_types = Column(JSON)  # Types of CPD to pursue
    suggested_providers = Column(JSON)  # Recommended providers
    suggested_resources = Column(JSON)  # Specific courses, books, etc.
    estimated_duration = Column(String)  # Time commitment
    estimated_cost_range = Column(String)  # Cost estimate
    
    # Timeline
    recommended_start_date = Column(Date)
    recommended_completion_date = Column(Date)
    
    # Related CPD
    related_cpd_record_id = Column(String, ForeignKey("cpd_records.cpd_id"))  # If acted upon
    
    # AI generation
    generated_by_agent = Column(String)  # Which agent made this recommendation
    generation_method = Column(String)  # How it was generated
    confidence_score = Column(Float)  # AI confidence
    
    # User response
    status = Column(String, default="pending")  # pending, accepted, planned, in_progress, completed, dismissed
    user_feedback = Column(Text)
    dismissal_reason = Column(Text)
    
    # Impact tracking
    action_taken = Column(Boolean, default=False)
    action_date = Column(Date)
    impact_achieved = Column(Boolean)
    impact_notes = Column(Text)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = Column(DateTime)
    actioned_at = Column(DateTime)
    
    # Relationships
    cpd_record = relationship("CPDRecord", back_populates="recommendations")

    __table_args__ = (
        Index('idx_cpd_recommendations_user', 'user_profile_id'),
        Index('idx_cpd_recommendations_type', 'recommendation_type'),
        Index('idx_cpd_recommendations_status', 'status'),
        Index('idx_cpd_recommendations_priority', 'priority'),
        Index('idx_cpd_recommendations_created', 'created_at'),
    )


class SkillAssessment(Base):
    """Assessments of teaching skills and competencies"""
    __tablename__ = "skill_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # Assessment identification
    assessment_id = Column(String, unique=True, nullable=False, index=True)
    assessment_title = Column(String, nullable=False)
    assessment_type = Column(String, nullable=False)  # self_assessment, peer_review, observation, performance_data, ai_analysis
    
    # Assessment details
    skill_domain = Column(String, nullable=False)  # subject_knowledge, pedagogy, classroom_management, assessment, technology, etc.
    specific_skills = Column(JSON, nullable=False)  # Specific skills assessed
    
    # Assessment framework
    framework_used = Column(String)  # Teaching standards framework
    competency_areas = Column(JSON)  # Competency areas assessed
    
    # Timing
    assessment_date = Column(Date, nullable=False)
    assessment_period_start = Column(Date)  # Period covered by assessment
    assessment_period_end = Column(Date)
    
    # Results
    overall_score = Column(Float)  # Overall proficiency score
    skill_scores = Column(JSON, nullable=False)  # Individual skill scores
    strengths = Column(JSON)  # Identified strengths
    areas_for_development = Column(JSON)  # Areas needing improvement
    
    # Detailed feedback
    assessor_feedback = Column(Text)
    self_reflection = Column(Text)
    specific_observations = Column(JSON)  # Specific observations or evidence
    
    # Context
    class_context = Column(JSON)  # Classes/students assessed in
    subject_context = Column(JSON)  # Subjects
    grade_level_context = Column(JSON)  # Grade levels
    
    # Assessor
    assessed_by = Column(String)  # self, peer, supervisor, ai_agent
    assessor_name = Column(String)
    assessor_role = Column(String)
    
    # Comparison
    previous_assessment_id = Column(String, ForeignKey("skill_assessments.assessment_id"))
    progress_since_previous = Column(JSON)  # Progress indicators
    trend = Column(String)  # improving, stable, declining
    
    # Evidence
    evidence_sources = Column(JSON)  # Sources of evidence
    evidence_quality = Column(String)  # low, medium, high
    
    # Action planning
    recommended_actions = Column(JSON)  # Recommended next steps
    cpd_recommendations_generated = Column(JSON)  # CPD recommendation IDs
    development_goals_created = Column(JSON)  # Development goal IDs
    
    # Validation
    validated = Column(Boolean, default=False)
    validation_notes = Column(Text)
    
    # Status
    status = Column(String, default="completed")  # draft, completed, reviewed, archived
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_skill_assessments_user', 'user_profile_id'),
        Index('idx_skill_assessments_type', 'assessment_type'),
        Index('idx_skill_assessments_domain', 'skill_domain'),
        Index('idx_skill_assessments_date', 'assessment_date'),
    )


class DevelopmentGoal(Base):
    """Professional development goals"""
    __tablename__ = "development_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # Goal identification
    goal_id = Column(String, unique=True, nullable=False, index=True)
    goal_title = Column(String, nullable=False)
    goal_type = Column(String, nullable=False)  # skill_development, qualification, career_advancement, teaching_improvement
    
    # Goal details
    goal_description = Column(Text, nullable=False)
    goal_category = Column(String)  # subject_knowledge, pedagogy, leadership, etc.
    
    # SMART goal elements
    is_specific = Column(Boolean, default=True)
    is_measurable = Column(Boolean, default=True)
    is_achievable = Column(Boolean, default=True)
    is_relevant = Column(Boolean, default=True)
    is_time_bound = Column(Boolean, default=True)
    
    # Targets
    target_description = Column(Text)  # What success looks like
    success_criteria = Column(JSON)  # Measurable success criteria
    target_completion_date = Column(Date)
    
    # Context
    related_skill_assessments = Column(JSON)  # Assessment IDs
    related_cpd_records = Column(JSON)  # CPD record IDs
    aligned_with_standards = Column(JSON)  # Teaching standards
    school_priorities = Column(JSON)  # How it aligns with school goals
    
    # Action plan
    action_steps = Column(JSON, nullable=False)  # Steps to achieve goal
    resources_needed = Column(JSON)  # Resources required
    support_needed = Column(JSON)  # Support from others
    potential_barriers = Column(JSON)  # Anticipated challenges
    mitigation_strategies = Column(JSON)  # How to overcome barriers
    
    # Timeline
    start_date = Column(Date, nullable=False)
    milestones = Column(JSON)  # Key milestones with dates
    review_dates = Column(JSON)  # Scheduled review dates
    
    # Progress tracking
    status = Column(String, default="active")  # active, on_hold, completed, abandoned
    progress_percentage = Column(Integer, default=0)
    completed_steps = Column(JSON)  # Which action steps completed
    current_milestone = Column(String)
    
    # Reviews
    last_review_date = Column(Date)
    next_review_date = Column(Date)
    review_notes = Column(JSON)  # Notes from reviews
    
    # Impact
    expected_impact = Column(Text)  # Expected impact on teaching
    actual_impact = Column(Text)  # Actual impact achieved
    impact_evidence = Column(JSON)  # Evidence of impact
    impact_rating = Column(Integer)  # 1-5 scale
    
    # Outcomes
    completion_date = Column(Date)
    outcome_achieved = Column(Boolean)
    outcome_description = Column(Text)
    lessons_learned = Column(Text)
    
    # Priority and urgency
    priority = Column(Integer, default=5)  # 1-10
    urgency = Column(String)  # low, medium, high
    
    # Generation
    created_by = Column(String)  # user, ai_agent, supervisor
    generated_from_recommendation = Column(String)  # CPD recommendation ID
    
    # Visibility
    shared_with = Column(JSON)  # Who this goal is shared with
    visibility = Column(String, default="private")  # private, supervisor, team, public
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_development_goals_user', 'user_profile_id'),
        Index('idx_development_goals_type', 'goal_type'),
        Index('idx_development_goals_status', 'status'),
        Index('idx_development_goals_target_date', 'target_completion_date'),
    )


class CPDImpactEvidence(Base):
    """Evidence of CPD impact on teaching practice"""
    __tablename__ = "cpd_impact_evidence"

    id = Column(Integer, primary_key=True, index=True)
    cpd_record_id = Column(String, ForeignKey("cpd_records.cpd_id"), nullable=False)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # Evidence details
    evidence_type = Column(String, nullable=False)  # lesson_observation, student_data, reflection, artifact, feedback
    evidence_title = Column(String, nullable=False)
    evidence_description = Column(Text)
    
    # Evidence source
    source = Column(String)  # Where evidence came from
    source_date = Column(Date)
    
    # Evidence content
    evidence_data = Column(JSON)  # Structured evidence data
    evidence_file_path = Column(String)  # Path to evidence file
    
    # Analysis
    demonstrates_skills = Column(JSON)  # Which skills are demonstrated
    impact_level = Column(String)  # low, medium, high
    impact_description = Column(Text)  # Description of impact
    
    # Quality
    evidence_quality = Column(String)  # weak, moderate, strong
    validated = Column(Boolean, default=False)
    validator = Column(String)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_cpd_impact_cpd', 'cpd_record_id'),
        Index('idx_cpd_impact_user', 'user_profile_id'),
        Index('idx_cpd_impact_type', 'evidence_type'),
    )
