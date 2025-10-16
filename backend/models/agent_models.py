"""
Agent Management Database Models for PTCC

Implements agent registry, task management, inter-agent communication,
and performance metrics for the multi-agent system.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship

from ..core.database import Base


class AgentRegistry(Base):
    """Registry of all agents in the system"""
    __tablename__ = "agent_registry"

    id = Column(Integer, primary_key=True, index=True)
    
    # Agent identification
    agent_id = Column(String, unique=True, nullable=False, index=True)
    agent_name = Column(String, nullable=False)
    agent_type = Column(String, nullable=False)  # educational, context, workflow, safety, support
    agent_category = Column(String)  # planning, curriculum, student_analysis, etc.
    
    # Agent capabilities
    capabilities = Column(JSON, nullable=False)  # List of capabilities
    input_schema = Column(JSON)  # Expected input format
    output_schema = Column(JSON)  # Output format
    
    # Dependencies
    depends_on_agents = Column(JSON)  # List of agent IDs this agent depends on
    can_coordinate_with = Column(JSON)  # Agents this can work with
    requires_context_layers = Column(JSON)  # Required context layers
    
    # Configuration
    configuration = Column(JSON)  # Agent-specific configuration
    priority = Column(Integer, default=5)  # Execution priority 1-10
    max_concurrent_tasks = Column(Integer, default=5)
    
    # AI model details
    model_provider = Column(String)  # gemini, openai, local, etc.
    model_name = Column(String)
    prompt_template_id = Column(String)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_enabled = Column(Boolean, default=True)
    version = Column(String, default="1.0.0")
    
    # Performance
    avg_execution_time_ms = Column(Integer)
    success_rate = Column(Float)
    total_executions = Column(Integer, default=0)
    
    # Metadata
    description = Column(Text)
    documentation_url = Column(String)
    owner = Column(String)  # Which team/person maintains this agent
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_health_check = Column(DateTime)
    
    # Relationships
    tasks = relationship("AgentTask", back_populates="agent")
    performance_metrics = relationship("AgentPerformanceMetric", back_populates="agent")

    __table_args__ = (
        Index('idx_agent_registry_type', 'agent_type'),
        Index('idx_agent_registry_category', 'agent_category'),
        Index('idx_agent_registry_active', 'is_active'),
    )


class AgentTask(Base):
    """Tasks assigned to and executed by agents"""
    __tablename__ = "agent_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, nullable=False, index=True)
    agent_id = Column(String, ForeignKey("agent_registry.agent_id"), nullable=False)
    
    # Task details
    task_type = Column(String, nullable=False)  # analyze, generate, validate, coordinate, etc.
    task_description = Column(Text)
    priority = Column(Integer, default=5)  # 1-10, higher = more urgent
    
    # Input/Output
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON)
    intermediate_results = Column(JSON)  # Results from subtasks
    
    # Context
    context_layers_used = Column(JSON)  # Which context layers were applied
    memory_accessed = Column(JSON)  # Memory items accessed
    related_tasks = Column(JSON)  # Related task IDs
    
    # Execution
    status = Column(String, default="pending")  # pending, running, completed, failed, cancelled
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    execution_time_ms = Column(Integer)
    
    # Parent/Child relationships
    parent_task_id = Column(String, ForeignKey("agent_tasks.task_id"))
    is_subtask = Column(Boolean, default=False)
    subtask_count = Column(Integer, default=0)
    
    # Collaboration
    coordinating_agent_id = Column(String)  # If part of multi-agent coordination
    collaboration_context = Column(JSON)  # Context for agent collaboration
    
    # Error handling
    error_message = Column(Text)
    error_type = Column(String)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Quality
    confidence_score = Column(Float)  # Agent's confidence in the result
    quality_score = Column(Float)  # Quality assurance score
    user_feedback = Column(String)  # User feedback on result
    
    # Resource usage
    tokens_used = Column(Integer)
    api_calls_made = Column(Integer)
    cost_estimate = Column(Float)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_by = Column(String)  # user or system
    
    # Relationships
    agent = relationship("AgentRegistry", back_populates="tasks")
    communications = relationship("AgentCommunicationLog", back_populates="task")

    __table_args__ = (
        Index('idx_agent_tasks_agent', 'agent_id'),
        Index('idx_agent_tasks_status', 'status'),
        Index('idx_agent_tasks_created', 'created_at'),
        Index('idx_agent_tasks_parent', 'parent_task_id'),
    )


class AgentCommunicationLog(Base):
    """Logs of communication between agents"""
    __tablename__ = "agent_communication_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Communication parties
    sender_agent_id = Column(String, ForeignKey("agent_registry.agent_id"), nullable=False)
    receiver_agent_id = Column(String, ForeignKey("agent_registry.agent_id"), nullable=False)
    
    # Context
    task_id = Column(String, ForeignKey("agent_tasks.task_id"))
    communication_type = Column(String, nullable=False)  # request, response, notification, query, coordination
    
    # Message
    message_type = Column(String)  # data_request, task_delegation, status_update, error_notification
    message_content = Column(JSON, nullable=False)
    message_priority = Column(Integer, default=5)
    
    # Response
    requires_response = Column(Boolean, default=False)
    response_received = Column(Boolean, default=False)
    response_time_ms = Column(Integer)
    response_content = Column(JSON)
    
    # Coordination
    coordination_session_id = Column(String)  # Groups related communications
    sequence_number = Column(Integer)  # Order in conversation
    
    # Status
    status = Column(String, default="sent")  # sent, received, processed, failed
    success = Column(Boolean, default=True)
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Tracking
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    processed_at = Column(DateTime)
    
    # Relationships
    task = relationship("AgentTask", back_populates="communications")

    __table_args__ = (
        Index('idx_agent_comm_sender', 'sender_agent_id'),
        Index('idx_agent_comm_receiver', 'receiver_agent_id'),
        Index('idx_agent_comm_task', 'task_id'),
        Index('idx_agent_comm_timestamp', 'timestamp'),
        Index('idx_agent_comm_session', 'coordination_session_id'),
    )


class AgentPerformanceMetric(Base):
    """Performance metrics for agents over time"""
    __tablename__ = "agent_performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agent_registry.agent_id"), nullable=False)
    
    # Time period
    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String, nullable=False)  # hourly, daily, weekly, monthly
    
    # Execution metrics
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    cancelled_tasks = Column(Integer, default=0)
    
    # Performance metrics
    avg_execution_time_ms = Column(Integer)
    min_execution_time_ms = Column(Integer)
    max_execution_time_ms = Column(Integer)
    median_execution_time_ms = Column(Integer)
    
    # Quality metrics
    avg_confidence_score = Column(Float)
    avg_quality_score = Column(Float)
    user_satisfaction_rate = Column(Float)  # % of positive feedback
    
    # Resource usage
    total_tokens_used = Column(Integer)
    total_api_calls = Column(Integer)
    total_cost = Column(Float)
    avg_cost_per_task = Column(Float)
    
    # Collaboration metrics
    tasks_requiring_coordination = Column(Integer, default=0)
    successful_coordinations = Column(Integer, default=0)
    coordination_efficiency = Column(Float)  # Success rate of coordinations
    
    # Error analysis
    error_types = Column(JSON)  # Breakdown of error types
    error_rate = Column(Float)  # % of tasks that failed
    avg_retry_count = Column(Float)
    
    # Context usage
    context_layers_accessed = Column(JSON)  # Which context layers were used
    context_effectiveness = Column(Float)  # How effective was context
    
    # Health indicators
    health_status = Column(String)  # healthy, degraded, unhealthy
    health_score = Column(Float)  # 0.0 to 1.0
    anomalies_detected = Column(Integer, default=0)
    
    # Trends
    performance_trend = Column(String)  # improving, stable, degrading
    usage_trend = Column(String)  # increasing, stable, decreasing
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("AgentRegistry", back_populates="performance_metrics")

    __table_args__ = (
        Index('idx_agent_performance_agent', 'agent_id'),
        Index('idx_agent_performance_date', 'date'),
        Index('idx_agent_performance_period', 'period_type'),
        Index('idx_agent_performance_health', 'health_status'),
    )


class AgentCoordinationSession(Base):
    """Sessions where multiple agents coordinate on complex tasks"""
    __tablename__ = "agent_coordination_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    
    # Session details
    session_type = Column(String, nullable=False)  # multi_agent_workflow, collaborative_analysis, etc.
    session_description = Column(Text)
    
    # Participating agents
    coordinator_agent_id = Column(String, ForeignKey("agent_registry.agent_id"), nullable=False)
    participant_agent_ids = Column(JSON, nullable=False)  # List of participating agent IDs
    
    # Tasks
    primary_task_id = Column(String, ForeignKey("agent_tasks.task_id"))
    related_task_ids = Column(JSON)  # All related task IDs
    
    # Execution
    status = Column(String, default="active")  # active, completed, failed, cancelled
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    total_duration_ms = Column(Integer)
    
    # Coordination metrics
    total_messages = Column(Integer, default=0)
    coordination_efficiency = Column(Float)  # How well agents coordinated
    parallel_execution_achieved = Column(Boolean, default=False)
    
    # Results
    session_results = Column(JSON)
    success = Column(Boolean)
    failure_reason = Column(Text)
    
    # Context
    context_shared = Column(JSON)  # Context shared among agents
    memory_accessed = Column(JSON)  # Shared memory access
    
    # Quality
    overall_quality_score = Column(Float)
    user_satisfaction = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_coordination_coordinator', 'coordinator_agent_id'),
        Index('idx_coordination_status', 'status'),
        Index('idx_coordination_created', 'created_at'),
    )
