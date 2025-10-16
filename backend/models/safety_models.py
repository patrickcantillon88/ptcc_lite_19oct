"""
AI Safety & Governance Database Models for PTCC

Implements alignment logs, bias detection, governance metrics, risk assessments,
transparency logs, model factsheets, and compliance tracking.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship

from ..core.database import Base


class AlignmentLog(Base):
    """Logs for AI alignment validation"""
    __tablename__ = "alignment_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Context
    interaction_id = Column(Integer, ForeignKey("interaction_history.id"))
    agent_name = Column(String, nullable=False)
    module_id = Column(String)
    
    # Alignment check details
    check_type = Column(String, nullable=False)  # value_alignment, bias_check, cultural_sensitivity, educational_appropriateness
    check_status = Column(String, nullable=False)  # passed, warning, failed
    
    # Input/Output being checked
    input_text = Column(Text)
    output_text = Column(Text)
    
    # Results
    alignment_score = Column(Float)  # 0.0 to 1.0
    issues_detected = Column(JSON)  # List of issues found
    severity = Column(String)  # low, medium, high, critical
    
    # Actions taken
    action_taken = Column(String)  # allow, modify, block, flag_for_review
    modifications = Column(JSON)  # What was modified
    
    # Educational values assessed
    values_checked = Column(JSON)  # truthfulness, fairness, empathy, cultural_sensitivity
    values_scores = Column(JSON)  # Individual scores for each value
    
    # User feedback
    user_override = Column(Boolean, default=False)
    user_feedback = Column(Text)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_alignment_logs_agent', 'agent_name'),
        Index('idx_alignment_logs_status', 'check_status'),
        Index('idx_alignment_logs_timestamp', 'timestamp'),
        Index('idx_alignment_logs_severity', 'severity'),
    )


class BiasDetectionResult(Base):
    """Results from bias detection analysis"""
    __tablename__ = "bias_detection_results"

    id = Column(Integer, primary_key=True, index=True)
    
    # Context
    alignment_log_id = Column(Integer, ForeignKey("alignment_logs.id"))
    content_analyzed = Column(Text, nullable=False)
    content_type = Column(String)  # input, output, prompt, document
    
    # Bias detection
    bias_types_found = Column(JSON)  # gender, racial, age, cultural, socioeconomic, etc.
    bias_severity = Column(JSON)  # Severity for each bias type
    confidence_scores = Column(JSON)  # Confidence for each detection
    
    # Specific instances
    biased_phrases = Column(JSON)  # Specific phrases identified
    context_markers = Column(JSON)  # Contextual indicators of bias
    
    # Recommendations
    suggested_replacements = Column(JSON)
    mitigation_strategies = Column(JSON)
    
    # Model details
    detection_model = Column(String)
    detection_method = Column(String)  # lexicon_based, ml_model, heuristic
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_bias_detection_timestamp', 'timestamp'),
        Index('idx_bias_detection_content_type', 'content_type'),
    )


class GovernanceMetric(Base):
    """Governance and monitoring metrics"""
    __tablename__ = "governance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    
    # Time period
    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String, nullable=False)  # hourly, daily, weekly, monthly
    
    # Agent/Model being monitored
    agent_name = Column(String, index=True)
    model_name = Column(String)
    
    # Performance metrics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    avg_response_time_ms = Column(Integer)
    
    # Quality metrics
    alignment_pass_rate = Column(Float)  # % of requests passing alignment checks
    bias_detection_rate = Column(Float)  # % of requests with bias detected
    cultural_sensitivity_score = Column(Float)
    educational_appropriateness_score = Column(Float)
    
    # User satisfaction
    avg_user_rating = Column(Float)
    user_override_rate = Column(Float)  # % of times users overrode safety checks
    
    # Compliance
    compliance_status = Column(String)  # compliant, warning, non_compliant
    compliance_issues = Column(JSON)
    
    # Resource usage
    total_token_usage = Column(Integer)
    total_api_calls = Column(Integer)
    estimated_cost = Column(Float)
    
    # Anomalies
    anomaly_count = Column(Integer, default=0)
    anomaly_types = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_governance_metrics_date', 'date'),
        Index('idx_governance_metrics_agent', 'agent_name'),
        Index('idx_governance_metrics_period', 'period_type'),
    )


class RiskAssessment(Base):
    """Risk assessments for AI operations"""
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Context
    assessment_trigger = Column(String, nullable=False)  # scheduled, threshold, event, manual
    agent_name = Column(String)
    operation_type = Column(String)  # query, workflow, automation
    
    # Risk categories assessed
    autonomy_risk_score = Column(Float)  # Risk of AI being too autonomous
    human_agency_risk_score = Column(Float)  # Risk of diminishing human decision-making
    skill_atrophy_risk_score = Column(Float)  # Risk of users losing critical skills
    over_reliance_risk_score = Column(Float)  # Risk of excessive dependence on AI
    
    # Overall assessment
    overall_risk_level = Column(String)  # low, medium, high, critical
    risk_factors = Column(JSON)  # Specific risk factors identified
    
    # Mitigation
    mitigation_recommendations = Column(JSON)
    human_oversight_required = Column(Boolean, default=False)
    autonomy_limits_suggested = Column(JSON)
    
    # Critical thinking promotion
    questions_generated = Column(JSON)  # Questions to promote critical thinking
    verification_prompts = Column(JSON)  # Prompts for users to verify info
    
    # Actions taken
    actions_taken = Column(JSON)
    limits_applied = Column(JSON)
    
    # Follow-up
    requires_follow_up = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    assessed_by = Column(String)  # agent, system, manual

    __table_args__ = (
        Index('idx_risk_assessments_timestamp', 'timestamp'),
        Index('idx_risk_assessments_agent', 'agent_name'),
        Index('idx_risk_assessments_level', 'overall_risk_level'),
    )


class TransparencyLog(Base):
    """Logs for AI transparency and explainability"""
    __tablename__ = "transparency_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Context
    interaction_id = Column(Integer, ForeignKey("interaction_history.id"))
    agent_name = Column(String, nullable=False)
    operation_type = Column(String)
    
    # Reasoning explanation
    reasoning_steps = Column(JSON)  # Step-by-step reasoning process
    decision_points = Column(JSON)  # Key decision points
    alternatives_considered = Column(JSON)  # Alternative approaches considered
    
    # Source attribution
    data_sources_used = Column(JSON)  # Data sources consulted
    context_layers_used = Column(JSON)  # Context layers applied
    knowledge_base_queries = Column(JSON)  # Knowledge base queries made
    
    # Confidence levels
    overall_confidence = Column(Float)  # 0.0 to 1.0
    component_confidence = Column(JSON)  # Confidence for each component
    uncertainty_factors = Column(JSON)  # Sources of uncertainty
    
    # Model details
    model_used = Column(String)
    model_version = Column(String)
    prompt_used = Column(Text)
    parameters_used = Column(JSON)
    
    # Limitations disclosed
    known_limitations = Column(JSON)
    caveats = Column(JSON)
    assumptions_made = Column(JSON)
    
    # User interaction
    explanation_requested = Column(Boolean, default=False)
    user_understood = Column(Boolean)
    user_feedback = Column(Text)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_transparency_logs_agent', 'agent_name'),
        Index('idx_transparency_logs_timestamp', 'timestamp'),
        Index('idx_transparency_logs_interaction', 'interaction_id'),
    )


class ModelFactsheet(Base):
    """Factsheets documenting AI models"""
    __tablename__ = "model_factsheets"

    id = Column(Integer, primary_key=True, index=True)
    
    # Model identification
    model_id = Column(String, unique=True, nullable=False, index=True)
    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    model_provider = Column(String)
    
    # Purpose and capabilities
    intended_use = Column(Text)
    capabilities = Column(JSON)
    limitations = Column(JSON)
    
    # Training data
    training_data_description = Column(Text)
    training_data_sources = Column(JSON)
    training_data_size = Column(String)
    training_cutoff_date = Column(DateTime)
    
    # Performance characteristics
    accuracy_metrics = Column(JSON)
    performance_benchmarks = Column(JSON)
    typical_response_time = Column(String)
    resource_requirements = Column(JSON)
    
    # Ethical considerations
    known_biases = Column(JSON)
    mitigation_strategies = Column(JSON)
    ethical_guidelines = Column(Text)
    prohibited_uses = Column(JSON)
    
    # Usage guidelines
    best_practices = Column(Text)
    recommended_contexts = Column(JSON)
    human_oversight_requirements = Column(Text)
    
    # Compliance
    regulatory_compliance = Column(JSON)  # Which regulations it complies with
    audit_history = Column(JSON)
    
    # Versioning
    changelog = Column(JSON)
    deprecated = Column(Boolean, default=False)
    replacement_model = Column(String)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_model_factsheets_provider', 'model_provider'),
        Index('idx_model_factsheets_deprecated', 'deprecated'),
    )


class ComplianceTracking(Base):
    """Tracking for compliance with educational standards and regulations"""
    __tablename__ = "compliance_tracking"

    id = Column(Integer, primary_key=True, index=True)
    
    # Compliance check details
    compliance_type = Column(String, nullable=False)  # GDPR, FERPA, educational_standards, ethical_guidelines
    compliance_category = Column(String)  # privacy, data_protection, content_appropriateness
    
    # What was checked
    entity_type = Column(String)  # model, agent, workflow, data_storage
    entity_id = Column(String)
    
    # Results
    compliance_status = Column(String, nullable=False)  # compliant, partial, non_compliant
    compliance_score = Column(Float)  # 0.0 to 1.0
    
    # Issues and remediation
    issues_found = Column(JSON)
    severity_levels = Column(JSON)
    remediation_required = Column(Boolean, default=False)
    remediation_actions = Column(JSON)
    
    # Timeline
    check_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    next_check_date = Column(DateTime)
    remediation_deadline = Column(DateTime)
    
    # Auditing
    checked_by = Column(String)  # automated, manual, external_audit
    auditor_notes = Column(Text)
    evidence = Column(JSON)  # Supporting evidence
    
    # Follow-up
    remediation_completed = Column(Boolean, default=False)
    remediation_date = Column(DateTime)
    verification_status = Column(String)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_compliance_tracking_type', 'compliance_type'),
        Index('idx_compliance_tracking_status', 'compliance_status'),
        Index('idx_compliance_tracking_entity', 'entity_type', 'entity_id'),
        Index('idx_compliance_tracking_timestamp', 'timestamp'),
    )
