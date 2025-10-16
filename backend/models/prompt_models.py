"""
Prompt Management Database Models for PTCC

Implements prompt library, versioning, performance tracking, and A/B testing
for the Prompt-Tuning system.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship

from ..core.database import Base


class PromptLibraryItem(Base):
    """Individual prompts in the prompt library"""
    __tablename__ = "prompt_library_items"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"))  # NULL for system prompts
    
    # Prompt identification
    prompt_id = Column(String, unique=True, nullable=False, index=True)
    prompt_name = Column(String, nullable=False)
    prompt_category = Column(String, nullable=False)  # generation, analysis, evaluation, communication, planning
    
    # Prompt details
    prompt_template = Column(Text, nullable=False)  # The actual prompt template
    description = Column(Text)
    purpose = Column(Text)  # What this prompt is for
    
    # Prompt variables
    variables = Column(JSON)  # Variables that can be substituted
    required_variables = Column(JSON)  # Required variables
    optional_variables = Column(JSON)  # Optional variables
    variable_descriptions = Column(JSON)  # Descriptions of variables
    
    # Educational context
    subject_area = Column(String)
    grade_level = Column(String)
    teaching_context = Column(JSON)  # When/where to use this prompt
    
    # Model configuration
    target_model = Column(String)  # Which AI model this is optimized for
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer)
    top_p = Column(Float)
    frequency_penalty = Column(Float)
    presence_penalty = Column(Float)
    stop_sequences = Column(JSON)
    
    # Prompt engineering techniques
    uses_few_shot = Column(Boolean, default=False)
    few_shot_examples = Column(JSON)  # Example inputs/outputs
    uses_chain_of_thought = Column(Boolean, default=False)
    uses_role_prompting = Column(Boolean, default=False)
    role_description = Column(Text)
    
    # Quality and performance
    avg_response_quality = Column(Float)  # Average quality score
    avg_execution_time_ms = Column(Integer)
    avg_token_usage = Column(Integer)
    success_rate = Column(Float)
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    user_rating = Column(Float)  # Average user rating
    
    # Optimization
    is_optimized = Column(Boolean, default=False)
    optimization_history = Column(JSON)  # History of optimizations
    current_version_id = Column(String)  # Current best version
    
    # Status
    status = Column(String, default="active")  # active, testing, archived, deprecated
    is_system_prompt = Column(Boolean, default=False)  # System vs user-created
    is_public = Column(Boolean, default=False)  # Can be shared
    
    # Validation
    validated = Column(Boolean, default=False)
    validation_notes = Column(Text)
    
    # Metadata
    tags = Column(JSON)
    keywords = Column(JSON)
    related_prompts = Column(JSON)  # Related prompt IDs
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    versions = relationship("PromptVersion", back_populates="prompt_item")
    performance_records = relationship("PromptPerformance", back_populates="prompt_item")
    ab_tests = relationship("PromptABTest", foreign_keys="[PromptABTest.control_prompt_id]")

    __table_args__ = (
        Index('idx_prompt_library_user', 'user_profile_id'),
        Index('idx_prompt_library_category', 'prompt_category'),
        Index('idx_prompt_library_status', 'status'),
        Index('idx_prompt_library_subject', 'subject_area'),
    )


class PromptVersion(Base):
    """Versions of prompts for tracking improvements"""
    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(String, ForeignKey("prompt_library_items.prompt_id"), nullable=False)
    
    # Version identification
    version_id = Column(String, unique=True, nullable=False, index=True)
    version_number = Column(String, nullable=False)  # 1.0, 1.1, 2.0, etc.
    version_type = Column(String)  # major, minor, patch
    
    # Version details
    prompt_content = Column(Text, nullable=False)
    changes_made = Column(Text)  # What changed from previous version
    change_rationale = Column(Text)  # Why changes were made
    
    # Configuration for this version
    model_settings = Column(JSON)  # Model parameters for this version
    
    # Performance comparison
    improvement_over_previous = Column(Float)  # % improvement
    metrics_comparison = Column(JSON)  # Detailed metrics vs previous
    
    # Testing
    is_release_candidate = Column(Boolean, default=False)
    is_current_version = Column(Boolean, default=False)
    testing_status = Column(String)  # not_tested, testing, passed, failed
    test_results = Column(JSON)
    
    # Approval
    approved = Column(Boolean, default=False)
    approved_by = Column(String)
    approval_notes = Column(Text)
    
    # Performance tracking
    usage_count = Column(Integer, default=0)
    avg_quality_score = Column(Float)
    avg_response_time_ms = Column(Integer)
    success_rate = Column(Float)
    
    # Rollback
    can_rollback = Column(Boolean, default=True)
    rollback_count = Column(Integer, default=0)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    deployed_at = Column(DateTime)
    deprecated_at = Column(DateTime)
    
    # Relationships
    prompt_item = relationship("PromptLibraryItem", back_populates="versions")

    __table_args__ = (
        Index('idx_prompt_versions_prompt', 'prompt_id'),
        Index('idx_prompt_versions_current', 'is_current_version'),
        Index('idx_prompt_versions_created', 'created_at'),
    )


class PromptPerformance(Base):
    """Performance tracking for individual prompt executions"""
    __tablename__ = "prompt_performance"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(String, ForeignKey("prompt_library_items.prompt_id"), nullable=False)
    version_id = Column(String, ForeignKey("prompt_versions.version_id"))
    
    # Execution details
    execution_id = Column(String, unique=True, nullable=False, index=True)
    execution_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Input
    input_variables = Column(JSON)  # Variables provided
    rendered_prompt = Column(Text)  # Final prompt sent to model
    
    # Context
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"))
    context_layers_used = Column(JSON)
    task_context = Column(JSON)
    
    # Model execution
    model_used = Column(String)
    model_settings = Column(JSON)
    execution_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    cost = Column(Float)
    
    # Output
    response_text = Column(Text)
    response_quality = Column(String)  # poor, fair, good, excellent
    quality_score = Column(Float)  # 0.0 to 1.0
    
    # Success metrics
    execution_successful = Column(Boolean, default=True)
    error_occurred = Column(Boolean, default=False)
    error_message = Column(Text)
    error_type = Column(String)
    
    # Quality assessment
    relevance_score = Column(Float)  # How relevant was the response
    completeness_score = Column(Float)  # How complete was the response
    accuracy_score = Column(Float)  # How accurate was the response
    appropriateness_score = Column(Float)  # Educational appropriateness
    
    # User feedback
    user_rating = Column(Integer)  # 1-5 stars
    user_feedback = Column(Text)
    user_edited_output = Column(Boolean, default=False)
    user_used_output = Column(Boolean)  # Did user actually use it
    
    # AI safety validation
    alignment_check_passed = Column(Boolean)
    bias_detected = Column(Boolean, default=False)
    bias_types = Column(JSON)
    
    # Tracking
    agent_id = Column(String)  # Which agent used this prompt
    workflow_id = Column(String)  # If part of a workflow

    # Relationships
    prompt_item = relationship("PromptLibraryItem", back_populates="performance_records")

    __table_args__ = (
        Index('idx_prompt_performance_prompt', 'prompt_id'),
        Index('idx_prompt_performance_version', 'version_id'),
        Index('idx_prompt_performance_timestamp', 'execution_timestamp'),
        Index('idx_prompt_performance_user', 'user_profile_id'),
    )


class PromptABTest(Base):
    """A/B tests for comparing prompt variants"""
    __tablename__ = "prompt_ab_tests"

    id = Column(Integer, primary_key=True, index=True)
    
    # Test identification
    test_id = Column(String, unique=True, nullable=False, index=True)
    test_name = Column(String, nullable=False)
    test_description = Column(Text)
    
    # Test configuration
    control_prompt_id = Column(String, ForeignKey("prompt_library_items.prompt_id"), nullable=False)
    variant_prompt_ids = Column(JSON, nullable=False)  # List of variant prompt IDs
    
    # Test parameters
    test_type = Column(String, nullable=False)  # quality, speed, cost, user_satisfaction
    test_metrics = Column(JSON, nullable=False)  # Metrics to compare
    traffic_split = Column(JSON)  # Traffic allocation to each variant
    
    # Test duration
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    min_sample_size = Column(Integer, default=100)
    
    # Status
    status = Column(String, default="draft")  # draft, running, paused, completed, cancelled
    
    # Results
    control_metrics = Column(JSON)  # Metrics for control
    variant_metrics = Column(JSON)  # Metrics for each variant
    statistical_significance = Column(JSON)  # Significance tests
    winner_prompt_id = Column(String)  # Which prompt won
    confidence_level = Column(Float)  # Statistical confidence
    
    # Sample sizes
    control_sample_size = Column(Integer, default=0)
    variant_sample_sizes = Column(JSON)  # Sample size for each variant
    
    # Analysis
    analysis_notes = Column(Text)
    key_findings = Column(JSON)
    recommendations = Column(JSON)
    
    # Decision
    decision = Column(String)  # adopt_winner, keep_control, continue_testing, inconclusive
    decision_rationale = Column(Text)
    decision_date = Column(DateTime)
    decided_by = Column(String)
    
    # Implementation
    winner_deployed = Column(Boolean, default=False)
    deployment_date = Column(DateTime)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    control_prompt = relationship("PromptLibraryItem", foreign_keys=[control_prompt_id])

    __table_args__ = (
        Index('idx_prompt_ab_tests_control', 'control_prompt_id'),
        Index('idx_prompt_ab_tests_status', 'status'),
        Index('idx_prompt_ab_tests_start', 'start_date'),
    )


class PromptOptimizationRun(Base):
    """Records of automated prompt optimization attempts"""
    __tablename__ = "prompt_optimization_runs"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(String, ForeignKey("prompt_library_items.prompt_id"), nullable=False)
    
    # Optimization details
    run_id = Column(String, unique=True, nullable=False, index=True)
    optimization_method = Column(String, nullable=False)  # gradient, genetic, llm_assisted, manual
    optimization_goal = Column(String)  # quality, speed, cost, all
    
    # Input
    original_prompt = Column(Text, nullable=False)
    target_metrics = Column(JSON)  # Target performance metrics
    constraints = Column(JSON)  # Optimization constraints
    
    # Process
    iterations = Column(Integer, default=0)
    candidates_generated = Column(Integer, default=0)
    candidates_tested = Column(Integer, default=0)
    
    # Results
    best_prompt = Column(Text)
    best_prompt_metrics = Column(JSON)
    improvement_percentage = Column(Float)
    
    # All candidates
    all_candidates = Column(JSON)  # All prompts tried
    candidate_metrics = Column(JSON)  # Metrics for each
    
    # Status
    status = Column(String, default="running")  # running, completed, failed, cancelled
    success = Column(Boolean)
    
    # Resource usage
    total_time_ms = Column(Integer)
    total_api_calls = Column(Integer)
    total_cost = Column(Float)
    
    # Decision
    deployed = Column(Boolean, default=False)
    deployment_notes = Column(Text)
    
    # Tracking
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    initiated_by = Column(String)  # user, automated, agent

    __table_args__ = (
        Index('idx_prompt_optimization_prompt', 'prompt_id'),
        Index('idx_prompt_optimization_status', 'status'),
        Index('idx_prompt_optimization_started', 'started_at'),
    )


class PromptUsageAnalytics(Base):
    """Aggregated analytics for prompt usage patterns"""
    __tablename__ = "prompt_usage_analytics"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(String, ForeignKey("prompt_library_items.prompt_id"), nullable=False)
    
    # Time period
    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String, nullable=False)  # hourly, daily, weekly, monthly
    
    # Usage metrics
    execution_count = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    
    # Performance metrics
    avg_execution_time_ms = Column(Integer)
    avg_tokens_used = Column(Integer)
    avg_cost = Column(Float)
    total_cost = Column(Float)
    
    # Quality metrics
    avg_quality_score = Column(Float)
    avg_relevance_score = Column(Float)
    avg_user_rating = Column(Float)
    user_satisfaction_rate = Column(Float)  # % of positive ratings
    
    # Usage patterns
    most_common_contexts = Column(JSON)  # Most common use contexts
    most_common_variables = Column(JSON)  # Most used variable combinations
    peak_usage_times = Column(JSON)  # When it's used most
    
    # Effectiveness
    output_used_rate = Column(Float)  # % of times output was used
    edit_rate = Column(Float)  # % of times output was edited
    
    # Issues
    error_rate = Column(Float)
    error_types = Column(JSON)
    
    # Trends
    usage_trend = Column(String)  # increasing, stable, decreasing
    quality_trend = Column(String)  # improving, stable, declining
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_prompt_analytics_prompt', 'prompt_id'),
        Index('idx_prompt_analytics_date', 'date'),
        Index('idx_prompt_analytics_period', 'period_type'),
    )
