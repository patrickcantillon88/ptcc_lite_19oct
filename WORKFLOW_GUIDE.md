# PTCC Workflow System Guide

Complete guide to creating and executing multi-agent workflows in PTCC.

## Overview

The PTCC Workflow System enables you to chain multiple AI agents together to accomplish complex educational tasks. Instead of running agents individually, workflows allow you to create sophisticated pipelines that automatically coordinate multiple agents with data flow, error handling, and performance tracking.

## Key Concepts

### Workflows
A **workflow** is a directed acyclic graph (DAG) of nodes that represents a multi-step process. Each node can be:
- **Agent Task**: Executes an AI agent with specific inputs
- **Transform**: Processes/transforms data between nodes
- **Condition**: Branches based on conditions
- **Human Review**: Pauses for human input

### Workflow Engine
The **WorkflowEngine** orchestrates workflow execution, manages state, handles errors, and tracks performance.

### Workflow Builder
The **WorkflowBuilder** provides a fluent API for creating workflows programmatically.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Workflow Engine                       │
│  - Workflow registration                                 │
│  - Execution orchestration                               │
│  - State management                                      │
│  - Error handling                                        │
└──────────┬───────────────────────────────────────────────┘
           │
  ┌────────▼─────────┐
  │    Workflow      │
  │  - Node graph    │
  │  - Data flow     │
  │  - Validation    │
  └────────┬─────────┘
           │
    ┌──────▼──────────────────────────────────┐
    │            Workflow Nodes               │
    │  ┌─────────┐  ┌────────┐  ┌─────────┐ │
    │  │Agent    │  │Transform│  │Condition│ │
    │  │Task     │  │         │  │         │ │
    │  └─────────┘  └────────┘  └─────────┘ │
    └─────────────────────────────────────────┘
```

## Quick Start

### 1. Using Pre-built Templates

The simplest way to use workflows is via pre-built templates:

```python
from examples.api_client_example import PTCCClient

client = PTCCClient()

# Use lesson planning workflow
result = client.quick_lesson_plan(
    grade="5th",
    subject="Science",
    topic="Solar System",
    user_id="teacher123"
)

print(result['lesson_plan'])
```

### 2. Using cURL

```bash
# Execute lesson planning workflow
curl -X POST "http://localhost:8001/api/workflows/quick/lesson-plan" \
  -H "Content-Type: application/json" \
  -d '{
    "grade": "5th",
    "subject": "Science",
    "topic": "Solar System",
    "duration": "45 minutes",
    "user_id": "teacher123"
  }'
```

## Pre-built Workflow Templates

### 1. Lesson Planning Workflow

Creates comprehensive lesson plans through multiple stages:

**Workflow Steps:**
1. **Research Standards** - Identifies relevant curriculum standards
2. **Create Outline** - Develops lesson structure
3. **Develop Content** - Creates full lesson content
4. **Add Differentiation** - Adds differentiation strategies

**Usage:**
```python
from backend.core.workflow_engine import (
    WorkflowEngine,
    create_lesson_planning_workflow
)
from backend.core.agent_orchestrator import AgentOrchestrator

# Initialize
orchestrator = AgentOrchestrator()
engine = WorkflowEngine(orchestrator)

# Register workflow
workflow = create_lesson_planning_workflow()
engine.register_workflow(workflow)

# Execute
execution = engine.execute_workflow(
    workflow_id=workflow.workflow_id,
    input_data={
        "grade": "5th",
        "subject": "Science",
        "topic": "Photosynthesis",
        "duration": "45 minutes"
    },
    user_id="teacher_001"
)

print(f"Lesson Plan: {execution.context['final_plan']}")
print(f"Execution Time: {execution.total_execution_time_ms}ms")
```

### 2. Assessment Creation Workflow

Generates assessments with questions and rubrics:

**Workflow Steps:**
1. **Identify Standards** - Determines assessment standards
2. **Generate Questions** - Creates assessment questions
3. **Create Rubric** - Develops grading rubric

**Usage:**
```python
from backend.core.workflow_engine import create_assessment_workflow

workflow = create_assessment_workflow()
engine.register_workflow(workflow)

execution = engine.execute_workflow(
    workflow_id=workflow.workflow_id,
    input_data={
        "topic": "Photosynthesis",
        "grade": "5th",
        "question_count": 5,
        "question_types": ["multiple_choice", "short_answer"]
    },
    user_id="teacher_001"
)

print(f"Questions: {execution.context['questions']}")
print(f"Rubric: {execution.context['rubric']}")
```

### 3. Student Feedback Workflow

Creates personalized student feedback:

**Workflow Steps:**
1. **Analyze Performance** - Analyzes student data
2. **Compose Feedback** - Generates personalized feedback

**Usage:**
```python
from backend.core.workflow_engine import create_feedback_workflow

workflow = create_feedback_workflow()
engine.register_workflow(workflow)

execution = engine.execute_workflow(
    workflow_id=workflow.workflow_id,
    input_data={
        "student_name": "Alex",
        "assignment": "Photosynthesis Lab",
        "score": 85,
        "strengths": ["Clear explanation", "Good diagrams"],
        "improvements": ["More detail", "Include examples"]
    },
    user_id="teacher_001"
)

print(execution.context['feedback'])
```

## Building Custom Workflows

### Using WorkflowBuilder

The fluent API makes it easy to create custom workflows:

```python
from backend.core.workflow_engine import WorkflowBuilder

# Create custom workflow
builder = WorkflowBuilder(
    name="Custom Research Workflow",
    description="Research and summarize a topic"
)

workflow = (builder
    .agent_task(
        name="Research Topic",
        agent_id="research_agent",
        task_type="research",
        description="Research the topic",
        output_mapping={"research_data": "result.research"}
    )
    .agent_task(
        name="Summarize Findings",
        agent_id="summarization_agent",
        task_type="summarize",
        description="Summarize research findings",
        input_mapping={"content": "research_data"},
        output_mapping={"summary": "result.summary"}
    )
    .agent_task(
        name="Create Bibliography",
        agent_id="citation_agent",
        task_type="create_bibliography",
        description="Generate citations",
        output_mapping={"bibliography": "result.citations"}
    )
    .build()
)

# Register and execute
engine.register_workflow(workflow)
execution = engine.execute_workflow(
    workflow_id=workflow.workflow_id,
    input_data={"topic": "Climate Change Education"},
    user_id="teacher_001"
)
```

### Adding Data Transformations

Transform data between nodes:

```python
def grade_classifier(data):
    """Classify grade level into categories."""
    grade = data.get("grade", "")
    if "K" in grade or any(str(i) in grade for i in range(1, 4)):
        return {"category": "elementary"}
    elif any(str(i) in grade for i in range(4, 7)):
        return {"category": "middle"}
    else:
        return {"category": "high"}

workflow = (builder
    .transform(
        name="Classify Grade",
        transform_fn=grade_classifier,
        description="Categorize grade level"
    )
    .agent_task(
        name="Generate Content",
        agent_id="content_generator",
        task_type="generate",
        description="Generate grade-appropriate content"
    )
    .build()
)
```

### Adding Conditional Branching

Branch based on conditions:

```python
def needs_differentiation(data):
    """Check if differentiation is needed."""
    return data.get("student_level") != "on_level"

workflow = (builder
    .condition(
        name="Check Level",
        condition_fn=needs_differentiation,
        description="Determine if differentiation needed"
    )
    .build()
)
```

## Data Flow & Mapping

### Input/Output Mapping

Control data flow between nodes using mapping:

```python
.agent_task(
    name="Node 1",
    agent_id="agent1",
    task_type="task1",
    output_mapping={
        "standards": "result.curriculum_standards",
        "objectives": "result.learning_objectives"
    }
)
.agent_task(
    name="Node 2",
    agent_id="agent2",
    task_type="task2",
    input_mapping={
        "curriculum": "standards",
        "goals": "objectives"
    }
)
```

### Nested Field Access

Use dot notation for nested fields:

```python
output_mapping={
    "student_name": "result.student.name",
    "performance": "result.assessment.score"
}
```

## Error Handling

### Retry Configuration

Configure retries for resilient execution:

```python
from backend.core.workflow_engine import WorkflowNode, WorkflowNodeType

node = WorkflowNode(
    node_id="resilient_task",
    node_type=WorkflowNodeType.AGENT_TASK,
    name="Task with Retries",
    agent_id="agent1",
    task_type="task",
    retry_count=5,  # Retry up to 5 times
    timeout_seconds=600  # 10 minute timeout
)
```

### Error Handling Nodes

Specify fallback nodes for errors:

```python
node.on_error = "error_handler_node_id"
```

## Performance Monitoring

### Track Execution

Monitor workflow performance:

```python
execution = engine.execute_workflow(...)

print(f"Status: {execution.status.value}")
print(f"Total Time: {execution.total_execution_time_ms}ms")
print(f"Completed Nodes: {len(execution.completed_nodes)}")
print(f"Failed Nodes: {len(execution.failed_nodes)}")

# Per-node timing
for node_id, time_ms in execution.node_execution_times.items():
    print(f"  {node_id}: {time_ms}ms")
```

### Get Statistics

Query workflow statistics via API:

```bash
# Overall stats
curl "http://localhost:8001/api/workflows/stats/overview"

# Workflow-specific stats
curl "http://localhost:8001/api/workflows/stats/{workflow_id}"
```

## API Endpoints

### List Workflows

```bash
GET /api/workflows/
```

```python
workflows = client.get("/api/workflows/")
```

### Get Workflow Details

```bash
GET /api/workflows/{workflow_id}
```

### Execute Workflow

```bash
POST /api/workflows/execute
{
  "workflow_id": "workflow-uuid",
  "input_data": {...},
  "user_id": "teacher123",
  "context": {...}
}
```

### Get Execution Status

```bash
GET /api/workflows/executions/{execution_id}
```

### List Templates

```bash
GET /api/workflows/templates/
```

### Quick Actions

```bash
# Lesson Plan
POST /api/workflows/quick/lesson-plan

# Assessment
POST /api/workflows/quick/assessment
```

## Best Practices

### 1. Design for Modularity

Break complex tasks into smaller, reusable nodes:

```python
# ✅ Good: Modular
builder.agent_task("Research", ...)
       .agent_task("Analyze", ...)
       .agent_task("Synthesize", ...)

# ❌ Bad: Monolithic
builder.agent_task("DoEverything", ...)
```

### 2. Use Descriptive Names

Make workflows self-documenting:

```python
# ✅ Good
.agent_task(
    name="Identify State Standards",
    description="Research CCSS standards for grade level"
)

# ❌ Bad
.agent_task(name="Task 1", description="")
```

### 3. Map Data Explicitly

Be explicit about data flow:

```python
# ✅ Good: Clear mapping
output_mapping={"standards": "result.identified_standards"}

# ❌ Bad: Implicit
# (relying on default behavior)
```

### 4. Handle Errors Gracefully

Always plan for failures:

```python
node.on_error = "fallback_node"
node.retry_count = 3
```

### 5. Monitor Performance

Track and optimize:

```python
# Review execution times
for node_id, time_ms in execution.node_execution_times.items():
    if time_ms > 5000:  # Flag slow nodes
        logger.warning(f"Slow node: {node_id} took {time_ms}ms")
```

## Advanced Patterns

### Fan-Out / Fan-In

Execute multiple paths in parallel (future feature):

```python
# Coming soon: Parallel execution
.parallel(
    name="Generate Variations",
    nodes=[
        ("elementary_version", "agent1", "generate"),
        ("middle_version", "agent2", "generate"),
        ("high_version", "agent3", "generate")
    ]
)
```

### Recursive Workflows

Workflows calling other workflows (future feature):

```python
# Coming soon: Workflow composition
.workflow_task(
    name="Sub-Workflow",
    workflow_id="sub_workflow_id"
)
```

### Human-in-the-Loop

Pause for human review (future feature):

```python
# Coming soon: Human review nodes
.human_review(
    name="Review Draft",
    review_type="approval"
)
```

## Troubleshooting

### Workflow Validation Errors

```python
workflow = builder.build()  # May raise ValueError

is_valid, errors = workflow.validate()
if not is_valid:
    for error in errors:
        print(f"Error: {error}")
```

### Execution Failures

Check execution status:

```python
if execution.status == WorkflowStatus.FAILED:
    print("Errors:")
    for error in execution.error_messages:
        print(f"  - {error}")
    
    print("\nFailed Nodes:")
    for node_id in execution.failed_nodes:
        print(f"  - {node_id}")
```

### Performance Issues

Identify bottlenecks:

```python
# Find slowest nodes
sorted_times = sorted(
    execution.node_execution_times.items(),
    key=lambda x: x[1],
    reverse=True
)

print("Top 5 slowest nodes:")
for node_id, time_ms in sorted_times[:5]:
    print(f"  {node_id}: {time_ms}ms")
```

## Examples

### Complete Example: Comprehensive Lesson Planning

```python
from backend.core.workflow_engine import WorkflowBuilder
from backend.core.agent_orchestrator import AgentOrchestrator

# Initialize
orchestrator = AgentOrchestrator()
engine = WorkflowEngine(orchestrator)

# Build workflow
builder = WorkflowBuilder(
    name="Comprehensive Lesson Planning",
    description="Full lesson planning with standards alignment"
)

workflow = (builder
    # Step 1: Research
    .agent_task(
        name="Research Standards",
        agent_id="curriculum_advisor",
        task_type="research_standards",
        description="Identify relevant curriculum standards",
        output_mapping={"standards": "result.standards"}
    )
    # Step 2: Initial Planning
    .agent_task(
        name="Create Outline",
        agent_id="lesson_plan_generator",
        task_type="create_outline",
        description="Develop lesson structure",
        output_mapping={"outline": "result.outline"}
    )
    # Step 3: Content Development
    .agent_task(
        name="Develop Activities",
        agent_id="lesson_plan_generator",
        task_type="create_activities",
        description="Create learning activities",
        output_mapping={"activities": "result.activities"}
    )
    # Step 4: Differentiation
    .agent_task(
        name="Add Differentiation",
        agent_id="differentiation_specialist",
        task_type="differentiate",
        description="Add differentiation strategies",
        output_mapping={"differentiated": "result.strategies"}
    )
    # Step 5: Assessment
    .agent_task(
        name="Create Assessment",
        agent_id="assessment_generator",
        task_type="create_formative",
        description="Create formative assessment",
        output_mapping={"assessment": "result.assessment"}
    )
    # Step 6: Final Review
    .agent_task(
        name="Quality Review",
        agent_id="quality_agent",
        task_type="review_lesson",
        description="Final quality check",
        output_mapping={"final_plan": "result.reviewed_plan"}
    )
    .build()
)

# Register
engine.register_workflow(workflow)

# Execute
execution = engine.execute_workflow(
    workflow_id=workflow.workflow_id,
    input_data={
        "grade": "5th",
        "subject": "Science",
        "topic": "Photosynthesis",
        "duration": "45 minutes",
        "learning_objectives": [
            "Understand the process of photosynthesis",
            "Identify parts of a plant cell",
            "Explain the role of chlorophyll"
        ]
    },
    user_id="teacher_001"
)

# Display results
print(f"\n{'='*60}")
print(f"Lesson Planning Complete!")
print(f"{'='*60}")
print(f"Status: {execution.status.value}")
print(f"Total Time: {execution.total_execution_time_ms}ms")
print(f"\nFinal Lesson Plan:")
print(execution.context['final_plan'])
```

## Next Steps

1. **Explore Templates** - Try the pre-built workflow templates
2. **Build Custom Workflows** - Create workflows for your specific needs
3. **Monitor Performance** - Track and optimize workflow execution
4. **Share Workflows** - Export and share successful workflows
5. **Provide Feedback** - Help improve the workflow system

## Resources

- **API Documentation**: http://localhost:8001/docs
- **Quick Start Guide**: QUICKSTART.md
- **Architecture**: IMPLEMENTATION_SUMMARY.md
- **Agent Guide**: PHASE3_COMPLETE.md

## Support

For issues or questions:
- Check workflow validation errors
- Review execution logs
- Monitor node performance
- Inspect data flow between nodes
