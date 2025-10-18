# PTCC Enhancement Plan: Context-Aware Behavior Prediction
**Date**: 2025-10-17 12:41 UTC  
**Status**: PLANNING & IMPLEMENTATION  
**Target Completion**: 3 weeks  
**Priority**: CRITICAL - Unlocks behavior prediction effectiveness

---

## Executive Summary

Current system predicts behavior but **lacks contextual awareness** (who, where, when). This plan adds staff assignments, timetables, CCA coordination, and time-based analysis to make interventions **proactive** not reactive.

**Expected Impact**:
- 40% increase in behavior prediction accuracy
- Real-time intervention triggers based on staff/specialist lesson presence
- Reduced incidents through environmental accommodations
- Teacher-ready "briefing by period" recommendations

---

## Gap Analysis: PDF Data vs. System Implementation

### Data Rich in PDF, Missing in System

| **Domain** | **In PDF** | **In DB** | **In Frontend** | **Priority** | **Impact** |
|-----------|-----------|----------|-----------------|-------------|-----------|
| Staff assignments | ✅ Complete (teacher, TA, LST per class) | ❌ No model | ❌ No UI | 🔴 CRITICAL | Context-aware analysis |
| Timetables | ✅ Detailed (5 complete timetables) | ⚠️ Partial (Schedule table empty) | ❌ No UI | 🔴 CRITICAL | Time-based patterns |
| Specialist lessons | ✅ Embedded in timetables | ❌ Not extracted | ❌ No UI | 🔴 CRITICAL | Behavior by subject/lesson type |
| CCA assignments | ✅ Per-student enrollment | ✅ CCA table exists | ⚠️ API only | 🟡 HIGH | Intervention via enrichment |
| Accommodations | ✅ Detailed per student | ❌ No model | ❌ No UI | 🟡 HIGH | Environmental factors |
| Intervention frameworks | ✅ 6 documented strategies | ⚠️ Text-based in logs | ⚠️ Generic | 🟡 HIGH | Structured interventions |

---

## Implementation Roadmap

### Phase 1: Data Infrastructure (Week 1)

#### 1.1 Staff Assignment System
**Goal**: Enable staff context in behavior analysis

**Database Changes**:
```
Table: Staff
- id (PK)
- name (string)
- role (enum: 'Class Teacher', 'TA', 'Learning Support Teacher', 'Specialist')
- class_code (FK to class)
- specialties (JSON: ['ICT', 'PE', 'Music'])
- availability_schedule (JSON: day/period mapping)

Table: StaffAssignment
- id (PK)
- staff_id (FK)
- class_code (string)
- role (string)
- term (string)
- start_date
- end_date
```

**Implementation Tasks**:
- [ ] Add Staff and StaffAssignment models to `database_models.py`
- [ ] Create migration to populate staff from PDF data (see PDF table below)
- [ ] Add staff_id FK to QuickLog (optional, but recommended for context)
- [ ] Create `/api/staff/` endpoints:
  - `GET /api/staff/by-class/{class_code}` - Get class staff
  - `GET /api/staff/schedule/{staff_id}` - Get staff availability
  - `GET /api/staff/search` - Search staff by name/role

**PDF Data to Import**:
```
3A: Ms Elena Rodriguez (teacher), Mr David Chen (LS), Ms Linh Tran (TA)
4B: Mr Tariq Hassan (teacher), Ms Catherine Okafor (LS), Mr Duc Nguyen (TA)
5C: Mr James Watson (teacher), Ms Fiona Liu (LS), Ms Anh Vo (TA)
6D: Ms Rebecca Singh (teacher), Mr Michael O'Connor (LS), Ms Hoa Tran (TA)

Specialists: Various (ICT, PE, Music, Drama, Robotics, etc.)
```

**Behavior Prediction Gain**: "Which staff member was present during incident?"

---

#### 1.2 Timetable System
**Goal**: Enable time-based behavior correlation

**Database Changes**:
```
Table: Timetable (enhance existing Schedule)
- id (PK)
- class_code (string, FK)
- day_of_week (enum)
- period (int: 1-6)
- start_time (time)
- end_time (time)
- subject (string)
- lesson_type (enum: 'Literacy', 'Numeracy', 'Foundation', 'Specialist', 'CCA')
- specialist_name (string, nullable)
- room (string)
- notes (text)

Table: SpecialistLessonSchedule
- id (PK)
- class_code (string)
- day_of_week (enum)
- period (int)
- specialist_type (enum: 'ICT', 'PE', 'Music', 'Drama', 'Art')
- instructor_name (string)
```

**Implementation Tasks**:
- [ ] Enhance/populate Schedule table from PDF timetables
- [ ] Create SpecialistLessonSchedule table
- [ ] Add API endpoints:
  - `GET /api/timetable/class/{class_code}` - Full class timetable
  - `GET /api/timetable/today/{class_code}` - Today's lessons
  - `GET /api/timetable/period/{class_code}/{day}/{period}` - Specific period details
  - `GET /api/timetable/specialist-lessons/{class_code}` - All specialist lessons

**PDF Data to Import**:
```
3A: Mon 9:00-9:45 Literacy (Phonics), 9:45-10:15 ICT Specialist, etc.
(See full timetable in PDF pages 6-7)
```

**Behavior Prediction Gain**: "Did incident occur during transition? During specialist lesson?"

---

#### 1.3 CCA Enrollment System
**Goal**: Link CCA participation to behavior intervention

**Database Changes** (enhance existing):
```
Table: CCA (already exists, enhance)
- Add: term (string)
- Add: schedule (JSON: day, time, location)
- Add: leader_id (FK to Staff)
- Add: description (text)
- Add: capacity (int)
- Add: enrollment_status (enum: 'active', 'waitlist', 'inactive')

Table: StudentCCAEnrollment
- id (PK)
- student_id (FK)
- cca_id (FK)
- term (string)
- status (enum: 'enrolled', 'waitlist', 'dropped')
- enrollment_date
- dropout_date (nullable)
- attendance_count (int)
```

**Implementation Tasks**:
- [ ] Enhance CCA model in `database_models.py`
- [ ] Create StudentCCAEnrollment table
- [ ] Add API endpoints:
  - `GET /api/cca/student/{student_id}` - Student's CCA enrollments
  - `GET /api/cca/class/{class_code}` - All CCAs for class
  - `GET /api/cca/{cca_id}/enrollment` - Enrollment status
  - `POST /api/cca/{cca_id}/enroll` - Enroll student

**PDF Data to Import**:
```
Joshua Finch: Basketball (Tue 3:30-4:30) - Anxiety management outlet
Noah Williams: Not enrolled - recommended for engagement
(See CCA section in PDF pages 5-6)
```

**Behavior Prediction Gain**: "Is student engaging with prescribed CCA outlet?"

---

#### 1.4 Student Accommodations System
**Goal**: Track environmental factors affecting behavior

**Database Changes**:
```
Table: StudentAccommodations
- id (PK)
- student_id (FK)
- accommodation_type (enum: 'sensory', 'seating', 'schedule', 'equipment')
- description (string)
- implementation_details (text)
- active (boolean)
- effective_date
- notes (text)
```

**Implementation Tasks**:
- [ ] Create StudentAccommodations table
- [ ] Add API endpoints:
  - `GET /api/accommodations/student/{student_id}` - All accommodations
  - `GET /api/accommodations/active/{student_id}` - Active today
  - `POST /api/accommodations` - Add accommodation
  - `PUT /api/accommodations/{id}` - Update

**PDF Data to Import**:
```
Sophie Chen: Perfectionist, needs reassurance, anxiety buddy checks
Zoe Martinez: Noise sensitivity, ear defenders in assemblies
Freya Nielsen: Light sensitivity, blue-light filter on screens
(See individual profiles in PDF pages 3-4)
```

**Behavior Prediction Gain**: "Are accommodations in place for this environment?"

---

### Phase 2: Frontend Implementation (Week 2)

#### 2.1 Staff Assignment Board
**Components**:
- `StaffDirectory` - List of all staff by class
- `StaffSchedule` - Individual staff availability
- `ClassStaffView` - Who's assigned to this class/period

**Screens**:
- Classroom Management → Staff Assignments
- Show: Teacher name, role, specialties, availability
- Action: Assign/reassign staff to periods

**Data Flow**:
```
Staff API → Staff Card Components → Display current staff
Alert: "Ms Rodriguez not available for 10:30 ICT"
```

#### 2.2 Timetable Dashboard
**Components**:
- `WeeklyTimetable` - Full class schedule
- `TodayAtAGlance` - Current day lessons
- `PeriodDetails` - Who's teaching, what room, what accommodation needs
- `TransitionWarning` - Flag difficult transitions

**Screens**:
- Dashboard → Class Schedule widget
- Classroom Management → View Full Timetable
- Student Profile → Student's Timetable

**Data Flow**:
```
Timetable API → Period widgets → Highlight specialist lessons
Show: "ICT with unknown specialist - check lesson notes"
```

#### 2.3 CCA Enrollment View
**Components**:
- `StudentCCAStatus` - What CCAs is student in
- `CCADirectory` - All available CCAs
- `EnrollmentManagement` - Add/remove CCA

**Screens**:
- Student Profile → CCA Enrollments
- Classroom Management → CCA Overview (show who's NOT in any CCA)
- Intervention Hub → "Recommend CCA for engagement"

**Data Flow**:
```
Student API → CCA enrollments → Show in profile
Alert: "Joshua in Basketball (anxiety outlet) - consistent attendance?"
```

#### 2.4 "Today at a Glance" Dashboard
**Components**:
- Timeline showing: Staff, Lessons, CCA, Key behaviors
- Heat map: "Difficult periods for this student"
- Accommodation checklist: "Before this lesson, ensure..."

**Screen**:
- New dashboard widget for each class/student
- Shows real-time context for proactive intervention

---

### Phase 3: AI Agent Integration (Week 3)

#### 3.1 Period Briefing Agent
**Purpose**: Generate "before lesson" briefing with full context

**Output Example**:
```
🎓 PERIOD BRIEFING - 10:30 ICT (Room 1A)
Class: 4B | Instructor: [Specialist Name]

⚠️ ATTENTION ALERTS:
- Marcus Thompson: Needs movement break offer at 10:45 (proactive)
- Ravi Gupta: Boundary-testing behavior; assign to observer position
- Joshua Finch: Emotional check-in before class (required pre-lesson)

✅ ACCOMMODATIONS ACTIVE:
- Freya Nielsen: Blue-light filter on screen
- Zoe Martinez: Minimal audio setup

📍 TRANSITION NOTES:
- 30-minute period; Marcus thrives with structured breaks

RECOMMENDATION: Pre-assign peer buddy for Joshua
```

**Implementation**:
- Create new agent: `PeriodBriefingAgent`
- Integrate: staff presence + timetable + accommodations + quick_logs
- Trigger: 5 mins before each period

#### 3.2 CCA Engagement Agent
**Purpose**: Identify students missing CCA outlets or needing enrichment

**Output Example**:
```
🎯 CCA ENGAGEMENT ANALYSIS

🚨 HIGH PRIORITY:
- Noah Williams (3A): Not in any CCA; at-risk for disengagement
  → Recommend: Drama (builds confidence) or Coding Club (problem-solving)

⚠️ CONCERNING DROPS:
- Joshua Finch: Basketball (anxiety outlet) - 0 attendances in 2 weeks
  → Action: Check-in on barriers; reschedule if needed

✅ POSITIVE TRENDS:
- Marcus Thompson: Coding Club (high engagement)
  → Consider: Mentoring role to expand leadership

RECOMMENDATION: Enroll Noah in 1 CCA this week
```

**Implementation**:
- Create new agent: `CCAEngagementAgent`
- Integrate: enrollment data + attendance + behavior logs + intervention flags
- Trigger: Weekly summary

#### 3.3 Accommodation Compliance Agent
**Purpose**: Remind staff of accommodations before lessons

**Output Example**:
```
✅ LESSON SETUP CHECKLIST - 2:00 PM Foundation Learning (3A)

Environment:
☐ Freya Nielsen: Dim classroom lighting (light sensitivity)
☐ Zoe Martinez: Noise level monitor; ear defenders nearby
☐ Marcus Thompson: Movement breaks every 30 mins scheduled

Behavior Support:
☐ Sophie Chen: Reassurance buddy available (anxiety management)
☐ Noah Williams: Emotional temperature check at 2:15

Seating/Positioning:
☐ James Park: Visual schedule at transitions visible
☐ Liam O'Brien: 1:1 position for speech/language focus

QUICK NOTE: Three accommodation needs; allow 2 extra mins setup time
```

**Implementation**:
- Create new agent: `AccommodationComplianceAgent`
- Integrate: accommodations + staff + room/environment + lesson type
- Trigger: 10 mins before each period

---

## Data Import Plan

### Source: PDF Dataset (40 students, 4 classes)

**Staff Data** (from PDF class rosters):
```python
STAFF_DATA = [
    # 3A
    {"name": "Ms Elena Rodriguez", "role": "Class Teacher", "class_code": "3A"},
    {"name": "Mr David Chen", "role": "Learning Support Teacher", "class_code": "3A"},
    {"name": "Ms Linh Tran", "role": "TA", "class_code": "3A"},
    # ... (12 total staff)
]
```

**Timetable Data** (from PDF timetables, pages 6-7):
```python
TIMETABLE_DATA = [
    # 3A Monday
    {"class_code": "3A", "day": "Monday", "period": 1, "start": "09:00", "end": "09:45",
     "subject": "Literacy (Phonics)", "lesson_type": "Literacy"},
    {"class_code": "3A", "day": "Monday", "period": 2, "start": "09:45", "end": "10:15",
     "subject": "ICT", "lesson_type": "Specialist", "specialist_name": "Unknown"},
    # ... (120+ entries)
]
```

**CCA Data** (from PDF CCA assignments):
```python
CCA_DATA = [
    # 3A CCAs
    {"name": "Football", "day": "Monday", "time": "15:30-16:30", "class_code": "3A",
     "enrolled": ["Marcus T.", "James P.", "Oliver G."]},
    # ... (20+ CCAs)
]
```

**Accommodation Data** (from PDF profiles):
```python
ACCOMMODATIONS_DATA = [
    {"student_name": "Zoe Martinez", "type": "sensory",
     "description": "Noise sensitivity; ear defenders in assemblies"},
    {"student_name": "Freya Nielsen", "type": "sensory",
     "description": "Light sensitivity; blue-light filter on screens"},
    # ... (15+ accommodations)
]
```

### Import Scripts to Create
- [ ] `import_staff_data.py` - Populate Staff and StaffAssignment tables
- [ ] `import_timetable_data.py` - Populate Schedule and SpecialistLessonSchedule
- [ ] `import_cca_enrollments.py` - Link students to CCAs
- [ ] `import_accommodations_data.py` - Add student accommodations

---

## Success Criteria

### Phase 1 Complete When:
- ✅ All 4 data models created and tested
- ✅ 12 API endpoints working
- ✅ All PDF data imported (staff, timetables, CCAs, accommodations)
- ✅ Database validates 40 students + context data

### Phase 2 Complete When:
- ✅ 4 dashboard views rendering correctly
- ✅ Staff assignments visible in UI
- ✅ Timetable shows specialist lessons and transitions
- ✅ CCA enrollments displayed on student profiles
- ✅ No API errors in frontend

### Phase 3 Complete When:
- ✅ 3 agents implemented and tested
- ✅ Period briefings generated 5 mins before lessons
- ✅ CCA engagement analysis weekly
- ✅ Accommodation reminders 10 mins before lessons
- ✅ Manual test: Run 1 full day simulation with context

---

## Risk Assessment

| **Risk** | **Impact** | **Mitigation** |
|---------|-----------|----------------|
| Incomplete PDF data (missing staff names, times) | MEDIUM | Use "Unknown"/"TBD" placeholders; allow manual edits |
| Timetable complexity (specialist lessons, transitions) | MEDIUM | Test with 3A first, then expand |
| Staff unavailability data not in PDF | LOW | Default to all-day availability; update via UI |
| Performance (too many API calls) | LOW | Cache timetable data; batch API calls |

---

## Timeline

- **Week 1 (Oct 17-23)**: Implement Phase 1 (data infrastructure)
- **Week 2 (Oct 24-30)**: Implement Phase 2 (frontend views)
- **Week 3 (Oct 31-Nov 6)**: Implement Phase 3 (AI agents)
- **Week 4 (Nov 7-13)**: Testing, bug fixes, documentation

---

## Next Steps

1. Review this plan with team
2. Create database models (Phase 1.1-1.4)
3. Import data from PDF
4. Build Phase 1 API endpoints
5. Track progress in TODO list

**Estimated Total Effort**: 40-50 hours  
**Expected Behavior Prediction Improvement**: 40-50%

---

**Last Updated**: 2025-10-17 12:41 UTC  
**Status**: READY FOR IMPLEMENTATION
