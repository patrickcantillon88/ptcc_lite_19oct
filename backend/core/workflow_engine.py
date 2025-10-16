"""
Workflow Engine for PTCC

Enables creation and execution of multi-agent workflows with:
- DAG-based workflow definition
- Conditional branching
- Parallel execution
- Error handling and rollback
- Workflow templates
- Performance tracking
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import uuid
from collections import defaultdict
import asyncio


class WorkflowNodeType(Enum):
    """Types of workflow nodes."""
    AGENT_TASK = "agent_task"
    CONDITION = "condition"
    PARALLEL = "parallel"
    TRANSFORM = "transform"
    HUMAN_REVIEW = "human_review"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class WorkflowNode:
    """Single node in a workflow."""
    node_id: str
    node_type: WorkflowNodeType
    name: str
    description: str = ""
    
    # Agent task configuration
    agent_id: Optional[str] = None
    task_type: Optional[str] = None
    
    # Condition configuration
    condition_fn: Optional[Callable] = None
    
    # Transform configuration
    transform_fn: Optional[Callable] = None
    
    # Connections
    next_nodes: List[str] = field(default_factory=list)
    on_error: Optional[str] = None
    
    # Input/output mapping
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    
    # Execution config
    retry_count: int = 3
    timeout_seconds: int = 300
    
    def __post_init__(self):
        if not self.node_id:
            self.node_id = str(uuid.uuid4())


@dataclass
class WorkflowExecution:
    """Tracks execution of a workflow instance."""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    # Execution state
    current_nodes: List[str] = field(default_factory=list)
    completed_nodes: List[str] = field(default_factory=list)
    failed_nodes: List[str] = field(default_factory=list)
    
    # Data
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Metrics
    total_execution_time_ms: int = 0
    node_execution_times: Dict[str, int] = field(default_factory=dict)
    error_messages: List[str] = field(default_factory=list)
    
    user_id: Optional[str] = None


class Workflow:
    """Represents a complete workflow definition."""
    
    def __init__(
        self,
        workflow_id: str,
        name: str,
        description: str = "",
        version: str = "1.0.0"
    ):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.version = version
        
        self.nodes: Dict[str, WorkflowNode] = {}
        self.start_node: Optional[str] = None
        self.end_nodes: List[str] = []
        
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_node(self, node: WorkflowNode) -> None:
        """Add a node to the workflow."""
        self.nodes[node.node_id] = node
        self.updated_at = datetime.now()
    
    def connect_nodes(self, from_node_id: str, to_node_id: str) -> None:
        """Connect two nodes."""
        if from_node_id not in self.nodes:
            raise ValueError(f"Node {from_node_id} not found")
        if to_node_id not in self.nodes:
            raise ValueError(f"Node {to_node_id} not found")
        
        self.nodes[from_node_id].next_nodes.append(to_node_id)
        self.updated_at = datetime.now()
    
    def set_start_node(self, node_id: str) -> None:
        """Set the starting node."""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")
        self.start_node = node_id
    
    def validate(self) -> tuple[bool, List[str]]:
        """Validate workflow structure."""
        errors = []
        
        if not self.start_node:
            errors.append("No start node defined")
        
        if not self.nodes:
            errors.append("No nodes defined")
        
        # Check for unreachable nodes
        reachable = set()
        if self.start_node:
            queue = [self.start_node]
            while queue:
                node_id = queue.pop(0)
                if node_id in reachable:
                    continue
                reachable.add(node_id)
                node = self.nodes.get(node_id)
                if node:
                    queue.extend(node.next_nodes)
        
        unreachable = set(self.nodes.keys()) - reachable
        if unreachable:
            errors.append(f"Unreachable nodes: {unreachable}")
        
        # Check node configurations
        for node_id, node in self.nodes.items():
            if node.node_type == WorkflowNodeType.AGENT_TASK:
                if not node.agent_id:
                    errors.append(f"Node {node_id}: Missing agent_id")
                if not node.task_type:
                    errors.append(f"Node {node_id}: Missing task_type")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "start_node": self.start_node,
            "end_nodes": self.end_nodes,
            "nodes": {
                node_id: {
                    "node_id": node.node_id,
                    "node_type": node.node_type.value,
                    "name": node.name,
                    "description": node.description,
                    "agent_id": node.agent_id,
                    "task_type": node.task_type,
                    "next_nodes": node.next_nodes,
                    "on_error": node.on_error,
                    "input_mapping": node.input_mapping,
                    "output_mapping": node.output_mapping,
                }
                for node_id, node in self.nodes.items()
            },
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class WorkflowBuilder:
    """Fluent API for building workflows."""
    
    def __init__(self, name: str, description: str = ""):
        workflow_id = str(uuid.uuid4())
        self.workflow = Workflow(workflow_id, name, description)
        self._last_node_id: Optional[str] = None
    
    def agent_task(
        self,
        name: str,
        agent_id: str,
        task_type: str,
        description: str = "",
        input_mapping: Optional[Dict[str, str]] = None,
        output_mapping: Optional[Dict[str, str]] = None
    ) -> 'WorkflowBuilder':
        """Add an agent task node."""
        node = WorkflowNode(
            node_id=str(uuid.uuid4()),
            node_type=WorkflowNodeType.AGENT_TASK,
            name=name,
            description=description,
            agent_id=agent_id,
            task_type=task_type,
            input_mapping=input_mapping or {},
            output_mapping=output_mapping or {}
        )
        
        self.workflow.add_node(node)
        
        # Auto-connect from last node
        if self._last_node_id:
            self.workflow.connect_nodes(self._last_node_id, node.node_id)
        else:
            # First node becomes start node
            self.workflow.set_start_node(node.node_id)
        
        self._last_node_id = node.node_id
        return self
    
    def transform(
        self,
        name: str,
        transform_fn: Callable,
        description: str = ""
    ) -> 'WorkflowBuilder':
        """Add a data transformation node."""
        node = WorkflowNode(
            node_id=str(uuid.uuid4()),
            node_type=WorkflowNodeType.TRANSFORM,
            name=name,
            description=description,
            transform_fn=transform_fn
        )
        
        self.workflow.add_node(node)
        
        if self._last_node_id:
            self.workflow.connect_nodes(self._last_node_id, node.node_id)
        
        self._last_node_id = node.node_id
        return self
    
    def condition(
        self,
        name: str,
        condition_fn: Callable,
        description: str = ""
    ) -> 'WorkflowBuilder':
        """Add a conditional branching node."""
        node = WorkflowNode(
            node_id=str(uuid.uuid4()),
            node_type=WorkflowNodeType.CONDITION,
            name=name,
            description=description,
            condition_fn=condition_fn
        )
        
        self.workflow.add_node(node)
        
        if self._last_node_id:
            self.workflow.connect_nodes(self._last_node_id, node.node_id)
        
        self._last_node_id = node.node_id
        return self
    
    def build(self) -> Workflow:
        """Build and validate the workflow."""
        is_valid, errors = self.workflow.validate()
        if not is_valid:
            raise ValueError(f"Invalid workflow: {errors}")
        return self.workflow


class WorkflowEngine:
    """Main workflow execution engine."""
    
    def __init__(self, orchestrator=None):
        """
        Initialize workflow engine.
        
        Args:
            orchestrator: AgentOrchestrator instance for agent execution
        """
        self.orchestrator = orchestrator
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
    
    def register_workflow(self, workflow: Workflow) -> None:
        """Register a workflow for execution."""
        is_valid, errors = workflow.validate()
        if not is_valid:
            raise ValueError(f"Cannot register invalid workflow: {errors}")
        
        self.workflows[workflow.workflow_id] = workflow
    
    def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecution:
        """Execute a workflow."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        
        # Create execution record
        execution = WorkflowExecution(
            execution_id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now(),
            input_data=input_data,
            context=context or {},
            user_id=user_id
        )
        
        self.executions[execution.execution_id] = execution
        
        try:
            # Start from the start node
            if not workflow.start_node:
                raise ValueError("Workflow has no start node")
            
            # Execute workflow
            self._execute_node(
                workflow=workflow,
                execution=execution,
                node_id=workflow.start_node,
                data=input_data
            )
            
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now()
            execution.total_execution_time_ms = int(
                (execution.completed_at - execution.started_at).total_seconds() * 1000
            )
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_messages.append(str(e))
            execution.completed_at = datetime.now()
            raise
        
        return execution
    
    def _execute_node(
        self,
        workflow: Workflow,
        execution: WorkflowExecution,
        node_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single workflow node."""
        node = workflow.nodes[node_id]
        execution.current_nodes.append(node_id)
        
        start_time = datetime.now()
        result = {}
        
        try:
            # Map input data
            mapped_input = self._map_data(data, node.input_mapping)
            
            # Execute based on node type
            if node.node_type == WorkflowNodeType.AGENT_TASK:
                result = self._execute_agent_task(node, mapped_input, execution)
            
            elif node.node_type == WorkflowNodeType.TRANSFORM:
                if node.transform_fn:
                    result = node.transform_fn(mapped_input)
                else:
                    result = mapped_input
            
            elif node.node_type == WorkflowNodeType.CONDITION:
                if node.condition_fn:
                    result = {"condition_result": node.condition_fn(mapped_input)}
                else:
                    result = {"condition_result": True}
            
            # Map output data
            mapped_output = self._map_data(result, node.output_mapping)
            
            # Update execution context
            execution.context.update(mapped_output)
            execution.completed_nodes.append(node_id)
            
            # Track execution time
            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            execution.node_execution_times[node_id] = execution_time_ms
            
            # Execute next nodes
            for next_node_id in node.next_nodes:
                self._execute_node(workflow, execution, next_node_id, execution.context)
            
            return result
            
        except Exception as e:
            execution.failed_nodes.append(node_id)
            execution.error_messages.append(f"Node {node_id} ({node.name}): {str(e)}")
            
            # Try error handling node
            if node.on_error:
                return self._execute_node(workflow, execution, node.on_error, data)
            raise
    
    def _execute_agent_task(
        self,
        node: WorkflowNode,
        input_data: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute an agent task node."""
        if not self.orchestrator:
            raise ValueError("No orchestrator configured for agent tasks")
        
        result = self.orchestrator.execute_agent_task(
            agent_id=node.agent_id,
            task_type=node.task_type,
            input_data=input_data,
            user_id=execution.user_id
        )
        
        return result
    
    def _map_data(
        self,
        data: Dict[str, Any],
        mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Map data fields according to mapping configuration."""
        if not mapping:
            return data
        
        result = {}
        for target_key, source_key in mapping.items():
            # Support dot notation for nested fields
            value = self._get_nested_value(data, source_key)
            if value is not None:
                result[target_key] = value
        
        return result
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = key.split('.')
        value = data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get status of a workflow execution."""
        return self.executions.get(execution_id)
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow definition."""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Workflow]:
        """List all registered workflows."""
        return list(self.workflows.values())


# Workflow Templates

def create_lesson_planning_workflow() -> Workflow:
    """Create a lesson planning workflow template."""
    builder = WorkflowBuilder(
        name="Lesson Planning Workflow",
        description="Complete lesson planning from research to final plan"
    )
    
    builder.agent_task(
        name="Research Standards",
        agent_id="curriculum_advisor",
        task_type="research_standards",
        description="Research curriculum standards for topic",
        output_mapping={"standards": "result.standards"}
    ).agent_task(
        name="Create Outline",
        agent_id="lesson_plan_generator",
        task_type="create_outline",
        description="Create lesson outline based on standards",
        output_mapping={"outline": "result.outline"}
    ).agent_task(
        name="Develop Content",
        agent_id="lesson_plan_generator",
        task_type="create_lesson_plan",
        description="Develop full lesson content",
        output_mapping={"lesson_plan": "result.lesson_plan"}
    ).agent_task(
        name="Add Differentiation",
        agent_id="differentiation_specialist",
        task_type="add_differentiation",
        description="Add differentiation strategies",
        output_mapping={"final_plan": "result.differentiated_plan"}
    )
    
    return builder.build()


def create_assessment_workflow() -> Workflow:
    """Create an assessment creation workflow template."""
    builder = WorkflowBuilder(
        name="Assessment Creation Workflow",
        description="Create comprehensive assessments with rubrics"
    )
    
    builder.agent_task(
        name="Identify Standards",
        agent_id="curriculum_advisor",
        task_type="identify_standards",
        description="Identify relevant standards",
        output_mapping={"standards": "result.standards"}
    ).agent_task(
        name="Generate Questions",
        agent_id="assessment_generator",
        task_type="create_assessment",
        description="Generate assessment questions",
        output_mapping={"questions": "result.questions"}
    ).agent_task(
        name="Create Rubric",
        agent_id="assessment_generator",
        task_type="create_rubric",
        description="Create grading rubric",
        output_mapping={"rubric": "result.rubric"}
    )
    
    return builder.build()


def create_feedback_workflow() -> Workflow:
    """Create a student feedback workflow template."""
    builder = WorkflowBuilder(
        name="Student Feedback Workflow",
        description="Comprehensive student feedback generation"
    )
    
    builder.agent_task(
        name="Analyze Performance",
        agent_id="assessment_generator",
        task_type="analyze_performance",
        description="Analyze student performance data",
        output_mapping={"analysis": "result.analysis"}
    ).agent_task(
        name="Compose Feedback",
        agent_id="feedback_composer",
        task_type="compose_feedback",
        description="Compose personalized feedback",
        output_mapping={"feedback": "result.feedback"}
    )
    
    return builder.build()
