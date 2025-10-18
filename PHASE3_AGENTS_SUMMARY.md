# Phase 3 Implementation Summary: Intelligent Agents System

## Overview

Phase 3 completes the intelligent agents infrastructure that powers proactive behavior context and intervention recommendations. The system consists of three specialized agents coordinated by an orchestrator, exposing analysis via a comprehensive API.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────┐
│        AgentOrchestrator (agents_api.py)    │
│  Coordinates all agents & aggregates results │
└────────────────────┬────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌────────┐ ┌────────┐ ┌────────────┐
    │Period  │ │CCA     │ │Accommodation
    │Briefing│ │Engage  │ │Compliance
    │Agent   │ │Agent   │ │Agent
    └────────┘ └────────┘ └────────────┘
        │            │            │
        └────────────┼────────────┘
                     │
              ┌──────▼──────┐
              │  /api/agents│
              │   Endpoints │
              └─────────────┘
```

### File Structure

```
backend/api/agents/
├── __init__.py                          # Package initialization
├── period_briefing_agent.py             # Pre-lesson intelligence agent
├── cca_engagement_agent.py              # Enrichment & engagement agent
├── accommodation_compliance_agent.py    # Accessibility compliance agent
└── agent_orchestrator.py                # Central coordinator

backend/api/
└── agents_api.py                        # FastAPI endpoint definitions

backend/core/
└── base_agent.py                        # Base classes (StudentContext, AgentOutput)
```

## Agents

### 1. PeriodBriefingAgent
**Purpose**: Pre-lesson context and intelligence  
**Input**: Student profile, behavior flags, accommodations, timetable data  
**Output**: Comprehensive briefing for lesson preparation  
**Key Features**:
- Staff context (teacher/TA presence, specialist info)
- Active accommodations status
- Behavior flag alerts
- Classroom setup recommendations
- At-risk identification

**Example Output**:
```
📋 PERIOD BRIEFING - 14:30 Mathematics (Period 4)
Student: Alex Johnson | Class: 9A
Lesson: Mr. Smith + TA | Specialist: NO | Room: A12

ALERTS:
  [AT-RISK] - Requires proactive engagement
  [BEHAVIOR-CONCERN] - Energy management needed

ACCOMMODATIONS ACTIVE:
  ✓ Seating arrangement (front, near TA)
  ✓ Movement breaks (max 30 min seated)
  ✓ Sensory break access

SETUP CHECKLIST:
  1. Verify seating is front of room
  2. Brief Alex on movement break option
  3. Alert TA to proximity support
  4. Confirm 30-min check-in before fatigue
```

### 2. CCAEngagementAgent
**Purpose**: Enrichment recommendations and engagement optimization  
**Input**: Behavior flags, accommodations, student profile  
**Output**: Activity recommendations and engagement strategies  
**Key Features**:
- CCA type recommendations by behavior profile
- At-risk engagement prioritization
- Anxiety management through structured activities
- Energy outlet matching for behavior concerns
- Leadership opportunity identification

**Example Output**:
```
🎯 CCA ENGAGEMENT - Support Needed
Student: Jamie | Class: 9B | Time: 14:30

Student Profile:
  [ANXIETY]
  [BEHAVIOR-CONCERN]

Engagement Strategy:
  ✓ Consider: Sports CCA (Physical outlet for energy management)
  ✓ Consider: Drama CCA (Confidence and social skills in structured setting)
  ✓ Consider: Leadership CCA (Structure and responsibility)

Priority: MEDIUM
Action Required: YES
```

### 3. AccommodationComplianceAgent
**Purpose**: Legal compliance and accessibility verification  
**Input**: Active accommodations, student profile  
**Output**: Implementation checklists and compliance reminders  
**Key Features**:
- Accommodation categorization (physical, sensory, learning, behavioral, medical, pastoral, dietary)
- Daily implementation checklists
- Compliance verification
- Accessibility legal requirements
- Medical protocol reminders

**Example Output**:
```
✅ LESSON SETUP CHECKLIST - 14:30 Mathematics (Period 4)
Student: Alex Johnson | Class: 9A

ACCESSIBILITY (Priority: HIGH)
  ☐ Seating: Position Alex appropriately (front, near support)
  ☐ Sensory: Minimize overstimulation during lesson

BEHAVIORAL SUPPORT (Priority: MEDIUM)
  ☐ Movement: Schedule movement breaks max 30 min seated
  ☐ Boundaries: Establish clear expectations at lesson start

PASTORAL SUPPORT (Priority: HIGH)
  ☐ Check-in: Brief wellbeing check before end of period

Total: 5 accommodations require setup verification
```

## API Endpoints

### Analysis Endpoints

#### 1. Full Student Analysis
```bash
POST /api/agents/analyze/{student_id}
  ?class_code=9A
  ?period_code=P1
  ?agents=period_briefing,cca_engagement

# Response
{
  "student_id": 1,
  "student_name": "Alex Johnson",
  "class_code": "9A",
  "timestamp": "2024-01-15T14:30:00",
  "summary": "...",
  "high_priority_count": 2,
  "agents": {
    "period_briefing": {...},
    "cca_engagement": {...},
    "accommodation_compliance": {...}
  }
}
```

#### 2. Display Format (CLI/Testing)
```bash
GET /api/agents/analyze/{student_id}/display

# Response: Text formatted for terminal display
```

#### 3. Individual Agent Analysis
```bash
POST /api/agents/analyze/{student_id}/agent/{agent_name}
  ?class_code=9A

# Returns single agent's analysis with full details
```

### Information Endpoints

#### 4. List All Agents
```bash
GET /api/agents/list

# Response
{
  "agents": [
    {
      "name": "period_briefing",
      "display_name": "Period Briefing Agent",
      "description": "Pre-lesson intelligence...",
      "intervention_type": "briefing",
      "focus_areas": [...]
    },
    ...
  ],
  "total_agents": 3
}
```

#### 5. Get Agent Metadata
```bash
GET /api/agents/agents/{agent_name}

# Returns inputs, outputs, priority factors, use cases
```

#### 6. Health Check
```bash
GET /api/agents/health

# Response
{
  "status": "healthy",
  "agents": ["period_briefing", "cca_engagement", "accommodation_compliance"],
  "agent_count": 3
}
```

## Usage Examples

### Example 1: Pre-Lesson Briefing Workflow

```python
# Get full context analysis for a student before Period 3
response = requests.post(
    "http://localhost:8001/api/agents/analyze/42",
    params={
        "class_code": "9A",
        "period_code": "P3"
    }
)

# High-priority alerts are at the top of the response
high_alerts = response.json()['summary']
print(high_alerts)  # Teacher sees critical flags immediately

# Detailed agent outputs for lesson planning
for agent_name, analysis in response.json()['agents'].items():
    print(f"\n{analysis['title']}")
    print(analysis['message'])
    for action in analysis['recommended_actions']:
        print(f"  → {action}")
```

### Example 2: CLI Display for Quick Testing

```bash
# View formatted analysis in terminal
curl "http://localhost:8001/api/agents/analyze/42/display"

# Pipe to file for record keeping
curl "http://localhost:8001/api/agents/analyze/42/display" > briefing_student42.txt
```

### Example 3: Enrichment Planning

```python
# Get CCA recommendations for a specific student
response = requests.post(
    "http://localhost:8001/api/agents/analyze/15/agent/cca_engagement"
)

recommendations = response.json()['analysis']['recommended_actions']
print("CCA Recommendations:")
for rec in recommendations:
    print(f"  • {rec}")
```

## Integration Points

### 1. Frontend Dashboard
- Display agent recommendations on student profile page
- Show high-priority alerts in teacher home screen
- CCA recommendations in student development section

### 2. Mobile PWA
- Quick briefing before each lesson
- Accommodation reminders during lesson
- Post-lesson engagement suggestions

### 3. Automation Triggers
- Auto-generate briefings 10 minutes before each lesson
- Send accommodation compliance reminders to TAs
- Weekly enrichment planning recommendations

## Data Flow

### Input Processing
1. Request arrives with student_id and optional parameters
2. `_build_student_context()` constructs StudentContext from database:
   - Student info and class assignment
   - Behavior flags from notes/quick logs
   - Active accommodations
   - Timetable data (if available)

3. Orchestrator dispatches to registered agents

### Agent Analysis
1. Each agent analyzes StudentContext independently
2. Generates prioritized output (high/medium/low)
3. Returns recommended actions

### Output Aggregation
1. Orchestrator collects all agent outputs
2. Sorts by priority (high → medium → low)
3. Formats for target interface (API, CLI, display)

## Priority Determination

### High Priority Triggers
- At-risk student identified
- Medical accommodations present
- Multiple behavior concerns
- Accessibility requirements

### Medium Priority Triggers
- Anxiety flags present
- Behavior concerns flagged
- Learning support accommodations
- Single accommodation type

### Low Priority Triggers
- No flags or accommodations
- Routine monitoring
- Positive engagement profile

## Testing

### Manual Testing via API

```bash
# Test health endpoint
curl http://localhost:8001/api/agents/health

# Test analysis with real student
curl -X POST http://localhost:8001/api/agents/analyze/1

# Test display format
curl http://localhost:8001/api/agents/analyze/1/display

# Test specific agent
curl -X POST http://localhost:8001/api/agents/analyze/1/agent/period_briefing
```

### Testing with Sample Data

```python
# Create StudentContext manually for testing
context = StudentContext(
    student_id=1,
    student_name="Test Student",
    class_code="9A",
    current_day="Monday",
    current_period=1,
    current_time=datetime.now(),
    current_subject="Mathematics",
    lesson_type="Core",
    specialist_name=None,
    class_teacher="Ms. Smith",
    ta_present=True,
    specialist_present=False,
    recent_logs=[],
    behavior_flags=['[AT-RISK]', '[BEHAVIOR-CONCERN]'],
    active_accommodations=[{'name': 'seating arrangement'}],
    next_period_subject="English",
    is_transition_period=False,
    time_since_last_break=45
)

# Run orchestrator
orchestrator = AgentOrchestrator()
result = orchestrator.analyze_student(context)
print(orchestrator.format_for_display(result))
```

## Future Enhancements

1. **CCA Enrollment Integration**: Link to actual CCA enrollment data
2. **Timetable Lookup**: Pull current period/subject from timetable
3. **Incident Prediction**: ML model for behavior incident forecasting
4. **Parent Communication**: Auto-generate parent update emails
5. **Staff Workload**: Balance accommodation implementation across staff
6. **Historical Trending**: Track agent recommendations over time
7. **Performance Metrics**: Measure impact of recommendations

## Configuration

Agent behavior can be customized via environment variables or config files:

```yaml
# config/config.yaml
agents:
  period_briefing:
    priority_threshold: high
    include_staff_context: true
  
  cca_engagement:
    max_recommendations: 3
    focus_at_risk: true
  
  accommodation_compliance:
    daily_reminders: true
    legal_compliance_mode: strict
```

## Documentation

- **API Reference**: Full endpoint documentation with examples
- **Agent Behavior**: Detailed logic for each agent
- **Data Models**: StudentContext and AgentOutput schemas
- **Integration Guide**: How to integrate with other PTCC systems

## Completion Status

✅ Agent orchestrator implemented  
✅ Three specialized agents created  
✅ API endpoints defined and registered  
✅ Input/output handling complete  
✅ Priority determination logic  
✅ Text formatting for multiple interfaces  
✅ Error handling and validation  

## Next Steps

1. **Phase 3B (Optional)**: Add more specialized agents
   - LearningPathAgent: Personalized learning recommendations
   - BehaviorTrendAgent: Historical pattern analysis
   - PeerGroupAgent: Positive peer influence strategies

2. **Integration**: Wire agents into frontend components
   - Display on student profile pages
   - Pre-lesson briefing dashboard
   - Teacher notifications

3. **Testing & Validation**: Gather teacher feedback on recommendations

4. **Performance Optimization**: Cache frequently accessed data
