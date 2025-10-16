"""
Alignment Database Models for PTCC

Models for value alignment, ethics checking, bias detection,
and cultural sensitivity tracking.
"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from datetime import datetime

from ..core.database import Base


class ValueAlignment(Base):
    """Track value alignment checks."""
    __tablename__ = "value_alignment"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Alignment details
    value_category = Column(String(100), nullable=False, index=True)
    expected_values = Column(JSON, nullable=False)
    actual_alignment_score = Column(Float)
    alignment_level = Column(String(50))  # fully_aligned, mostly_aligned, etc.
    
    # Content
    content_sample = Column(Text)
    context_metadata = Column(JSON, default=dict)
    
    # Analysis
    alignment_details = Column(JSON, default=dict)
    recommendations = Column(JSON, default=list)
    
    # Tracking
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    checked_by = Column(String(255))


class EthicsCheckpoint(Base):
    """Track ethics verification checkpoints."""
    __tablename__ = "ethics_checkpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Checkpoint details
    checkpoint_type = Column(String(100), nullable=False, index=True)
    ethical_principle = Column(String(255), nullable=False)
    
    # Content
    content_sample = Column(Text)
    context_metadata = Column(JSON, default=dict)
    
    # Results
    passed = Column(Boolean, nullable=False)
    issues_identified = Column(JSON, default=list)
    severity_level = Column(String(50))  # low, medium, high, critical
    
    # Details
    check_details = Column(JSON, default=dict)
    mitigation_actions = Column(JSON, default=list)
    
    # Tracking
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)


class BiasDetection(Base):
    """Track bias detection results."""
    __tablename__ = "bias_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Bias details
    bias_type = Column(String(100), nullable=False, index=True)
    content_sample = Column(Text)
    context_metadata = Column(JSON, default=dict)
    
    # Detection results
    detected = Column(Boolean, nullable=False)
    confidence_score = Column(Float)
    bias_indicators = Column(JSON, default=list)
    
    # Mitigation
    mitigation_suggestions = Column(JSON, default=list)
    mitigated = Column(Boolean, default=False)
    mitigation_notes = Column(Text)
    
    # Tracking
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    reviewed_by = Column(String(255))
    reviewed_at = Column(DateTime, nullable=True)


class CulturalSensitivity(Base):
    """Track cultural sensitivity assessments."""
    __tablename__ = "cultural_sensitivity"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Culture details
    culture_category = Column(String(100), nullable=False, index=True)
    content_sample = Column(Text)
    context_metadata = Column(JSON, default=dict)
    
    # Assessment results
    sensitivity_score = Column(Float)
    issues_identified = Column(JSON, default=list)
    strengths_identified = Column(JSON, default=list)
    
    # Recommendations
    recommendations = Column(JSON, default=list)
    best_practices = Column(JSON, default=list)
    
    # Tracking
    assessed_at = Column(DateTime, default=datetime.utcnow, index=True)
    assessed_by = Column(String(255))
