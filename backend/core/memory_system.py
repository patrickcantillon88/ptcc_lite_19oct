"""
Memory System for PTCC

Implements personalized AI memory with user profiling, context management,
interaction tracking, and memory evolution.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .database import SessionLocal
from .logging_config import get_logger
from ..models.memory_models import (
    UserProfile,
    ContextLayer,
    InteractionHistory,
    TeachingPreference,
    StudentDemographic,
    CurriculumContext
)

logger = get_logger("memory_system")


class UserProfileManager:
    """Manages user profiles and preferences."""
    
    def __init__(self):
        self.logger = logger
    
    def get_or_create_profile(
        self,
        user_id: str,
        db: Optional[Session] = None
    ) -> UserProfile:
        """Get existing profile or create new one."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            profile = db.query(UserProfile).filter_by(user_id=user_id).first()
            
            if not profile:
                profile = UserProfile(
                    user_id=user_id,
                    role="teacher"
                )
                db.add(profile)
                db.commit()
                db.refresh(profile)
                self.logger.info(f"Created new user profile for {user_id}")
            
            return profile
            
        finally:
            if should_close:
                db.close()
    
    def update_profile(
        self,
        user_id: str,
        updates: Dict[str, Any],
        db: Optional[Session] = None
    ) -> UserProfile:
        """Update user profile with new information."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            profile = self.get_or_create_profile(user_id, db)
            
            for key, value in updates.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            profile.last_updated = datetime.utcnow()
            db.commit()
            db.refresh(profile)
            
            return profile
            
        finally:
            if should_close:
                db.close()
    
    def get_teaching_preferences(
        self,
        user_id: str,
        category: Optional[str] = None,
        db: Optional[Session] = None
    ) -> List[TeachingPreference]:
        """Get teaching preferences for a user."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            profile = self.get_or_create_profile(user_id, db)
            
            query = db.query(TeachingPreference).filter_by(
                user_profile_id=profile.id
            )
            
            if category:
                query = query.filter_by(preference_category=category)
            
            return query.all()
            
        finally:
            if should_close:
                db.close()


class ContextLayerManager:
    """Manages the 6-layer context system."""
    
    LAYER_TYPES = [
        "base",          # Static information
        "dynamic",       # Current activities
        "historical",    # Past history
        "situational",   # Real-time needs
        "environmental", # Physical constraints
        "philosophical"  # Values and beliefs
    ]
    
    def __init__(self):
        self.logger = logger
    
    def get_context_layers(
        self,
        user_id: str,
        layer_types: Optional[List[str]] = None,
        active_only: bool = True,
        db: Optional[Session] = None
    ) -> Dict[str, ContextLayer]:
        """Get context layers for a user."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            profile_manager = UserProfileManager()
            profile = profile_manager.get_or_create_profile(user_id, db)
            
            query = db.query(ContextLayer).filter_by(
                user_profile_id=profile.id
            )
            
            if active_only:
                query = query.filter_by(active=True)
            
            if layer_types:
                query = query.filter(ContextLayer.layer_type.in_(layer_types))
            
            layers = query.all()
            
            # Return as dictionary keyed by layer_type
            return {layer.layer_type: layer for layer in layers}
            
        finally:
            if should_close:
                db.close()
    
    def update_context_layer(
        self,
        user_id: str,
        layer_type: str,
        layer_data: Dict[str, Any],
        merge: bool = True,
        db: Optional[Session] = None
    ) -> ContextLayer:
        """Update a context layer."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            profile_manager = UserProfileManager()
            profile = profile_manager.get_or_create_profile(user_id, db)
            
            layer = db.query(ContextLayer).filter_by(
                user_profile_id=profile.id,
                layer_type=layer_type
            ).first()
            
            if not layer:
                layer = ContextLayer(
                    user_profile_id=profile.id,
                    layer_type=layer_type,
                    layer_name=f"{layer_type.title()} Context",
                    layer_data=layer_data
                )
                db.add(layer)
            else:
                if merge:
                    # Merge with existing data
                    existing_data = layer.layer_data or {}
                    existing_data.update(layer_data)
                    layer.layer_data = existing_data
                else:
                    # Replace existing data
                    layer.layer_data = layer_data
                
                layer.last_updated = datetime.utcnow()
            
            layer.last_accessed = datetime.utcnow()
            layer.access_count = (layer.access_count or 0) + 1
            
            db.commit()
            db.refresh(layer)
            
            return layer
            
        finally:
            if should_close:
                db.close()
    
    def get_relevant_context(
        self,
        user_id: str,
        query_context: Dict[str, Any],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Get relevant context for a specific query."""
        layers = self.get_context_layers(user_id, db=db)
        
        # Compile relevant context from all layers
        relevant_context = {}
        
        for layer_type, layer in layers.items():
            if layer.layer_data:
                relevant_context[layer_type] = {
                    "data": layer.layer_data,
                    "priority": layer.priority,
                    "last_updated": layer.last_updated.isoformat() if layer.last_updated else None
                }
        
        return relevant_context


class InteractionHistoryTracker:
    """Tracks and manages interaction history."""
    
    def __init__(self):
        self.logger = logger
    
    def log_interaction(
        self,
        user_id: str,
        interaction_type: str,
        query_text: str,
        response_text: str,
        agent_used: Optional[str] = None,
        context_used: Optional[Dict[str, Any]] = None,
        successful: bool = True,
        user_feedback: Optional[str] = None,
        db: Optional[Session] = None
    ) -> InteractionHistory:
        """Log a new interaction."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            profile_manager = UserProfileManager()
            profile = profile_manager.get_or_create_profile(user_id, db)
            
            interaction = InteractionHistory(
                user_profile_id=profile.id,
                interaction_type=interaction_type,
                query_text=query_text,
                response_text=response_text,
                agent_used=agent_used,
                context_used=context_used,
                successful=successful,
                user_feedback=user_feedback
            )
            
            db.add(interaction)
            db.commit()
            db.refresh(interaction)
            
            return interaction
            
        finally:
            if should_close:
                db.close()
    
    def get_recent_interactions(
        self,
        user_id: str,
        limit: int = 10,
        interaction_type: Optional[str] = None,
        db: Optional[Session] = None
    ) -> List[InteractionHistory]:
        """Get recent interactions for a user."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            profile_manager = UserProfileManager()
            profile = profile_manager.get_or_create_profile(user_id, db)
            
            query = db.query(InteractionHistory).filter_by(
                user_profile_id=profile.id
            )
            
            if interaction_type:
                query = query.filter_by(interaction_type=interaction_type)
            
            interactions = query.order_by(
                desc(InteractionHistory.timestamp)
            ).limit(limit).all()
            
            return interactions
            
        finally:
            if should_close:
                db.close()
    
    def analyze_patterns(
        self,
        user_id: str,
        days: int = 30,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Analyze interaction patterns."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            profile_manager = UserProfileManager()
            profile = profile_manager.get_or_create_profile(user_id, db)
            
            interactions = db.query(InteractionHistory).filter(
                InteractionHistory.user_profile_id == profile.id,
                InteractionHistory.timestamp >= cutoff_date
            ).all()
            
            # Analyze patterns
            patterns = {
                "total_interactions": len(interactions),
                "successful_interactions": sum(1 for i in interactions if i.successful),
                "interaction_types": {},
                "agents_used": {},
                "common_queries": [],
                "feedback_summary": {
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0
                }
            }
            
            # Count by type
            for interaction in interactions:
                itype = interaction.interaction_type
                patterns["interaction_types"][itype] = patterns["interaction_types"].get(itype, 0) + 1
                
                if interaction.agent_used:
                    agent = interaction.agent_used
                    patterns["agents_used"][agent] = patterns["agents_used"].get(agent, 0) + 1
                
                if interaction.user_feedback:
                    if interaction.user_feedback in ["positive", "good", "helpful"]:
                        patterns["feedback_summary"]["positive"] += 1
                    elif interaction.user_feedback in ["negative", "bad", "unhelpful"]:
                        patterns["feedback_summary"]["negative"] += 1
                    else:
                        patterns["feedback_summary"]["neutral"] += 1
            
            return patterns
            
        finally:
            if should_close:
                db.close()


class MemoryRetrievalEngine:
    """Engine for retrieving relevant memories."""
    
    def __init__(self):
        self.profile_manager = UserProfileManager()
        self.context_manager = ContextLayerManager()
        self.history_tracker = InteractionHistoryTracker()
        self.logger = logger
    
    def get_complete_context(
        self,
        user_id: str,
        query_context: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Get complete context for a user query."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            # Get user profile
            profile = self.profile_manager.get_or_create_profile(user_id, db)
            
            # Get context layers
            context_layers = self.context_manager.get_relevant_context(
                user_id,
                query_context or {},
                db
            )
            
            # Get recent interactions
            recent_interactions = self.history_tracker.get_recent_interactions(
                user_id,
                limit=5,
                db=db
            )
            
            # Get interaction patterns
            patterns = self.history_tracker.analyze_patterns(
                user_id,
                days=30,
                db=db
            )
            
            # Compile complete context
            complete_context = {
                "user_profile": {
                    "user_id": profile.user_id,
                    "role": profile.role,
                    "instructional_style": profile.instructional_style,
                    "subject_expertise": profile.subject_expertise,
                    "grade_levels": profile.grade_levels,
                    "teaching_philosophy": profile.teaching_philosophy
                },
                "context_layers": context_layers,
                "recent_interactions": [
                    {
                        "type": i.interaction_type,
                        "query": i.query_text[:100],  # Truncate for brevity
                        "successful": i.successful,
                        "timestamp": i.timestamp.isoformat()
                    }
                    for i in recent_interactions
                ],
                "patterns": patterns
            }
            
            return complete_context
            
        finally:
            if should_close:
                db.close()


class MemoryEvolutionEngine:
    """Engine for evolving memory based on interactions."""
    
    def __init__(self):
        self.profile_manager = UserProfileManager()
        self.context_manager = ContextLayerManager()
        self.logger = logger
    
    def learn_from_interaction(
        self,
        user_id: str,
        interaction: InteractionHistory,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Learn from an interaction and update memory."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            updates = {
                "context_updates": [],
                "preference_updates": [],
                "new_insights": []
            }
            
            # Analyze interaction for learnable patterns
            if interaction.successful and interaction.user_feedback == "positive":
                # Update dynamic context with successful strategies
                self.context_manager.update_context_layer(
                    user_id,
                    "dynamic",
                    {
                        "recent_success": {
                            "query": interaction.query_text[:100],
                            "timestamp": interaction.timestamp.isoformat(),
                            "agent": interaction.agent_used
                        }
                    },
                    merge=True,
                    db=db
                )
                updates["context_updates"].append("dynamic")
            
            # Learn from repeated patterns
            if interaction.agent_used:
                # Could update preferences based on agent usage
                updates["new_insights"].append(
                    f"User frequently uses {interaction.agent_used}"
                )
            
            return updates
            
        finally:
            if should_close:
                db.close()
    
    def prune_outdated_context(
        self,
        user_id: str,
        days: int = 90,
        db: Optional[Session] = None
    ) -> int:
        """Remove or archive outdated context."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            profile = self.profile_manager.get_or_create_profile(user_id, db)
            
            # Deactivate old dynamic context layers
            updated_count = db.query(ContextLayer).filter(
                ContextLayer.user_profile_id == profile.id,
                ContextLayer.layer_type == "dynamic",
                ContextLayer.last_updated < cutoff_date
            ).update({"active": False})
            
            db.commit()
            
            return updated_count
            
        finally:
            if should_close:
                db.close()


# Convenience functions
def get_user_context(user_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """Get complete user context."""
    engine = MemoryRetrievalEngine()
    return engine.get_complete_context(user_id, db=db)


def log_user_interaction(
    user_id: str,
    interaction_type: str,
    query: str,
    response: str,
    agent: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    db: Optional[Session] = None
) -> InteractionHistory:
    """Log a user interaction."""
    tracker = InteractionHistoryTracker()
    return tracker.log_interaction(
        user_id,
        interaction_type,
        query,
        response,
        agent_used=agent,
        context_used=context,
        db=db
    )
