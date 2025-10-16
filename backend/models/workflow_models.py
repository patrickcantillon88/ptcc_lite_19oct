"""
Workflow and Generative Computing Database Models for PTCC

Implements workflows, templates, AI modules, executions, and performance metrics
for the Generative Computing Framework.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship

from ..core.database import Base


class Workflow(Base):
    """User-created workflows"""
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # Workflow identification
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # lesson_planning, assessment, grading, communication, research
    tags = Column(JSON)  # List of tags for organization
    
    # Workflow structure
    workflow_definition = Column(JSON, nullable=False)  # Complete workflow structure
    modules = Column(JSON, nullable=False)  # List of module IDs in execution order
    connections = Column(JSON)  # How modules connect
    
    # Configuration
    parameters = Column(JSON)  # Configurable parameters
    default_inputs = Column(JSON)  # Default input values
    
    # Status
    status = Column(String, default="active")  # active, archived, template
    version = Column(String, default="1.0.0")
    is_public = Column(Boolean, default=False)  # Share with other users
    
    # Performance tracking
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    avg_execution_time_ms = Column(Integer)
    avg_user_rating = Column(Float)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    executions = relationship("WorkflowExecution", back_populates="workflow")

    __table_args__ = (
        Index('idx_workflows_user', 'user_profile_id'),
        Index('idx_workflows_category', 'category'),
        Index('idx_workflows_status', 'status'),
    )


class WorkflowTemplate(Base):
    """Pre-built workflow templates"""
    __tablename__ = "workflow_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Template identification
    name = Column(String, nullable=False, unique=True)
    display_name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)
    tags = Column(JSON)
    
    # Template structure
    template_definition = Column(JSON, nullable=False)
    modules = Column(JSON, nullable=False)
    connections = Column(JSON)
    
    # Configuration
    configurable_parameters = Column(JSON)
    required_inputs = Column(JSON)
    optional_inputs = Column(JSON)
    
    # Documentation
    usage_guide = Column(Text)
    example_inputs = Column(JSON)
    example_outputs = Column(JSON)
    
    # Metadata
    difficulty_level = Column(String)  # beginner, intermediate, advanced
    estimated_time = Column(String)  # "2 minutes", "5-10 minutes"
    prerequisites = Column(JSON)  # List of required data or context
    
    # Status
    is_active = Column(Boolean, default=True)
    version = Column(String, default="1.0.0")
    
    # Statistics
    usage_count = Column(Integer, default=0)
    avg_success_rate = Column(Float)
    avg_user_rating = Column(Float)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_workflow_templates_category', 'category'),
        Index('idx_workflow_templates_active', 'is_active'),
    )


class AIModule(Base):
    """AI modules that can be used in workflows"""
    __tablename__ = "ai_modules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Module identification
    module_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # generation, analysis, transformation, validation
    
    # Module specification
    input_schema = Column(JSON, nullable=False)
    output_schema = Column(JSON, nullable=False)
    configuration_schema = Column(JSON)
    
    # AI model details
    model_provider = Column(String)  # gemini, openai, local
    model_name = Column(String)
    prompt_template = Column(Text)
    
    # Capabilities
    supports_streaming = Column(Boolean, default=False)
    supports_batch = Column(Boolean, default=False)
    max_input_tokens = Column(Integer)
    max_output_tokens = Column(Integer)
    
    # Performance
    avg_execution_time_ms = Column(Integer)
    avg_token_usage = Column(Integer)
    success_rate = Column(Float)
    
    # Status
    is_active = Column(Boolean, default=True)
    version = Column(String, default="1.0.0")
    
    # Documentation
    usage_examples = Column(JSON)
    best_practices = Column(Text)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_ai_modules_category', 'category'),
        Index('idx_ai_modules_provider', 'model_provider'),
    )


class WorkflowExecution(Base):
    """Log of workflow executions"""
    __tablename__ = "workflow_executions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # Execution details
    execution_status = Column(String, nullable=False)  # running, completed, failed, cancelled
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)
    execution_time_ms = Column(Integer)
    
    # Input/Output
    inputs = Column(JSON)
    outputs = Column(JSON)
    intermediate_results = Column(JSON)  # Results from each module
    
    # Execution context
    context_used = Column(JSON)  # Context layers applied
    modules_executed = Column(JSON)  # List of modules and their status
    
    # Error handling
    error_message = Column(Text)
    error_module = Column(String)  # Which module failed
    retry_count = Column(Integer, default=0)
    
    # User feedback
    user_rating = Column(Integer)  # 1-5 stars
    user_feedback = Column(Text)
    output_used = Column(Boolean)  # Did user actually use the output
    
    # Performance metrics
    token_usage = Column(Integer)
    api_calls_made = Column(Integer)
    cost_estimate = Column(Float)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")

    __table_args__ = (
        Index('idx_workflow_executions_workflow', 'workflow_id'),
        Index('idx_workflow_executions_user', 'user_profile_id'),
        Index('idx_workflow_executions_status', 'execution_status'),
        Index('idx_workflow_executions_created', 'created_at'),
    )


class ModulePerformanceMetric(Base):
    """Performance metrics for AI modules"""
    __tablename__ = "module_performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(String, ForeignKey("ai_modules.module_id"), nullable=False)
    
    # Time period
    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String, nullable=False)  # hourly, daily, weekly, monthly
    
    # Usage metrics
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Performance metrics
    avg_execution_time_ms = Column(Integer)
    min_execution_time_ms = Column(Integer)
    max_execution_time_ms = Column(Integer)
    avg_token_usage = Column(Integer)
    
    # Quality metrics
    avg_user_rating = Column(Float)
    output_used_count = Column(Integer)  # How many times output was actually used
    
    # Resource usage
    total_api_calls = Column(Integer, default=0)
    total_cost_estimate = Column(Float)
    
    # Error analysis
    error_types = Column(JSON)  # Breakdown of error types
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_module_performance_module', 'module_id'),
        Index('idx_module_performance_date', 'date'),
        Index('idx_module_performance_period', 'period_type'),
    )
