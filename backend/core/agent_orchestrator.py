"""
Agent Orchestration Layer for PTCC

Coordinates AI agents with LLM integration, memory system, alignment checks,
and governance policies. Provides unified interface for all agent operations.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
import uuid

from .database import SessionLocal
from .logging_config import get_logger
from .llm_integration import get_llm_orchestrator, LLMResponse
from .memory_system import (
    get_user_context,
    log_user_interaction,
    UserProfileManager,
    ContextLayerManager
)
from .alignment_system import check_content_alignment
from .governance_system import check_governance
from .prompt_system import PromptLibraryManager, PromptRenderer
from ..models.agent_models import (
    AgentRegistry,
    AgentTask,
    AgentCommunicationLog,
    AgentPerformanceMetric
)

logger = get_logger("agent_orchestrator")


class AgentStatus(Enum):
    """Agent execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentOrchestrator:
    """
    Main orchestrator for all AI agents.
    
    Features:
    - Agent registration and discovery
    - Task routing and execution
    - LLM integration
    - Memory and context management
    - Alignment and governance checking
    - Performance tracking
    """
    
    def __init__(self):
        self.logger = logger
        self.llm_orchestrator = get_llm_orchestrator()
        self.profile_manager = UserProfileManager()
        self.context_manager = ContextLayerManager()
        self.prompt_manager = PromptLibraryManager()
        self.prompt_renderer = PromptRenderer()
        
        # Agent registry cache
        self.agent_cache = {}
        self._load_agents()
    
    def _load_agents(self):
        """Load registered agents from database."""
        try:
            db = SessionLocal()
            agents = db.query(AgentRegistry).filter_by(is_active=True).all()
            
            for agent in agents:
                self.agent_cache[agent.agent_id] = {
                    "name": agent.agent_name,
                    "type": agent.agent_type,
                    "capabilities": agent.capabilities,
                    "model_provider": agent.model_provider,
                    "model_name": agent.model_name
                }
            
            self.logger.info(f"Loaded {len(self.agent_cache)} agents")
            db.close()
            
        except Exception as e:
            self.logger.error(f"Error loading agents: {e}")
    
    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        capabilities: List[str],
        model_provider: str = "gemini",
        model_name: str = "gemini-1.5-pro",
        configuration: Optional[Dict[str, Any]] = None,
        db: Optional[Any] = None
    ) -> AgentRegistry:
        """Register a new agent in the system."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            agent = AgentRegistry(
                agent_id=agent_id,
                agent_name=agent_name,
                agent_type=agent_type,
                capabilities=capabilities,
                model_provider=model_provider,
                model_name=model_name,
                configuration=configuration or {},
                is_active=True,
                is_enabled=True
            )
            
            db.add(agent)
            db.commit()
            db.refresh(agent)
            
            # Update cache
            self.agent_cache[agent_id] = {
                "name": agent_name,
                "type": agent_type,
                "capabilities": capabilities,
                "model_provider": model_provider,
                "model_name": model_name
            }
            
            self.logger.info(f"Registered agent: {agent_name} ({agent_id})")
            return agent
            
        finally:
            if should_close:
                db.close()
    
    def execute_agent_task(
        self,
        agent_id: str,
        task_type: str,
        input_data: Dict[str, Any],
        user_id: Optional[str] = None,
        enable_memory: bool = True,
        enable_alignment: bool = True,
        enable_governance: bool = True,
        db: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Execute an agent task with full orchestration.
        
        This is the main method for running agents with all PTCC features.
        """
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        start_time = datetime.utcnow()
        
        try:
            # 1. Load agent configuration
            agent_config = self.agent_cache.get(agent_id)
            if not agent_config:
                raise ValueError(f"Agent {agent_id} not found")
            
            # 2. Retrieve user context if memory enabled
            context = {}
            if enable_memory and user_id:
                context = get_user_context(user_id, db)
                self.logger.info(f"Retrieved memory context for user {user_id}")
            
            # 3. Check governance before execution
            if enable_governance:
                gov_check = check_governance(
                    entity_type="agent_task",
                    entity_id=task_id,
                    action="execute",
                    actor_id=user_id or "system",
                    context={
                        "agent_id": agent_id,
                        "task_type": task_type,
                        "risk_category": "agent_execution"
                    },
                    db=db
                )
                
                if not gov_check["allowed"]:
                    self.logger.warning(f"Governance check failed for task {task_id}")
                    return {
                        "success": False,
                        "error": "Task blocked by governance policy",
                        "governance_result": gov_check
                    }
            
            # 4. Create task record
            task = AgentTask(
                task_id=task_id,
                agent_id=agent_id,
                task_type=task_type,
                input_data=input_data,
                status=AgentStatus.RUNNING.value,
                start_time=start_time,
                created_by=user_id or "system"
            )
            db.add(task)
            db.commit()
            
            # 5. Build prompt with context
            prompt = self._build_agent_prompt(
                agent_id=agent_id,
                task_type=task_type,
                input_data=input_data,
                context=context
            )
            
            # 6. Execute with LLM
            llm_response = self.llm_orchestrator.generate(
                prompt=prompt,
                provider=agent_config["model_provider"],
                model=agent_config["model_name"],
                temperature=0.7,
                max_tokens=2048
            )
            
            # 7. Check alignment if enabled
            alignment_result = None
            if enable_alignment:
                alignment_result = check_content_alignment(
                    content=llm_response.text,
                    context={
                        "agent_id": agent_id,
                        "task_type": task_type,
                        "user_id": user_id
                    },
                    db=db
                )
                
                if not alignment_result["overall_aligned"]:
                    self.logger.warning(f"Alignment concerns for task {task_id}")
            
            # 8. Update memory if enabled
            if enable_memory and user_id:
                log_user_interaction(
                    user_id=user_id,
                    interaction_type=f"agent_{task_type}",
                    query=str(input_data),
                    response=llm_response.text[:500],  # Truncate for storage
                    agent=agent_id,
                    context={"task_id": task_id},
                    db=db
                )
            
            # 9. Update task record
            end_time = datetime.utcnow()
            execution_time = int((end_time - start_time).total_seconds() * 1000)
            
            task.status = AgentStatus.COMPLETED.value
            task.end_time = end_time
            task.execution_time_ms = execution_time
            task.output_data = {
                "result": llm_response.text,
                "confidence": 0.9,
                "metadata": llm_response.metadata
            }
            task.tokens_used = llm_response.usage["total_tokens"]
            task.cost_estimate = self.llm_orchestrator.estimate_cost(llm_response)
            task.confidence_score = 0.9
            
            db.commit()
            
            # 10. Track performance
            self._track_performance(agent_id, task, db)
            
            return {
                "success": True,
                "task_id": task_id,
                "result": llm_response.text,
                "confidence": 0.9,
                "execution_time_ms": execution_time,
                "tokens_used": llm_response.usage["total_tokens"],
                "cost": task.cost_estimate,
                "alignment_result": alignment_result,
                "metadata": {
                    "agent_id": agent_id,
                    "agent_name": agent_config["name"],
                    "model_used": f"{llm_response.provider}/{llm_response.model}",
                    "context_used": bool(context),
                    "timestamp": end_time.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error executing task {task_id}: {e}")
            
            # Update task as failed
            if 'task' in locals():
                task.status = AgentStatus.FAILED.value
                task.error_message = str(e)
                task.end_time = datetime.utcnow()
                db.commit()
            
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e),
                "metadata": {"agent_id": agent_id}
            }
            
        finally:
            if should_close:
                db.close()
    
    def _build_agent_prompt(
        self,
        agent_id: str,
        task_type: str,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Build the prompt for agent execution."""
        agent_config = self.agent_cache[agent_id]
        
        # Base prompt structure
        prompt = f"""You are {agent_config['name']}, an AI agent specialized in {agent_config['type']}.

Your capabilities include: {', '.join(agent_config['capabilities'])}

Task Type: {task_type}

"""
        
        # Add context if available
        if context and context.get("user_profile"):
            profile = context["user_profile"]
            prompt += f"""User Context:
- Role: {profile.get('role', 'teacher')}
- Subject Expertise: {', '.join(profile.get('subject_expertise', []))}
- Grade Levels: {', '.join(profile.get('grade_levels', []))}
- Teaching Philosophy: {profile.get('teaching_philosophy', 'Not specified')}

"""
        
        # Add input data
        prompt += f"""Input Data:
{self._format_input_data(input_data)}

Please provide a comprehensive, actionable response that aligns with educational best practices and the user's context.
"""
        
        return prompt
    
    def _format_input_data(self, input_data: Dict[str, Any]) -> str:
        """Format input data for prompt."""
        formatted = []
        for key, value in input_data.items():
            if isinstance(value, (dict, list)):
                import json
                value_str = json.dumps(value, indent=2)
            else:
                value_str = str(value)
            formatted.append(f"- {key}: {value_str}")
        return "\n".join(formatted)
    
    def _track_performance(
        self,
        agent_id: str,
        task: AgentTask,
        db: Any
    ):
        """Track agent performance metrics."""
        try:
            # Update agent registry stats
            agent = db.query(AgentRegistry).filter_by(agent_id=agent_id).first()
            if agent:
                agent.total_executions = (agent.total_executions or 0) + 1
                
                # Update average execution time
                if agent.avg_execution_time_ms:
                    agent.avg_execution_time_ms = int(
                        (agent.avg_execution_time_ms * (agent.total_executions - 1) + 
                         task.execution_time_ms) / agent.total_executions
                    )
                else:
                    agent.avg_execution_time_ms = task.execution_time_ms
                
                # Update success rate
                if task.status == AgentStatus.COMPLETED.value:
                    successful = agent.total_executions * (agent.success_rate or 0)
                    agent.success_rate = (successful + 1) / agent.total_executions
                
                db.commit()
                
        except Exception as e:
            self.logger.error(f"Error tracking performance: {e}")
    
    def find_agent_for_task(
        self,
        task_type: str,
        required_capabilities: Optional[List[str]] = None
    ) -> Optional[str]:
        """Find the best agent for a given task."""
        candidates = []
        
        for agent_id, agent_info in self.agent_cache.items():
            # Check if agent has required capabilities
            if required_capabilities:
                if all(cap in agent_info["capabilities"] for cap in required_capabilities):
                    candidates.append(agent_id)
            else:
                # Check if task_type matches agent capabilities
                if task_type in agent_info["capabilities"]:
                    candidates.append(agent_id)
        
        if candidates:
            # Return first match (could be enhanced with scoring)
            return candidates[0]
        
        return None
    
    def get_agent_capabilities(self, agent_id: str) -> List[str]:
        """Get capabilities for a specific agent."""
        agent_info = self.agent_cache.get(agent_id)
        return agent_info["capabilities"] if agent_info else []
    
    def list_available_agents(self) -> List[Dict[str, Any]]:
        """List all available agents."""
        return [
            {
                "agent_id": agent_id,
                "name": info["name"],
                "type": info["type"],
                "capabilities": info["capabilities"]
            }
            for agent_id, info in self.agent_cache.items()
        ]


# Convenience functions
def execute_task(
    agent_id: str,
    task_type: str,
    input_data: Dict[str, Any],
    user_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to execute an agent task."""
    orchestrator = AgentOrchestrator()
    return orchestrator.execute_agent_task(
        agent_id=agent_id,
        task_type=task_type,
        input_data=input_data,
        user_id=user_id,
        **kwargs
    )


def register_new_agent(
    agent_id: str,
    agent_name: str,
    agent_type: str,
    capabilities: List[str],
    **kwargs
) -> AgentRegistry:
    """Convenience function to register a new agent."""
    orchestrator = AgentOrchestrator()
    return orchestrator.register_agent(
        agent_id=agent_id,
        agent_name=agent_name,
        agent_type=agent_type,
        capabilities=capabilities,
        **kwargs
    )
