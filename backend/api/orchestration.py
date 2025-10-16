"""
Agent Orchestration API Endpoints

Provides REST API for the PTCC agent orchestration system.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.logging_config import get_logger
from ..core.agent_orchestrator import (
    AgentOrchestrator,
    execute_task,
    register_new_agent
)
from ..models.agent_models import AgentRegistry, AgentTask

logger = get_logger("api.orchestration")
router = APIRouter(prefix="/api/orchestration", tags=["orchestration"]) 


# Pydantic models for request/response
class AgentRegistrationRequest(BaseModel):
    """Request to register a new agent."""
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_name: str = Field(..., description="Human-readable agent name")
    agent_type: str = Field(..., description="Agent type (e.g., educational_planning)")
    capabilities: List[str] = Field(..., description="List of agent capabilities")
    model_provider: str = Field(default="gemini", description="LLM provider")
    model_name: str = Field(default="gemini-1.5-pro", description="LLM model name")
    configuration: Optional[Dict[str, Any]] = Field(default=None, description="Agent configuration")


class AgentTaskRequest(BaseModel):
    """Request to execute an agent task."""
    agent_id: str = Field(..., description="Agent to execute")
    task_type: str = Field(..., description="Type of task")
    input_data: Dict[str, Any] = Field(..., description="Task input data")
    user_id: Optional[str] = Field(default=None, description="User ID for personalization")
    enable_memory: bool = Field(default=True, description="Enable memory integration")
    enable_alignment: bool = Field(default=True, description="Enable alignment checks")
    enable_governance: bool = Field(default=True, description="Enable governance checks")


class AgentResponse(BaseModel):
    """Response from agent registration."""
    agent_id: str
    agent_name: str
    agent_type: str
    capabilities: List[str]
    is_active: bool
    message: str


class TaskResponse(BaseModel):
    """Response from agent task execution."""
    success: bool
    task_id: Optional[str] = None
    result: Optional[str] = None
    confidence: Optional[float] = None
    execution_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentListItem(BaseModel):
    """Agent list item."""
    agent_id: str
    name: str
    type: str
    capabilities: List[str]


class TaskHistoryItem(BaseModel):
    """Task history item."""
    task_id: str
    agent_id: str
    task_type: str
    status: str
    execution_time_ms: Optional[int]
    created_at: str
    cost_estimate: Optional[float]


# Agent Management Endpoints

@router.get("/agents", response_model=List[AgentListItem])
async def list_agents():
    """
    List all available agents.
    
    Returns a list of registered agents with their capabilities.
    """
    try:
        orchestrator = AgentOrchestrator()
        agents = orchestrator.list_available_agents()
        
        return [
            AgentListItem(
                agent_id=agent["agent_id"],
                name=agent["name"],
                type=agent["type"],
                capabilities=agent["capabilities"]
            )
            for agent in agents
        ]
        
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/register", response_model=AgentResponse)
async def register_agent(request: AgentRegistrationRequest):
    """
    Register a new agent in the system.
    
    Allows dynamic registration of new agents with their capabilities.
    """
    try:
        agent = register_new_agent(
            agent_id=request.agent_id,
            agent_name=request.agent_name,
            agent_type=request.agent_type,
            capabilities=request.capabilities,
            model_provider=request.model_provider,
            model_name=request.model_name,
            configuration=request.configuration
        )
        
        return AgentResponse(
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
            agent_type=agent.agent_type,
            capabilities=agent.capabilities,
            is_active=agent.is_active,
            message=f"Agent '{agent.agent_name}' registered successfully"
        )
        
    except Exception as e:
        logger.error(f"Error registering agent: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """
    Get details about a specific agent.
    """
    try:
        agent = db.query(AgentRegistry).filter_by(agent_id=agent_id).first()
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        return {
            "agent_id": agent.agent_id,
            "agent_name": agent.agent_name,
            "agent_type": agent.agent_type,
            "capabilities": agent.capabilities,
            "model_provider": agent.model_provider,
            "model_name": agent.model_name,
            "is_active": agent.is_active,
            "total_executions": agent.total_executions,
            "success_rate": agent.success_rate,
            "avg_execution_time_ms": agent.avg_execution_time_ms
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Task Execution Endpoints

@router.post("/tasks/execute", response_model=TaskResponse)
async def execute_agent_task(request: AgentTaskRequest):
    """
    Execute an agent task with full orchestration.
    
    This endpoint provides the complete PTCC experience:
    - LLM integration
    - Memory and context
    - Alignment checking
    - Governance enforcement
    - Performance tracking
    """
    try:
        result = execute_task(
            agent_id=request.agent_id,
            task_type=request.task_type,
            input_data=request.input_data,
            user_id=request.user_id,
            enable_memory=request.enable_memory,
            enable_alignment=request.enable_alignment,
            enable_governance=request.enable_governance
        )
        
        return TaskResponse(
            success=result.get("success", False),
            task_id=result.get("task_id"),
            result=result.get("result"),
            confidence=result.get("confidence"),
            execution_time_ms=result.get("execution_time_ms"),
            tokens_used=result.get("tokens_used"),
            cost=result.get("cost"),
            error=result.get("error"),
            metadata=result.get("metadata")
        )
        
    except Exception as e:
        logger.error(f"Error executing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/history", response_model=List[TaskHistoryItem])
async def get_task_history(
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    limit: int = Query(20, ge=1, le=100, description="Number of tasks to return"),
    db: Session = Depends(get_db)
):
    """
    Get task execution history.
    
    Returns recent tasks with their status and performance metrics.
    """
    try:
        query = db.query(AgentTask)
        
        if agent_id:
            query = query.filter_by(agent_id=agent_id)
        
        tasks = query.order_by(AgentTask.created_at.desc()).limit(limit).all()
        
        return [
            TaskHistoryItem(
                task_id=task.task_id,
                agent_id=task.agent_id,
                task_type=task.task_type,
                status=task.status,
                execution_time_ms=task.execution_time_ms,
                created_at=task.created_at.isoformat(),
                cost_estimate=task.cost_estimate
            )
            for task in tasks
        ]
        
    except Exception as e:
        logger.error(f"Error getting task history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}")
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    Get details about a specific task.
    """
    try:
        task = db.query(AgentTask).filter_by(task_id=task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
        
        return {
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "task_type": task.task_type,
            "status": task.status,
            "input_data": task.input_data,
            "output_data": task.output_data,
            "execution_time_ms": task.execution_time_ms,
            "tokens_used": task.tokens_used,
            "cost_estimate": task.cost_estimate,
            "confidence_score": task.confidence_score,
            "created_at": task.created_at.isoformat(),
            "start_time": task.start_time.isoformat() if task.start_time else None,
            "end_time": task.end_time.isoformat() if task.end_time else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Quick Action Endpoints (Convenience)

@router.post("/quick/lesson-plan")
async def quick_lesson_plan(
    grade: str = Query(..., description="Grade level"),
    subject: str = Query(..., description="Subject"),
    topic: str = Query(..., description="Topic"),
    duration: str = Query(default="45 minutes", description="Duration"),
    user_id: Optional[str] = Query(None)
):
    """
    Quick endpoint to generate a lesson plan.
    """
    try:
        result = execute_task(
            agent_id="lesson_planner",
            task_type="create_lesson_plan",
            input_data={
                "grade": grade,
                "subject": subject,
                "topic": topic,
                "duration": duration
            },
            user_id=user_id
        )
        
        return {
            "lesson_plan": result.get("result"),
            "metadata": result.get("metadata")
        }
        
    except Exception as e:
        logger.error(f"Error creating lesson plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick/assessment")
async def quick_assessment(
    topic: str = Query(..., description="Topic"),
    grade: str = Query(..., description="Grade level"),
    question_count: int = Query(5, ge=1, le=20, description="Number of questions"),
    user_id: Optional[str] = Query(None)
):
    """
    Quick endpoint to generate assessment questions.
    """
    try:
        result = execute_task(
            agent_id="assessment_generator",
            task_type="generate_questions",
            input_data={
                "topic": topic,
                "grade": grade,
                "question_count": question_count,
                "question_types": ["multiple_choice", "short_answer"]
            },
            user_id=user_id
        )
        
        return {
            "questions": result.get("result"),
            "metadata": result.get("metadata")
        }
        
    except Exception as e:
        logger.error(f"Error generating assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick/feedback")
async def quick_feedback(
    student_name: str = Query(..., description="Student name"),
    assignment: str = Query(..., description="Assignment name"),
    score: int = Query(..., ge=0, le=100, description="Score"),
    strengths: List[str] = Query(..., description="Student strengths"),
    improvements: List[str] = Query(..., description="Areas for improvement"),
    user_id: Optional[str] = Query(None)
):
    """
    Quick endpoint to compose personalized feedback.
    """
    try:
        result = execute_task(
            agent_id="feedback_composer",
            task_type="compose_feedback",
            input_data={
                "student_name": student_name,
                "assignment": assignment,
                "score": score,
                "strengths": strengths,
                "areas_for_improvement": improvements
            },
            user_id=user_id
        )
        
        return {
            "feedback": result.get("result"),
            "metadata": result.get("metadata")
        }
        
    except Exception as e:
        logger.error(f"Error composing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Statistics Endpoints

@router.get("/stats/overview")
async def get_stats_overview(db: Session = Depends(get_db)):
    """
    Get overview statistics for the orchestration system.
    """
    try:
        from sqlalchemy import func
        
        # Count agents
        total_agents = db.query(func.count(AgentRegistry.id)).filter_by(is_active=True).scalar()
        
        # Count tasks
        total_tasks = db.query(func.count(AgentTask.id)).scalar()
        completed_tasks = db.query(func.count(AgentTask.id)).filter_by(status="completed").scalar()
        
        # Calculate total cost
        total_cost = db.query(func.sum(AgentTask.cost_estimate)).filter_by(status="completed").scalar() or 0
        
        # Average execution time
        avg_time = db.query(func.avg(AgentTask.execution_time_ms)).filter_by(status="completed").scalar() or 0
        
        return {
            "total_agents": total_agents,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "total_cost": round(total_cost, 4),
            "avg_execution_time_ms": round(avg_time, 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
