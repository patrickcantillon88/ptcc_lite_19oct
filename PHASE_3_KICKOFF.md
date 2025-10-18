# Phase 3 Kickoff: Intelligent Agents
**Date**: 2025-10-17 13:20 UTC  
**Status**: 🚀 PHASE 3 STARTED  
**Infrastructure**: BaseAgent + AgentOrchestrator created  

---

## 🎯 Phase 3 Objectives

Build 3 intelligent agents that use Phase 1 API data + context to generate **proactive interventions**:

1. **PeriodBriefingAgent** - Pre-lesson intelligence (5 mins before period)
2. **CCAEngagementAgent** - Student enrichment recommendations (weekly)
3. **AccommodationComplianceAgent** - Pre-lesson accommodation reminders (10 mins before)

---

## 📋 What's Done

✅ **BaseAgent Infrastructure** (`backend/core/base_agent.py`)
- Abstract base class for all agents
- StudentContext dataclass (complete student state at a moment)
- AgentOutput dataclass (structured agent output)
- AgentOrchestrator for coordinating multiple agents

✅ **Phase 2 Test Page** (`frontend/mobile-pwa/src/components/ContextTestPage.tsx`)
- Wires StaffBoard, TimetableView, StudentContextView
- Allows selecting 4 test students (Marcus, Sophie, Joshua, Freya)
- Ready for Phase 3 agent testing

---

## 🏗️ Architecture Overview

```
StudentContext (rich data)
    ↓
    ├→ PeriodBriefingAgent
    │  Output: "Here's what you need to know about this period"
    │
    ├→ CCAEngagementAgent
    │  Output: "This student should join X CCA for Y reason"
    │
    └→ AccommodationComplianceAgent
       Output: "Before this lesson, ensure Z accommodations"
       
    ↓
AgentOrchestrator (sorts by priority)
    ↓
API Response (JSON) → Frontend → Teacher sees alerts
```

---

## 📊 StudentContext Data Available

Each agent gets complete context:

```python
StudentContext(
    student_id=1,
    student_name="Marcus Thompson",
    class_code="3A",
    
    # Current moment
    current_day="Monday",
    current_period=3,
    current_time=datetime(2025,10,17,9,45),
    
    # What's happening NOW
    current_subject="ICT",
    lesson_type="Specialist",
    specialist_name="Unknown",
    
    # Who's here
    class_teacher="Ms Elena Rodriguez",
    ta_present=True,
    specialist_present=False,
    
    # Recent behavior
    recent_logs=[
        {"log_type": "negative", "category": "off_task", "time": "09:30"},
        {"log_type": "positive", "category": "good_effort", "time": "09:15"},
    ],
    behavior_flags=["[BEHAVIOR-CONCERN]"],  # From student profile
    
    # What Marcus needs
    active_accommodations=[
        {"type": "behavioral", "description": "Impulsivity, movement breaks needed"},
        {"type": "behavioral", "description": "Attention-seeking behavior"},
    ],
    
    # Next up
    next_period_subject="Break",
    is_transition_period=False,
    time_since_last_break=75,  # minutes
)
```

---

## 🔧 How to Build Each Agent

### 1. PeriodBriefingAgent
**File to create**: `backend/api/agents/period_briefing_agent.py`

**Logic**:
```
IF Marcus & ICT specialist period & TA present & hasn't had break in 75min
  → ALERT: "Marcus needs movement break offer at 10:15"
  
IF specialist name is "Unknown"
  → ALERT: "Specialist instructor not confirmed"
  
IF Sophie & perfectionist & recent test period
  → ALERT: "Sophie may need reassurance after assessment"
  
FOR each active accommodation
  → ADD: "Ensure [accommodation] during this period"
```

**Output Example**:
```json
{
  "agent": "PeriodBriefingAgent",
  "student_id": 1,
  "priority": "high",
  "title": "⚠️ PERIOD BRIEFING - 09:45 ICT",
  "message": "🎓 PERIOD BRIEFING - 09:45 ICT (Room Lab)\nClass: 3A | Instructor: Unknown\n\n⚠️ ATTENTION ALERTS:\n• Marcus: Hasn't had break in 75min - offer movement break at 10:15\n• Specialist not confirmed - verify instructor before lesson\n\n✅ ACCOMMODATIONS ACTIVE:\n• Marcus: Movement break every 30min (offer at 10:15)\n• Marcus: Attention-seeking - use positive feedback\n\n💡 RECOMMENDATIONS:\n• Assign Marcus to observer position for first 5 mins\n• Have TA ready to facilitate movement break",
  "recommended_actions": [
    "Offer Marcus movement break at 10:15",
    "Verify specialist instructor",
    "Assign TA to proximity support"
  ]
}
```

### 2. CCAEngagementAgent
**File to create**: `backend/api/agents/cca_engagement_agent.py`

**Logic**:
```
IF student NOT enrolled in any CCA & not at-risk
  → RECOMMEND: "Noah should enroll in Drama (builds confidence)"
  
IF enrolled in anxiety outlet CCA & zero attendance this month
  → ALERT: "Joshua in Basketball (anxiety outlet) - zero attendance"
  → RECOMMEND: "Check barriers; reschedule if needed"
  
IF student in CCA with high engagement
  → SUGGEST: "Consider mentoring role for Marcus in Coding Club"
  
CORRELATE: behavior flags + CCA types
  → Marcus (energy management) → Sports (Football, Basketball)
  → Sophie (perfectionism) → Creative (Art Club, Creative Writing)
  → Grace (anxiety) → Structured (Robotics, Coding)
```

**Output Example**:
```json
{
  "agent": "CCAEngagementAgent",
  "priority": "high",
  "title": "🎯 CCA ENGAGEMENT ANALYSIS",
  "message": "🎯 CCA ENGAGEMENT ANALYSIS\n\n🚨 HIGH PRIORITY:\n• Noah Williams (3A): Not in any CCA; at-risk for disengagement\n  → Recommend: Drama (builds confidence) or Coding Club (problem-solving)\n\n⚠️ CONCERNING DROPS:\n• Joshua Finch: Basketball (anxiety outlet) - 0 attendances in 2 weeks\n  → Action: Check-in on barriers; reschedule if needed\n\n✅ POSITIVE TRENDS:\n• Marcus Thompson: Coding Club (high engagement)\n  → Consider: Mentoring role to expand leadership",
  "recommended_actions": [
    "Enroll Noah in Drama or Coding Club",
    "Check-in with Joshua re: Basketball barriers",
    "Discuss mentoring opportunity with Marcus"
  ]
}
```

### 3. AccommodationComplianceAgent
**File to create**: `backend/api/agents/accommodation_compliance_agent.py`

**Logic**:
```
FOR each student's accommodations:
  IF accommodation_type == "sensory"
    → ADD to environment checklist (lights, noise, seating)
  
  IF accommodation_type == "behavioral"
    → ADD to support checklist (movement breaks, de-escalation)
  
  IF accommodation_type == "social"
    → ADD to pairing checklist (peer buddy, inclusion)

GENERATE: Pre-lesson checklist with ☐ boxes
```

**Output Example**:
```json
{
  "agent": "AccommodationComplianceAgent",
  "priority": "medium",
  "title": "✅ LESSON SETUP CHECKLIST - 10:00 Foundation Learning (3A)",
  "message": "✅ LESSON SETUP CHECKLIST - 10:00 Foundation Learning (3A)\n\nEnvironment:\n☐ Freya Nielsen: Dim classroom lighting (light sensitivity)\n☐ Zoe Martinez: Noise level monitor; ear defenders nearby\n☐ Marcus Thompson: Movement breaks every 30 mins scheduled\n\nBehavior Support:\n☐ Sophie Chen: Reassurance buddy available (anxiety management)\n☐ Noah Williams: Emotional temperature check at 10:15\n\nSeating/Positioning:\n☐ James Park: Visual schedule at transitions visible\n☐ Liam O'Brien: 1:1 position for speech/language focus\n\nQUICK NOTE: Three accommodation needs; allow 2 extra mins setup time",
  "recommended_actions": [
    "Adjust classroom lighting",
    "Have ear defenders available",
    "Brief reassurance buddy",
    "Position TA near James for transitions"
  ]
}
```

---

## 🚀 Implementation Order

**Priority 1: PeriodBriefingAgent** (highest ROI)
- Uses all context data
- Triggers 5 mins before each period (automatic for testing)
- Most immediate teacher value

**Priority 2: AccommodationComplianceAgent** (high ROI)
- Simpler logic (checklist generation)
- Prevents behavioral incidents
- Low complexity

**Priority 3: CCAEngagementAgent** (medium ROI)
- Weekly trigger (slower)
- Enrichment focus
- Complex correlation logic

---

## 📁 Files to Create (Phase 3)

```
backend/
├── api/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── period_briefing_agent.py (NEW)
│   │   ├── cca_engagement_agent.py (NEW)
│   │   └── accommodation_compliance_agent.py (NEW)
│   └── agents_router.py (NEW - 3 endpoints)
│
└── core/
    └── base_agent.py (✅ DONE)
```

---

## 🔌 API Endpoints (Phase 3)

```
GET /api/agents/period-briefing/{student_id}/{class_code}/{day}/{period}
  → Returns PeriodBriefingAgent output for that moment

GET /api/agents/cca-engagement/{student_id}
  → Returns CCAEngagementAgent output

GET /api/agents/accommodation-compliance/{student_id}/{class_code}/{day}/{period}
  → Returns AccommodationComplianceAgent output
```

---

## 📊 Test Workflow

1. **Load ContextTestPage** (Phase 2 wiring)
   - Select Marcus Thompson (3A)
   - Manually set "current time" to Monday 9:45

2. **Call PeriodBriefingAgent API**
   - `GET /api/agents/period-briefing/1/3A/Monday/3`
   - Should return alerts about:
     - Movement break needed
     - Unknown specialist
     - Accommodations active

3. **Call CCAEngagementAgent API**
   - `GET /api/agents/cca-engagement/1`
   - Should return: "Marcus in Coding Club (high engagement)"

4. **Call AccommodationComplianceAgent API**
   - `GET /api/agents/accommodation-compliance/1/3A/Monday/3`
   - Should return: checklist with Marcus's accommodations

5. **Test full orchestrator**
   - Call all 3 agents
   - Verify priority sorting
   - Check JSON output format

---

## 💡 Example: Marcus Thompson Full Briefing

**Scenario**: Monday 9:45, about to start ICT specialist lesson

**StudentContext provided**:
- student_id: 1
- name: Marcus Thompson
- flags: [BEHAVIOR-CONCERN]
- accommodations: movement_breaks (needs break every 30min)
- recent_logs: off_task at 9:30
- last_break: 75 mins ago
- specialist: Unknown
- TA: present

**Agent Outputs**:

1. **PeriodBriefingAgent**:
   - PRIORITY: HIGH
   - ALERTS: "Movement break needed", "Specialist not confirmed"
   - ACTIONS: "Offer break at 10:15", "Verify instructor"

2. **AccommodationComplianceAgent**:
   - PRIORITY: MEDIUM
   - CHECKLIST: "Movement breaks scheduled", "TA proximity support"
   - ACTIONS: "Position TA nearby"

3. **CCAEngagementAgent**:
   - PRIORITY: LOW
   - INSIGHT: "Marcus thriving in Coding Club - consider mentoring"
   - ACTIONS: "Discuss leadership opportunity"

**Orchestrator Output** (sorted by priority):
```json
[
  {agent: "PeriodBriefingAgent", priority: "high", ...},
  {agent: "AccommodationComplianceAgent", priority: "medium", ...},
  {agent: "CCAEngagementAgent", priority: "low", ...}
]
```

---

## 🎯 Success Metrics (Phase 3)

- [x] BaseAgent infrastructure created
- [ ] PeriodBriefingAgent implemented & tested
- [ ] AccommodationComplianceAgent implemented & tested
- [ ] CCAEngagementAgent implemented & tested
- [ ] All 3 agents callable via API
- [ ] Full orchestrator workflow tested
- [ ] Outputs formatted for frontend display
- [ ] Integration test: full day simulation with 4 test students

---

## ⏱️ Estimated Timeline

- **PeriodBriefingAgent**: 2-3 hours (core logic)
- **AccommodationComplianceAgent**: 1-2 hours (checklist generation)
- **CCAEngagementAgent**: 2-3 hours (correlation logic)
- **API Integration**: 1 hour
- **Testing & Debugging**: 2-3 hours
- **Total Phase 3**: 8-12 hours

---

**Status**: Ready to build agents  
**Next**: Implement PeriodBriefingAgent first (highest ROI)  
**Test Page**: Available at ContextTestPage component with test students ready
