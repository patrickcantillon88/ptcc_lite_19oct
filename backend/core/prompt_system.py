"""
Prompt Management System for PTCC

Implements prompt library management, versioning, A/B testing,
optimization, and performance tracking.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import uuid

from .database import SessionLocal
from .logging_config import get_logger
from ..models.prompt_models import (
    PromptLibraryItem,
    PromptVersion,
    PromptPerformance,
    PromptABTest,
    PromptOptimizationRun,
    PromptUsageAnalytics
)

logger = get_logger("prompt_system")


class PromptLibraryManager:
    """Manages the prompt library and templates."""
    
    def __init__(self):
        self.logger = logger
    
    def create_prompt(
        self,
        prompt_name: str,
        prompt_category: str,
        prompt_template: str,
        description: str,
        variables: List[str],
        user_id: Optional[str] = None,
        subject_area: Optional[str] = None,
        grade_level: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None
    ) -> PromptLibraryItem:
        """Create a new prompt in the library."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            prompt_id = f"prompt_{uuid.uuid4().hex[:12]}"
            
            prompt = PromptLibraryItem(
                prompt_id=prompt_id,
                prompt_name=prompt_name,
                prompt_category=prompt_category,
                prompt_template=prompt_template,
                description=description,
                variables={"all": variables},
                required_variables=variables,
                subject_area=subject_area,
                grade_level=grade_level,
                created_by=user_id,
                status="active"
            )
            
            # Apply model configuration if provided
            if model_config:
                prompt.temperature = model_config.get("temperature", 0.7)
                prompt.max_tokens = model_config.get("max_tokens")
                prompt.top_p = model_config.get("top_p")
                prompt.frequency_penalty = model_config.get("frequency_penalty")
                prompt.presence_penalty = model_config.get("presence_penalty")
            
            db.add(prompt)
            db.commit()
            db.refresh(prompt)
            
            # Create initial version
            self._create_version(prompt, "1.0.0", "Initial version", user_id, db)
            
            self.logger.info(f"Created prompt: {prompt_name} ({prompt_id})")
            return prompt
            
        finally:
            if should_close:
                db.close()
    
    def _create_version(
        self,
        prompt: PromptLibraryItem,
        version_number: str,
        changes: str,
        user_id: Optional[str],
        db: Session
    ) -> PromptVersion:
        """Create a new version of a prompt."""
        version_id = f"{prompt.prompt_id}_v{version_number}"
        
        # Mark previous versions as not current
        db.query(PromptVersion).filter_by(
            prompt_id=prompt.prompt_id,
            is_current_version=True
        ).update({"is_current_version": False})
        
        version = PromptVersion(
            prompt_id=prompt.prompt_id,
            version_id=version_id,
            version_number=version_number,
            prompt_content=prompt.prompt_template,
            changes_made=changes,
            is_current_version=True,
            created_by=user_id
        )
        
        db.add(version)
        db.commit()
        
        return version
    
    def get_prompt(
        self,
        prompt_id: str,
        db: Optional[Session] = None
    ) -> Optional[PromptLibraryItem]:
        """Get a prompt by ID."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            return db.query(PromptLibraryItem).filter_by(
                prompt_id=prompt_id
            ).first()
            
        finally:
            if should_close:
                db.close()
    
    def search_prompts(
        self,
        category: Optional[str] = None,
        subject_area: Optional[str] = None,
        grade_level: Optional[str] = None,
        search_text: Optional[str] = None,
        status: str = "active",
        db: Optional[Session] = None
    ) -> List[PromptLibraryItem]:
        """Search for prompts in the library."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            query = db.query(PromptLibraryItem).filter_by(status=status)
            
            if category:
                query = query.filter_by(prompt_category=category)
            
            if subject_area:
                query = query.filter_by(subject_area=subject_area)
            
            if grade_level:
                query = query.filter_by(grade_level=grade_level)
            
            if search_text:
                query = query.filter(
                    (PromptLibraryItem.prompt_name.contains(search_text)) |
                    (PromptLibraryItem.description.contains(search_text))
                )
            
            return query.all()
            
        finally:
            if should_close:
                db.close()
    
    def update_prompt(
        self,
        prompt_id: str,
        updates: Dict[str, Any],
        user_id: Optional[str] = None,
        create_version: bool = False,
        db: Optional[Session] = None
    ) -> Optional[PromptLibraryItem]:
        """Update a prompt."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            prompt = self.get_prompt(prompt_id, db)
            
            if not prompt:
                return None
            
            # If updating template and create_version is True
            if "prompt_template" in updates and create_version:
                current_version = db.query(PromptVersion).filter_by(
                    prompt_id=prompt_id,
                    is_current_version=True
                ).first()
                
                # Increment version
                if current_version:
                    parts = current_version.version_number.split(".")
                    new_version = f"{parts[0]}.{int(parts[1]) + 1}.0"
                else:
                    new_version = "1.0.0"
                
                self._create_version(
                    prompt,
                    new_version,
                    updates.get("change_notes", "Updated prompt template"),
                    user_id,
                    db
                )
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(prompt, key) and key != "prompt_id":
                    setattr(prompt, key, value)
            
            db.commit()
            db.refresh(prompt)
            
            return prompt
            
        finally:
            if should_close:
                db.close()


class PromptRenderer:
    """Renders prompt templates with variables."""
    
    def __init__(self):
        self.logger = logger
    
    def render(
        self,
        prompt_template: str,
        variables: Dict[str, Any]
    ) -> str:
        """Render a prompt template with provided variables."""
        try:
            # Simple variable substitution
            rendered = prompt_template
            
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"  # {{variable_name}}
                rendered = rendered.replace(placeholder, str(value))
            
            # Check for unsubstituted variables
            if "{{" in rendered and "}}" in rendered:
                self.logger.warning("Unsubstituted variables found in rendered prompt")
            
            return rendered
            
        except Exception as e:
            self.logger.error(f"Error rendering prompt: {e}")
            return prompt_template


class PromptPerformanceTracker:
    """Tracks and analyzes prompt performance."""
    
    def __init__(self):
        self.logger = logger
    
    def log_execution(
        self,
        prompt_id: str,
        version_id: Optional[str],
        rendered_prompt: str,
        input_variables: Dict[str, Any],
        response_text: str,
        execution_time_ms: int,
        tokens_used: int,
        quality_score: Optional[float] = None,
        user_id: Optional[str] = None,
        successful: bool = True,
        db: Optional[Session] = None
    ) -> PromptPerformance:
        """Log a prompt execution for performance tracking."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            execution_id = f"exec_{uuid.uuid4().hex[:12]}"
            
            performance = PromptPerformance(
                prompt_id=prompt_id,
                version_id=version_id,
                execution_id=execution_id,
                input_variables=input_variables,
                rendered_prompt=rendered_prompt,
                response_text=response_text,
                execution_time_ms=execution_time_ms,
                tokens_used=tokens_used,
                quality_score=quality_score,
                execution_successful=successful
            )
            
            db.add(performance)
            
            # Update prompt usage statistics
            prompt = db.query(PromptLibraryItem).filter_by(
                prompt_id=prompt_id
            ).first()
            
            if prompt:
                prompt.usage_count = (prompt.usage_count or 0) + 1
                prompt.last_used = datetime.utcnow()
                
                # Update average metrics
                if quality_score:
                    current_avg = prompt.avg_response_quality or 0
                    count = prompt.usage_count
                    prompt.avg_response_quality = (
                        (current_avg * (count - 1) + quality_score) / count
                    )
            
            db.commit()
            db.refresh(performance)
            
            return performance
            
        finally:
            if should_close:
                db.close()
    
    def get_performance_metrics(
        self,
        prompt_id: str,
        days: int = 30,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Get aggregated performance metrics for a prompt."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            executions = db.query(PromptPerformance).filter(
                PromptPerformance.prompt_id == prompt_id,
                PromptPerformance.execution_timestamp >= cutoff_date
            ).all()
            
            if not executions:
                return {
                    "total_executions": 0,
                    "message": "No executions in time period"
                }
            
            metrics = {
                "total_executions": len(executions),
                "successful_executions": sum(1 for e in executions if e.execution_successful),
                "failed_executions": sum(1 for e in executions if not e.execution_successful),
                "avg_execution_time_ms": sum(
                    e.execution_time_ms for e in executions if e.execution_time_ms
                ) / len(executions),
                "avg_tokens_used": sum(
                    e.tokens_used for e in executions if e.tokens_used
                ) / len(executions),
                "avg_quality_score": sum(
                    e.quality_score for e in executions if e.quality_score
                ) / len([e for e in executions if e.quality_score]) if any(e.quality_score for e in executions) else None,
                "success_rate": sum(1 for e in executions if e.execution_successful) / len(executions)
            }
            
            return metrics
            
        finally:
            if should_close:
                db.close()


class PromptABTester:
    """Manages A/B testing of prompt variants."""
    
    def __init__(self):
        self.logger = logger
    
    def create_test(
        self,
        test_name: str,
        control_prompt_id: str,
        variant_prompt_ids: List[str],
        test_metrics: List[str],
        min_sample_size: int = 100,
        traffic_split: Optional[Dict[str, float]] = None,
        user_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> PromptABTest:
        """Create a new A/B test."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            test_id = f"test_{uuid.uuid4().hex[:12]}"
            
            # Default even traffic split
            if not traffic_split:
                total_variants = len(variant_prompt_ids) + 1
                split_value = 1.0 / total_variants
                traffic_split = {
                    "control": split_value,
                    **{vid: split_value for vid in variant_prompt_ids}
                }
            
            test = PromptABTest(
                test_id=test_id,
                test_name=test_name,
                control_prompt_id=control_prompt_id,
                variant_prompt_ids=variant_prompt_ids,
                test_metrics=test_metrics,
                traffic_split=traffic_split,
                min_sample_size=min_sample_size,
                start_date=datetime.utcnow(),
                status="running",
                created_by=user_id
            )
            
            db.add(test)
            db.commit()
            db.refresh(test)
            
            self.logger.info(f"Created A/B test: {test_name} ({test_id})")
            return test
            
        finally:
            if should_close:
                db.close()
    
    def select_variant(
        self,
        test_id: str,
        db: Optional[Session] = None
    ) -> str:
        """Select which prompt variant to use for this request."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            test = db.query(PromptABTest).filter_by(test_id=test_id).first()
            
            if not test or test.status != "running":
                return test.control_prompt_id if test else None
            
            # Simple round-robin selection for now
            # In production, use proper randomization with traffic split
            import random
            
            all_variants = [test.control_prompt_id] + test.variant_prompt_ids
            return random.choice(all_variants)
            
        finally:
            if should_close:
                db.close()
    
    def analyze_test(
        self,
        test_id: str,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Analyze A/B test results."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            test = db.query(PromptABTest).filter_by(test_id=test_id).first()
            
            if not test:
                return {"error": "Test not found"}
            
            # Get performance data for control and variants
            control_metrics = self._get_variant_metrics(
                test.control_prompt_id,
                test.start_date,
                db
            )
            
            variant_metrics = {}
            for variant_id in test.variant_prompt_ids:
                variant_metrics[variant_id] = self._get_variant_metrics(
                    variant_id,
                    test.start_date,
                    db
                )
            
            # Determine winner (simplified)
            all_scores = {
                "control": control_metrics.get("avg_quality_score", 0),
                **{vid: metrics.get("avg_quality_score", 0) 
                   for vid, metrics in variant_metrics.items()}
            }
            
            winner_id = max(all_scores, key=all_scores.get)
            winner_prompt_id = test.control_prompt_id if winner_id == "control" else winner_id
            
            analysis = {
                "test_id": test_id,
                "status": test.status,
                "control_metrics": control_metrics,
                "variant_metrics": variant_metrics,
                "winner": winner_id,
                "winner_prompt_id": winner_prompt_id,
                "improvement": all_scores.get(winner_id, 0) - all_scores.get("control", 0),
                "ready_to_conclude": (
                    control_metrics.get("sample_size", 0) >= test.min_sample_size
                    and all(
                        m.get("sample_size", 0) >= test.min_sample_size
                        for m in variant_metrics.values()
                    )
                )
            }
            
            return analysis
            
        finally:
            if should_close:
                db.close()
    
    def _get_variant_metrics(
        self,
        prompt_id: str,
        start_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Get metrics for a specific variant."""
        executions = db.query(PromptPerformance).filter(
            PromptPerformance.prompt_id == prompt_id,
            PromptPerformance.execution_timestamp >= start_date
        ).all()
        
        if not executions:
            return {"sample_size": 0}
        
        return {
            "sample_size": len(executions),
            "avg_quality_score": sum(
                e.quality_score for e in executions if e.quality_score
            ) / len([e for e in executions if e.quality_score]) if any(e.quality_score for e in executions) else 0,
            "avg_execution_time": sum(
                e.execution_time_ms for e in executions if e.execution_time_ms
            ) / len(executions),
            "success_rate": sum(1 for e in executions if e.execution_successful) / len(executions)
        }


class PromptOptimizer:
    """Optimizes prompts for better performance."""
    
    def __init__(self):
        self.logger = logger
    
    def start_optimization(
        self,
        prompt_id: str,
        optimization_method: str,
        optimization_goal: str,
        target_metrics: Dict[str, float],
        user_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> PromptOptimizationRun:
        """Start a prompt optimization run."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            run_id = f"opt_{uuid.uuid4().hex[:12]}"
            
            prompt = db.query(PromptLibraryItem).filter_by(
                prompt_id=prompt_id
            ).first()
            
            if not prompt:
                raise ValueError(f"Prompt {prompt_id} not found")
            
            optimization = PromptOptimizationRun(
                prompt_id=prompt_id,
                run_id=run_id,
                optimization_method=optimization_method,
                optimization_goal=optimization_goal,
                original_prompt=prompt.prompt_template,
                target_metrics=target_metrics,
                status="running",
                initiated_by=user_id
            )
            
            db.add(optimization)
            db.commit()
            db.refresh(optimization)
            
            self.logger.info(f"Started optimization run: {run_id}")
            return optimization
            
        finally:
            if should_close:
                db.close()
    
    def suggest_improvements(
        self,
        prompt_id: str,
        db: Optional[Session] = None
    ) -> List[str]:
        """Suggest improvements for a prompt based on performance data."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            prompt = db.query(PromptLibraryItem).filter_by(
                prompt_id=prompt_id
            ).first()
            
            if not prompt:
                return []
            
            suggestions = []
            
            # Analyze performance
            if prompt.success_rate and prompt.success_rate < 0.8:
                suggestions.append("Consider clarifying instructions in the prompt")
            
            if prompt.avg_response_quality and prompt.avg_response_quality < 0.7:
                suggestions.append("Add more specific examples or constraints")
            
            if not prompt.uses_few_shot and prompt.prompt_category in ["generation", "analysis"]:
                suggestions.append("Consider adding few-shot examples")
            
            if prompt.avg_execution_time_ms and prompt.avg_execution_time_ms > 5000:
                suggestions.append("Prompt may be too complex, consider simplification")
            
            return suggestions
            
        finally:
            if should_close:
                db.close()


class PromptOrchestrator:
    """Orchestrates all prompt management functions."""
    
    def __init__(self):
        self.library = PromptLibraryManager()
        self.renderer = PromptRenderer()
        self.performance = PromptPerformanceTracker()
        self.ab_tester = PromptABTester()
        self.optimizer = PromptOptimizer()
        self.logger = logger
    
    def execute_prompt(
        self,
        prompt_id: str,
        variables: Dict[str, Any],
        user_id: Optional[str] = None,
        track_performance: bool = True,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Execute a prompt with full orchestration."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            # Get prompt
            prompt = self.library.get_prompt(prompt_id, db)
            
            if not prompt:
                return {"error": "Prompt not found"}
            
            # Render prompt
            rendered_prompt = self.renderer.render(
                prompt.prompt_template,
                variables
            )
            
            # This is a placeholder - in production, this would call the actual LLM
            response_text = f"[Simulated response to: {rendered_prompt[:100]}...]"
            execution_time_ms = 1500
            tokens_used = 250
            
            # Track performance
            if track_performance:
                self.performance.log_execution(
                    prompt_id=prompt_id,
                    version_id=prompt.current_version_id,
                    rendered_prompt=rendered_prompt,
                    input_variables=variables,
                    response_text=response_text,
                    execution_time_ms=execution_time_ms,
                    tokens_used=tokens_used,
                    quality_score=0.85,
                    user_id=user_id,
                    db=db
                )
            
            return {
                "prompt_id": prompt_id,
                "rendered_prompt": rendered_prompt,
                "response": response_text,
                "execution_time_ms": execution_time_ms,
                "tokens_used": tokens_used
            }
            
        finally:
            if should_close:
                db.close()


# Convenience functions
def execute_prompt(
    prompt_id: str,
    variables: Dict[str, Any],
    user_id: Optional[str] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """Convenience function to execute a prompt."""
    orchestrator = PromptOrchestrator()
    return orchestrator.execute_prompt(prompt_id, variables, user_id, db=db)


def get_prompt_performance(
    prompt_id: str,
    days: int = 30,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """Convenience function to get prompt performance."""
    tracker = PromptPerformanceTracker()
    return tracker.get_performance_metrics(prompt_id, days, db)
