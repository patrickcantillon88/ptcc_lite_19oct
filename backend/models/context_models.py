"""
Context Engineering Database Models for PTCC

Implements context metadata, relevance scoring, relationships,
and validation logging for the Context Engineering system.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship

from ..core.database import Base


class ContextMetadata(Base):
    """Metadata about context elements"""
    __tablename__ = "context_metadata"

    id = Column(Integer, primary_key=True, index=True)
    context_layer_id = Column(Integer, ForeignKey("context_layers.id"), nullable=False)
    
    # Metadata fields
    metadata_key = Column(String, nullable=False)
    metadata_value = Column(JSON)
    data_type = Column(String)  # string, number, boolean, array, object
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_context_metadata_layer', 'context_layer_id'),
        Index('idx_context_metadata_key', 'metadata_key'),
    )


class ContextRelevanceScore(Base):
    """Relevance scores for context in different scenarios"""
    __tablename__ = "context_relevance_scores"

    id = Column(Integer, primary_key=True, index=True)
    context_layer_id = Column(Integer, ForeignKey("context_layers.id"), nullable=False)
    
    # Scenario identification
    scenario_type = Column(String, nullable=False)  # query_type, time_of_day, subject, etc.
    scenario_value = Column(String, nullable=False)
    
    # Relevance metrics
    relevance_score = Column(Float, default=0.5)  # 0.0 to 1.0
    usage_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Performance metrics
    avg_response_time_ms = Column(Integer)
    avg_user_satisfaction = Column(Float)
    
    # Tracking
    first_used = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_context_relevance_layer', 'context_layer_id'),
        Index('idx_context_relevance_scenario', 'scenario_type', 'scenario_value'),
        Index('idx_context_relevance_score', 'relevance_score'),
    )


class ContextRelationship(Base):
    """Relationships between context elements"""
    __tablename__ = "context_relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_layer_id = Column(Integer, ForeignKey("context_layers.id"), nullable=False)
    target_layer_id = Column(Integer, ForeignKey("context_layers.id"), nullable=False)
    
    # Relationship details
    relationship_type = Column(String, nullable=False)  # depends_on, enhances, conflicts_with, relates_to
    relationship_strength = Column(Float, default=0.5)  # 0.0 to 1.0
    bidirectional = Column(Boolean, default=False)
    
    # Context
    description = Column(Text)
    metadata = Column(JSON)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_validated = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_context_relationships_source', 'source_layer_id'),
        Index('idx_context_relationships_target', 'target_layer_id'),
        Index('idx_context_relationships_type', 'relationship_type'),
    )


class ContextValidationLog(Base):
    """Logs for context validation and updates"""
    __tablename__ = "context_validation_logs"

    id = Column(Integer, primary_key=True, index=True)
    context_layer_id = Column(Integer, ForeignKey("context_layers.id"), nullable=False)
    
    # Validation details
    validation_type = Column(String, nullable=False)  # accuracy_check, relevance_check, consistency_check
    validation_status = Column(String, nullable=False)  # passed, failed, warning
    
    # Results
    issues_found = Column(JSON)  # List of issues
    suggestions = Column(JSON)  # List of suggestions
    auto_fix_applied = Column(Boolean, default=False)
    
    # Changes made
    changes_applied = Column(JSON)
    previous_state = Column(JSON)
    new_state = Column(JSON)
    
    # Context
    validator_agent = Column(String)  # Which agent performed validation
    triggered_by = Column(String)  # user_action, scheduled, threshold
    notes = Column(Text)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_context_validation_layer', 'context_layer_id'),
        Index('idx_context_validation_timestamp', 'timestamp'),
        Index('idx_context_validation_status', 'validation_status'),
    )


class ContextEvolutionHistory(Base):
    """History of context evolution and changes"""
    __tablename__ = "context_evolution_history"

    id = Column(Integer, primary_key=True, index=True)
    context_layer_id = Column(Integer, ForeignKey("context_layers.id"), nullable=False)
    
    # Change details
    change_type = Column(String, nullable=False)  # created, updated, deleted, merged, split
    field_changed = Column(String)
    old_value = Column(JSON)
    new_value = Column(JSON)
    
    # Change context
    change_reason = Column(String)  # user_edit, learned_from_interaction, validation, pruning
    confidence_delta = Column(Float)  # Change in confidence score
    
    # Impact assessment
    affected_interactions = Column(Integer, default=0)
    impact_score = Column(Float)  # 0.0 to 1.0
    
    # Tracking
    changed_by = Column(String)  # user, agent, system
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_context_evolution_layer', 'context_layer_id'),
        Index('idx_context_evolution_timestamp', 'timestamp'),
        Index('idx_context_evolution_type', 'change_type'),
    )


class ContextUsageAnalytics(Base):
    """Analytics for context usage patterns"""
    __tablename__ = "context_usage_analytics"

    id = Column(Integer, primary_key=True, index=True)
    context_layer_id = Column(Integer, ForeignKey("context_layers.id"), nullable=False)
    
    # Time period
    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String, nullable=False)  # hourly, daily, weekly, monthly
    
    # Usage metrics
    access_count = Column(Integer, default=0)
    successful_uses = Column(Integer, default=0)
    failed_uses = Column(Integer, default=0)
    
    # Performance metrics
    avg_response_time_ms = Column(Integer)
    avg_relevance_score = Column(Float)
    avg_user_satisfaction = Column(Float)
    
    # Context effectiveness
    queries_benefited = Column(Integer, default=0)
    queries_hindered = Column(Integer, default=0)
    
    # Agent usage
    agents_used_with = Column(JSON)  # Which agents accessed this context
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_context_analytics_layer', 'context_layer_id'),
        Index('idx_context_analytics_date', 'date'),
        Index('idx_context_analytics_period', 'period_type'),
    )
