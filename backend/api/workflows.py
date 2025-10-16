"""
Workflow API Endpoints

Provides REST API for workflow management and execution:
- Create and manage workflows
- Execute workflows
- Query workflow status
- Get workflow templates
- Monitor performance
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.core.workflow_engine import (
    WorkflowEngine,
    Workflow,
    WorkflowExecution,
    WorkflowStatus,
    WorkflowBuilder,
    create_lesson_planning_workflow,
    create_assessment_workflow,
    create_feedback_workflow
)
from backend.core.agent_orchestrator import AgentOrchestrator
from backend.core.database import get_db
from sqlalchemy.orm import Session


# Initialize workflow engine (will be properly initialized in main.py)
workflow_engine: Optional[WorkflowEngine] = None


def init_workflow_engine(orchestrator: AgentOrchestrator):
    """Initialize the workflow engine with orchestrator."""
    global workflow_engine
    workflow_engine = WorkflowEngine(orchestrator=orchestrator)
    
    # Register default workflow templates
    workflow_engine.register_workflow(create_lesson_planning_workflow())
    workflow_engine.register_workflow(create_assessment_workflow())
    workflow_engine.register_workflow(create_feedback_workflow())


def get_workflow_engine() -> WorkflowEngine:
    """Dependency to get workflow engine."""
    if workflow_engine is None:
        raise HTTPException(status_code=500, detail="Workflow engine not initialized")
    return workflow_engine


router = APIRouter(prefix="/api/workflows", tags=["workflows"])


# Pydantic Models

class WorkflowNodeRequest(BaseModel):
    """Request model for workflow node."""
    node_type: str
    name: str
    description: Optional[str] = ""
    agent_id: Optional[str] = None
    task_type: Optional[str] = None
    input_mapping: Optional[Dict[str, str]] = {}
    output_mapping: Optional[Dict[str, str]] = {}
    next_nodes: Optional[List[str]] = []


class WorkflowCreateRequest(BaseModel):
    """Request model for creating a workflow."""
    name: str
    description: Optional[str] = ""
    version: Optional[str] = "1.0.0"
    nodes: List[WorkflowNodeRequest]
    start_node_id: str


class WorkflowExecuteRequest(BaseModel):
    """Request model for executing a workflow."""
    workflow_id: str
    input_data: Dict[str, Any]
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}


class WorkflowResponse(BaseModel):
    """Response model for workflow."""
    workflow_id: str
    name: str
    description: str
    version: str
    node_count: int
    created_at: str
    updated_at: str


class WorkflowExecutionResponse(BaseModel):
    """Response model for workflow execution."""
    execution_id: str
    workflow_id: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    total_execution_time_ms: int
    completed_nodes_count: int
    failed_nodes_count: int
    error_messages: List[str]


class QuickLessonPlanRequest(BaseModel):
    """Quick request for lesson planning workflow."""
    grade: str = Field(..., description="Grade level (e.g., '5th')")
    subject: str = Field(..., description="Subject area")
    topic: str = Field(..., description="Lesson topic")
    duration: Optional[str] = "45 minutes"
    user_id: Optional[str] = None


class QuickAssessmentRequest(BaseModel):
    """Quick request for assessment workflow."""
    topic: str = Field(..., description="Assessment topic")
    grade: str = Field(..., description="Grade level")
    question_count: int = Field(5, description="Number of questions")
    question_types: Optional[List[str]] = ["multiple_choice", "short_answer"]
    user_id: Optional[str] = None


# Endpoints

@router.get("/", response_model=List[WorkflowResponse])
def list_workflows(engine: WorkflowEngine = Depends(get_workflow_engine)):
    """List all available workflows."""
    workflows = engine.list_workflows()
    
    return [
        WorkflowResponse(
            workflow_id=wf.workflow_id,
            name=wf.name,
            description=wf.description,
            version=wf.version,
            node_count=len(wf.nodes),
            created_at=wf.created_at.isoformat(),
            updated_at=wf.updated_at.isoformat()
        )
        for wf in workflows
    ]


@router.get("/{workflow_id}", response_model=Dict[str, Any])
def get_workflow(
    workflow_id: str,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Get detailed workflow definition."""
    workflow = engine.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow.to_dict()


@router.post("/execute", response_model=WorkflowExecutionResponse)
def execute_workflow(
    request: WorkflowExecuteRequest,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Execute a workflow."""
    try:
        execution = engine.execute_workflow(
            workflow_id=request.workflow_id,
            input_data=request.input_data,
            user_id=request.user_id,
            context=request.context
        )
        
        return WorkflowExecutionResponse(
            execution_id=execution.execution_id,
            workflow_id=execution.workflow_id,
            status=execution.status.value,
            started_at=execution.started_at.isoformat(),
            completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
            total_execution_time_ms=execution.total_execution_time_ms,
            completed_nodes_count=len(execution.completed_nodes),
            failed_nodes_count=len(execution.failed_nodes),
            error_messages=execution.error_messages
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/executions/{execution_id}", response_model=Dict[str, Any])
def get_execution_status(
    execution_id: str,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Get status of a workflow execution."""
    execution = engine.get_execution_status(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return {
        "execution_id": execution.execution_id,
        "workflow_id": execution.workflow_id,
        "status": execution.status.value,
        "started_at": execution.started_at.isoformat(),
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "total_execution_time_ms": execution.total_execution_time_ms,
        "current_nodes": execution.current_nodes,
        "completed_nodes": execution.completed_nodes,
        "failed_nodes": execution.failed_nodes,
        "input_data": execution.input_data,
        "output_data": execution.output_data,
        "context": execution.context,
        "node_execution_times": execution.node_execution_times,
        "error_messages": execution.error_messages,
        "user_id": execution.user_id
    }


# Template Workflows

@router.get("/templates/", response_model=List[Dict[str, Any]])
def list_workflow_templates():
    """List available workflow templates."""
    templates = [
        {
            "template_id": "lesson_planning",
            "name": "Lesson Planning Workflow",
            "description": "Complete lesson planning from research to final plan",
            "nodes": ["Research Standards", "Create Outline", "Develop Content", "Add Differentiation"],
            "estimated_time": "3-5 minutes",
            "use_case": "Create comprehensive, differentiated lesson plans"
        },
        {
            "template_id": "assessment_creation",
            "name": "Assessment Creation Workflow",
            "description": "Create comprehensive assessments with rubrics",
            "nodes": ["Identify Standards", "Generate Questions", "Create Rubric"],
            "estimated_time": "2-3 minutes",
            "use_case": "Generate standards-aligned assessments with grading rubrics"
        },
        {
            "template_id": "student_feedback",
            "name": "Student Feedback Workflow",
            "description": "Comprehensive student feedback generation",
            "nodes": ["Analyze Performance", "Compose Feedback"],
            "estimated_time": "1-2 minutes",
            "use_case": "Create personalized, actionable student feedback"
        }
    ]
    
    return templates


@router.get("/templates/{template_id}", response_model=Dict[str, Any])
def get_workflow_template(
    template_id: str,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Get a specific workflow template."""
    # Map template IDs to workflow creation functions
    template_map = {
        "lesson_planning": create_lesson_planning_workflow,
        "assessment_creation": create_assessment_workflow,
        "student_feedback": create_feedback_workflow
    }
    
    if template_id not in template_map:
        raise HTTPException(status_code=404, detail="Template not found")
    
    workflow = template_map[template_id]()
    return workflow.to_dict()


# Quick Actions

@router.post("/quick/lesson-plan", response_model=Dict[str, Any])
def quick_lesson_plan(
    request: QuickLessonPlanRequest,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Quick endpoint to create a lesson plan using the workflow."""
    # Find or create the lesson planning workflow
    workflows = engine.list_workflows()
    lesson_workflow = next(
        (wf for wf in workflows if "Lesson Planning" in wf.name),
        None
    )
    
    if not lesson_workflow:
        lesson_workflow = create_lesson_planning_workflow()
        engine.register_workflow(lesson_workflow)
    
    # Execute workflow
    execution = engine.execute_workflow(
        workflow_id=lesson_workflow.workflow_id,
        input_data={
            "grade": request.grade,
            "subject": request.subject,
            "topic": request.topic,
            "duration": request.duration
        },
        user_id=request.user_id
    )
    
    return {
        "execution_id": execution.execution_id,
        "status": execution.status.value,
        "lesson_plan": execution.context.get("final_plan", ""),
        "standards": execution.context.get("standards", ""),
        "outline": execution.context.get("outline", ""),
        "execution_time_ms": execution.total_execution_time_ms
    }


@router.post("/quick/assessment", response_model=Dict[str, Any])
def quick_assessment(
    request: QuickAssessmentRequest,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Quick endpoint to create an assessment using the workflow."""
    workflows = engine.list_workflows()
    assessment_workflow = next(
        (wf for wf in workflows if "Assessment Creation" in wf.name),
        None
    )
    
    if not assessment_workflow:
        assessment_workflow = create_assessment_workflow()
        engine.register_workflow(assessment_workflow)
    
    execution = engine.execute_workflow(
        workflow_id=assessment_workflow.workflow_id,
        input_data={
            "topic": request.topic,
            "grade": request.grade,
            "question_count": request.question_count,
            "question_types": request.question_types
        },
        user_id=request.user_id
    )
    
    return {
        "execution_id": execution.execution_id,
        "status": execution.status.value,
        "questions": execution.context.get("questions", ""),
        "rubric": execution.context.get("rubric", ""),
        "standards": execution.context.get("standards", ""),
        "execution_time_ms": execution.total_execution_time_ms
    }


# Performance & Statistics

@router.get("/stats/overview", response_model=Dict[str, Any])
def get_workflow_statistics(engine: WorkflowEngine = Depends(get_workflow_engine)):
    """Get workflow performance statistics."""
    executions = list(engine.executions.values())
    
    if not executions:
        return {
            "total_executions": 0,
            "completed": 0,
            "failed": 0,
            "running": 0,
            "success_rate": 0.0,
            "avg_execution_time_ms": 0,
            "total_nodes_executed": 0
        }
    
    completed = [e for e in executions if e.status == WorkflowStatus.COMPLETED]
    failed = [e for e in executions if e.status == WorkflowStatus.FAILED]
    running = [e for e in executions if e.status == WorkflowStatus.RUNNING]
    
    avg_time = (
        sum(e.total_execution_time_ms for e in completed) / len(completed)
        if completed else 0
    )
    
    total_nodes = sum(len(e.completed_nodes) for e in executions)
    
    return {
        "total_executions": len(executions),
        "completed": len(completed),
        "failed": len(failed),
        "running": len(running),
        "success_rate": (len(completed) / len(executions) * 100) if executions else 0.0,
        "avg_execution_time_ms": int(avg_time),
        "total_nodes_executed": total_nodes,
        "workflows_registered": len(engine.workflows)
    }


@router.get("/stats/{workflow_id}", response_model=Dict[str, Any])
def get_workflow_performance(
    workflow_id: str,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """Get performance statistics for a specific workflow."""
    workflow = engine.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Get executions for this workflow
    workflow_executions = [
        e for e in engine.executions.values()
        if e.workflow_id == workflow_id
    ]
    
    if not workflow_executions:
        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow.name,
            "total_executions": 0,
            "success_rate": 0.0,
            "avg_execution_time_ms": 0,
            "node_performance": {}
        }
    
    completed = [e for e in workflow_executions if e.status == WorkflowStatus.COMPLETED]
    
    avg_time = (
        sum(e.total_execution_time_ms for e in completed) / len(completed)
        if completed else 0
    )
    
    # Calculate per-node performance
    node_times = {}
    for execution in completed:
        for node_id, exec_time in execution.node_execution_times.items():
            if node_id not in node_times:
                node_times[node_id] = []
            node_times[node_id].append(exec_time)
    
    node_performance = {
        node_id: {
            "avg_time_ms": int(sum(times) / len(times)),
            "min_time_ms": min(times),
            "max_time_ms": max(times),
            "execution_count": len(times)
        }
        for node_id, times in node_times.items()
    }
    
    return {
        "workflow_id": workflow_id,
        "workflow_name": workflow.name,
        "total_executions": len(workflow_executions),
        "completed": len(completed),
        "failed": len([e for e in workflow_executions if e.status == WorkflowStatus.FAILED]),
        "success_rate": (len(completed) / len(workflow_executions) * 100) if workflow_executions else 0.0,
        "avg_execution_time_ms": int(avg_time),
        "node_performance": node_performance
    }
