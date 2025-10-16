"""
Governance Database Models for PTCC

Models for policy management, compliance tracking, audit logs,
risk assessment, and incident management.
"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from datetime import datetime

from ..core.database import Base


class PolicyFramework(Base):
    """Store organizational policies and frameworks."""
    __tablename__ = "policy_frameworks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Policy identification
    policy_name = Column(String(255), nullable=False, index=True)
    policy_category = Column(String(100), nullable=False, index=True)
    policy_version = Column(String(50), default="1.0.0")
    
    # Policy content
    policy_content = Column(JSON, nullable=False)
    scope = Column(String(255))  # Who/what this applies to
    enforcement_level = Column(String(50))  # mandatory, recommended, optional
    
    # Status
    active = Column(Boolean, default=True)
    effective_date = Column(DateTime)
    expiry_date = Column(DateTime, nullable=True)
    
    # Metadata
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_by = Column(String(255))
    approval_date = Column(DateTime, nullable=True)


class ComplianceCheck(Base):
    """Track compliance verification checks."""
    __tablename__ = "compliance_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # What was checked
    policy_id = Column(Integer, nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)  # user, agent, content, etc.
    entity_id = Column(String(255), nullable=False, index=True)
    
    # Results
    compliance_status = Column(String(50), nullable=False)  # compliant, non_compliant, etc.
    check_details = Column(JSON, default=dict)
    violations = Column(JSON, default=list)
    
    # Context
    context_metadata = Column(JSON, default=dict)
    
    # Actions
    action_required = Column(Boolean, default=False)
    action_taken = Column(Text)
    
    # Tracking
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    checked_by = Column(String(255))
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)


class AuditLog(Base):
    """Comprehensive audit trail of all system activities."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Action details
    action_type = Column(String(100), nullable=False, index=True)
    action_details = Column(JSON, default=dict)
    
    # Actor information
    actor_id = Column(String(255), nullable=False, index=True)
    actor_type = Column(String(100))  # user, system, agent, api
    
    # Target information
    target_entity = Column(String(100), nullable=False, index=True)
    target_id = Column(String(255), nullable=False)
    
    # Results
    result = Column(String(50))  # success, failure, partial
    result_details = Column(JSON, default=dict)
    
    # Context
    session_id = Column(String(255))
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    duration_ms = Column(Integer)
    
    # Security
    security_level = Column(String(50))
    flagged = Column(Boolean, default=False)
    flag_reason = Column(Text)


class RiskAssessment(Base):
    """Track risk assessments and management."""
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Risk identification
    risk_category = Column(String(100), nullable=False, index=True)
    risk_source = Column(String(255), nullable=False)
    risk_description = Column(Text)
    
    # Assessment
    risk_level = Column(String(50), nullable=False, index=True)  # critical, high, medium, low
    likelihood_score = Column(Float)  # 0-1
    impact_score = Column(Float)  # 0-1
    
    # Analysis
    risk_factors = Column(JSON, default=list)
    affected_areas = Column(JSON, default=list)
    
    # Mitigation
    mitigation_strategies = Column(JSON, default=list)
    mitigation_status = Column(String(50), default="pending")
    mitigation_effectiveness = Column(Float)
    
    # Context
    assessment_context = Column(JSON, default=dict)
    
    # Tracking
    assessment_date = Column(DateTime, default=datetime.utcnow, index=True)
    assessed_by = Column(String(255))
    last_reviewed = Column(DateTime)
    next_review_date = Column(DateTime)
    
    # Status
    status = Column(String(50), default="active")  # active, mitigated, accepted, closed
    owner = Column(String(255))


class IncidentReport(Base):
    """Track incidents and responses."""
    __tablename__ = "incident_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Incident identification
    incident_id = Column(String(100), unique=True, index=True)
    incident_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(50), nullable=False, index=True)
    
    # Description
    description = Column(Text, nullable=False)
    affected_entities = Column(JSON, default=list)
    incident_context = Column(JSON, default=dict)
    
    # Impact
    impact_description = Column(Text)
    impact_scope = Column(String(255))
    users_affected = Column(Integer)
    
    # Response
    status = Column(String(50), default="reported", index=True)
    priority = Column(String(50))
    assigned_to = Column(String(255))
    response_actions = Column(JSON, default=list)
    action_taken = Column(Text)
    
    # Resolution
    resolution = Column(Text)
    resolution_time_hours = Column(Float)
    root_cause = Column(Text)
    preventive_measures = Column(JSON, default=list)
    
    # Tracking
    reported_at = Column(DateTime, default=datetime.utcnow, index=True)
    reported_by = Column(String(255))
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Follow-up
    requires_follow_up = Column(Boolean, default=False)
    follow_up_actions = Column(JSON, default=list)
    lessons_learned = Column(Text)
