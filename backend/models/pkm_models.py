"""
Personal Knowledge Management Database Models for PTCC

Implements knowledge items, connections, tags, and synthesis
for the PKM system that organizes and connects the user's personal knowledge base.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship

from ..core.database import Base


class KnowledgeItem(Base):
    """Individual knowledge items in the personal knowledge base"""
    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # Item identification
    item_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    item_type = Column(String, nullable=False)  # note, resource, concept, practice, insight, question
    
    # Content
    content = Column(Text, nullable=False)
    summary = Column(Text)  # AI-generated summary
    key_points = Column(JSON)  # Extracted key points
    
    # Source
    source_type = Column(String)  # reading, experience, training, conversation, research
    source_reference = Column(String)  # URL, book title, document path, etc.
    source_date = Column(DateTime)
    
    # Categorization
    subject_area = Column(String)  # Subject/domain this relates to
    topic = Column(String)  # Specific topic
    subtopic = Column(String)
    grade_level = Column(String)  # If grade-specific
    
    # Educational context
    related_standards = Column(JSON)  # Educational standards
    related_objectives = Column(JSON)  # Learning objectives
    practical_applications = Column(JSON)  # How to apply this
    
    # Quality and relevance
    relevance_score = Column(Float, default=0.5)  # How relevant to user's practice
    quality_score = Column(Float)  # Quality of the knowledge item
    confidence_level = Column(Float)  # User's confidence in this knowledge
    
    # Usage
    times_referenced = Column(Integer, default=0)
    last_referenced = Column(DateTime)
    applied_in_practice = Column(Boolean, default=False)
    effectiveness_rating = Column(Float)  # How effective when applied
    
    # Status
    status = Column(String, default="active")  # active, archived, draft
    visibility = Column(String, default="private")  # private, shared, public
    
    # Metadata
    tags = Column(JSON)  # List of tag IDs
    keywords = Column(JSON)  # Searchable keywords
    language = Column(String, default="en")
    
    # Vector embedding for semantic search
    embedding_vector = Column(Text)  # Stored as JSON array
    embedding_model = Column(String)  # Which model generated the embedding
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_reviewed = Column(DateTime)
    review_frequency_days = Column(Integer)  # How often to review this
    
    # Relationships
    connections = relationship("KnowledgeConnection",
                             foreign_keys="[KnowledgeConnection.source_item_id]",
                             back_populates="source_item")
    syntheses = relationship("KnowledgeSynthesis",
                           secondary="knowledge_synthesis_items",
                           back_populates="knowledge_items")

    __table_args__ = (
        Index('idx_knowledge_items_user', 'user_profile_id'),
        Index('idx_knowledge_items_type', 'item_type'),
        Index('idx_knowledge_items_subject', 'subject_area'),
        Index('idx_knowledge_items_status', 'status'),
        Index('idx_knowledge_items_created', 'created_at'),
    )


class KnowledgeConnection(Base):
    """Connections between knowledge items"""
    __tablename__ = "knowledge_connections"

    id = Column(Integer, primary_key=True, index=True)
    
    # Connected items
    source_item_id = Column(String, ForeignKey("knowledge_items.item_id"), nullable=False)
    target_item_id = Column(String, ForeignKey("knowledge_items.item_id"), nullable=False)
    
    # Connection type
    connection_type = Column(String, nullable=False)  # relates_to, builds_on, contradicts, supports, applies_to, example_of
    connection_strength = Column(Float, default=0.5)  # 0.0 to 1.0
    bidirectional = Column(Boolean, default=False)
    
    # Connection details
    description = Column(Text)  # Why/how they're connected
    context = Column(JSON)  # Additional context
    
    # Discovery
    discovered_by = Column(String)  # user, ai, system
    discovery_method = Column(String)  # manual, semantic_similarity, co_occurrence, inference
    
    # Quality
    confidence_score = Column(Float, default=0.5)  # Confidence in this connection
    validated = Column(Boolean, default=False)
    validated_by = Column(String)  # user or agent
    
    # Usage
    times_traversed = Column(Integer, default=0)  # How often this connection is used
    usefulness_score = Column(Float)  # User rating of usefulness
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_traversed = Column(DateTime)
    
    # Relationships
    source_item = relationship("KnowledgeItem", foreign_keys=[source_item_id])

    __table_args__ = (
        Index('idx_knowledge_connections_source', 'source_item_id'),
        Index('idx_knowledge_connections_target', 'target_item_id'),
        Index('idx_knowledge_connections_type', 'connection_type'),
        Index('idx_knowledge_connections_active', 'is_active'),
    )


class KnowledgeTag(Base):
    """Tags for organizing knowledge items"""
    __tablename__ = "knowledge_tags"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # Tag identification
    tag_id = Column(String, unique=True, nullable=False, index=True)
    tag_name = Column(String, nullable=False)
    tag_type = Column(String)  # subject, topic, method, resource_type, etc.
    
    # Hierarchy
    parent_tag_id = Column(String, ForeignKey("knowledge_tags.tag_id"))
    is_root_tag = Column(Boolean, default=False)
    hierarchy_level = Column(Integer, default=0)
    
    # Description
    description = Column(Text)
    color = Column(String)  # For UI visualization
    icon = Column(String)  # Icon identifier
    
    # Usage
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # AI-generated metadata
    related_concepts = Column(JSON)  # AI-identified related concepts
    suggested_resources = Column(JSON)  # AI-suggested resources
    
    # Status
    is_active = Column(Boolean, default=True)
    is_system_tag = Column(Boolean, default=False)  # System-created vs user-created
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_knowledge_tags_user', 'user_profile_id'),
        Index('idx_knowledge_tags_parent', 'parent_tag_id'),
        Index('idx_knowledge_tags_active', 'is_active'),
    )


class KnowledgeSynthesis(Base):
    """AI-generated syntheses combining multiple knowledge items"""
    __tablename__ = "knowledge_syntheses"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # Synthesis identification
    synthesis_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    synthesis_type = Column(String, nullable=False)  # overview, comparison, integration, analysis, recommendation
    
    # Content
    synthesis_content = Column(Text, nullable=False)  # The synthesized knowledge
    executive_summary = Column(Text)
    key_insights = Column(JSON)  # Main insights from synthesis
    
    # Source items
    source_item_count = Column(Integer, default=0)
    source_item_ids = Column(JSON)  # IDs of knowledge items used
    
    # Synthesis details
    synthesis_method = Column(String)  # How synthesis was created
    synthesis_model = Column(String)  # AI model used
    synthesis_prompt = Column(Text)  # Prompt used for generation
    
    # Context
    synthesis_context = Column(JSON)  # Context for synthesis (subject, grade, etc.)
    intended_use = Column(String)  # What this synthesis is for
    
    # Quality
    confidence_score = Column(Float)  # AI confidence in synthesis
    quality_score = Column(Float)  # Quality assessment
    user_rating = Column(Integer)  # User rating 1-5
    
    # Validation
    validated = Column(Boolean, default=False)
    validation_notes = Column(Text)
    
    # Applications
    practical_applications = Column(JSON)  # How to apply this synthesis
    related_teaching_strategies = Column(JSON)
    recommended_resources = Column(JSON)
    
    # Usage
    times_referenced = Column(Integer, default=0)
    last_referenced = Column(DateTime)
    applied_in_practice = Column(Boolean, default=False)
    
    # Status
    status = Column(String, default="active")  # active, archived, draft
    visibility = Column(String, default="private")
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    knowledge_items = relationship("KnowledgeItem",
                                 secondary="knowledge_synthesis_items",
                                 back_populates="syntheses")

    __table_args__ = (
        Index('idx_knowledge_syntheses_user', 'user_profile_id'),
        Index('idx_knowledge_syntheses_type', 'synthesis_type'),
        Index('idx_knowledge_syntheses_status', 'status'),
        Index('idx_knowledge_syntheses_created', 'created_at'),
    )


class KnowledgeSynthesisItem(Base):
    """Association table between syntheses and knowledge items"""
    __tablename__ = "knowledge_synthesis_items"

    synthesis_id = Column(String, ForeignKey("knowledge_syntheses.synthesis_id"), primary_key=True)
    item_id = Column(String, ForeignKey("knowledge_items.item_id"), primary_key=True)
    
    # Relationship details
    relevance_to_synthesis = Column(Float)  # How relevant this item is to synthesis
    contribution_type = Column(String)  # supporting, contrasting, foundational, example
    specific_contribution = Column(Text)  # What specifically this item contributed
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_synthesis_items_synthesis', 'synthesis_id'),
        Index('idx_synthesis_items_item', 'item_id'),
    )


class KnowledgeInsight(Base):
    """AI-generated insights from knowledge patterns"""
    __tablename__ = "knowledge_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    
    # Insight details
    insight_type = Column(String, nullable=False)  # pattern, gap, opportunity, trend, recommendation
    insight_title = Column(String, nullable=False)
    insight_content = Column(Text, nullable=False)
    
    # Related knowledge
    related_item_ids = Column(JSON)  # Knowledge items this insight is based on
    related_tag_ids = Column(JSON)  # Tags related to this insight
    
    # Context
    subject_area = Column(String)
    topic = Column(String)
    context = Column(JSON)
    
    # Quality
    confidence_score = Column(Float)
    actionability_score = Column(Float)  # How actionable is this insight
    impact_potential = Column(String)  # high, medium, low
    
    # Actions
    suggested_actions = Column(JSON)  # Suggested next steps
    action_taken = Column(Boolean, default=False)
    action_details = Column(JSON)
    
    # Status
    status = Column(String, default="new")  # new, acknowledged, acting_on, completed, dismissed
    dismissed = Column(Boolean, default=False)
    dismissal_reason = Column(Text)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime)
    completed_at = Column(DateTime)

    __table_args__ = (
        Index('idx_knowledge_insights_user', 'user_profile_id'),
        Index('idx_knowledge_insights_type', 'insight_type'),
        Index('idx_knowledge_insights_status', 'status'),
        Index('idx_knowledge_insights_created', 'created_at'),
    )
