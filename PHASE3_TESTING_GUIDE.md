# 🧪 Phase 3 Testing Guide - Intelligent Agents

## System Now Running

```
✓ Backend API:   http://localhost:8001
✓ Mobile PWA:    http://localhost:5174
✓ Dashboard:     http://localhost:8501
```

---

## Quick Test Checklist

### 1. Backend API Health ✅
```bash
curl http://localhost:8001/api/agents/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "agents": ["period_briefing", "cca_engagement", "accommodation_compliance"],
  "agent_count": 3
}
```

**Status: PASS if you see all 3 agents**

---

### 2. Backend Agent List ✅
```bash
curl http://localhost:8001/api/agents/list
```

**Expected Response:**
```json
{
  "agents": [
    {
      "name": "period_briefing",
      "display_name": "Period Briefing Agent",
      "description": "Pre-lesson intelligence",
      "intervention_type": "briefing",
      "focus_areas": ["attendance", "behavior", "academic_readiness"]
    },
    {
      "name": "cca_engagement",
      "display_name": "CCA Engagement Agent",
      "description": "Enrichment recommendations",
      "intervention_type": "enrichment",
      "focus_areas": ["interests", "skills", "opportunities"]
    },
    {
      "name": "accommodation_compliance",
      "display_name": "Accommodation Compliance Agent",
      "description": "Compliance tracking",
      "intervention_type": "accommodation",
      "focus_areas": ["accommodations", "compliance", "tracking"]
    }
  ],
  "total_agents": 3
}
```

**Status: PASS if you see 3 agents with complete details**

---

### 3. Analyze a Student (Backend) ✅
```bash
# First, find a student ID (should be 1-40 based on our data)
curl -s http://localhost:8001/api/students | jq '.students[0:3]' # Get first 3 students
```

**Then analyze a student:**
```bash
curl -X POST http://localhost:8001/api/agents/analyze/1
```

**Expected Response:**
```json
{
  "student_id": 1,
  "student_name": "Student Name",
  "class_code": "CLASS",
  "timestamp": "2025-10-17T...",
  "summary": "Summary of findings across agents",
  "high_priority_count": 0,
  "agents": {
    "period_briefing": {
      "title": "Period Briefing",
      "priority": "medium",
      "action_required": true,
      "intervention_type": "briefing",
      "recommended_actions": ["..."],
      "reasoning": "..."
    },
    "cca_engagement": {...},
    "accommodation_compliance": {...}
  }
}
```

**Status: PASS if you see all 3 agent analyses**

---

## Mobile PWA Testing (Primary Phase 3 Feature)

### Access Mobile PWA
**URL:** http://localhost:5174

### Test 1: Student Selection
1. Open http://localhost:5174
2. Look at **left sidebar**
3. You should see a **student list**
4. **Search/Filter** students by name or class

**Expected:** 
- ✅ Student names visible
- ✅ Class codes shown
- ✅ Search/filter working

---

### Test 2: Student Selection Triggers Agent Analysis
1. **Click any student** in the sidebar
2. Wait 2-3 seconds
3. **Main panel should show 3 agent cards:**
   - 🔵 **Period Briefing Agent**
   - 🟢 **CCA Engagement Agent**  
   - 🟡 **Accommodation Compliance Agent**

**Expected:**
```
┌─────────────────────────────────────┐
│ Period Briefing Agent               │
│ Priority: HIGH                      │
│ Actions Required: 2                 │
│ [Show Details]                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ CCA Engagement Agent                │
│ Priority: MEDIUM                    │
│ Actions Required: 1                 │
│ [Show Details]                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Accommodation Compliance Agent      │
│ Priority: LOW                       │
│ Actions Required: 0                 │
│ [Show Details]                      │
└─────────────────────────────────────┘
```

---

### Test 3: Expand Agent Details
1. Click **"Show Details"** on any agent card
2. Card should expand to show:
   - Full recommendation text
   - Reasoning
   - Suggested actions
   - Priority color coding

**Expected:**
- ✅ Smooth expand animation
- ✅ Full text visible
- ✅ Multiple recommendations listed
- ✅ Click again to collapse

---

### Test 4: Switch Between Students
1. Select **Student A** → See their analysis
2. Select **Student B** → See different analysis
3. Back to **Student A** → Should show same analysis again

**Expected:**
- ✅ Analysis changes based on student
- ✅ Loading state visible during fetch
- ✅ No errors in browser console

---

### Test 5: Different Views (if available)
1. Look for **"Full View"** / **"Briefing View"** toggle
2. Switch between views
3. Briefing view should be more concise

**Expected:**
- ✅ Both views render correctly
- ✅ Briefing is shorter/simpler
- ✅ Full view shows all details

---

## Browser Console Testing

Open **DevTools** (F12) and check:

### Network Tab
1. Go to **Network** tab
2. Select a student
3. Look for requests to:
   - ✅ `POST /api/agents/analyze/1`
   - ✅ Response status: **200 OK**
   - ✅ Response time: **< 2 seconds**

### Console Tab
1. Go to **Console** tab
2. Select a student
3. Should see:
   - ✅ No red errors
   - ✅ No 404s or CORS issues
   - ✅ May see React warnings (acceptable)

---

## API Endpoint Testing

### Test Agents API Directly

**1. Health Check:**
```bash
curl http://localhost:8001/api/agents/health | jq .
```

**2. List Agents:**
```bash
curl http://localhost:8001/api/agents/list | jq .
```

**3. Analyze Student (with all agents):**
```bash
curl -X POST http://localhost:8001/api/agents/analyze/5 | jq .
```

**4. Analyze with Specific Agent:**
```bash
curl -X POST http://localhost:8001/api/agents/analyze/5/agent/period_briefing | jq .
```

**5. Get Display Format (CLI):**
```bash
curl http://localhost:8001/api/agents/analyze/5/display | jq .
```

---

## Streamlit Dashboard Testing

### Access Streamlit
**URL:** http://localhost:8501

### Expected Features
1. **Main Navigation** - Teacher interface
2. **Briefing Section** - Daily briefings
3. **Student Context** - Legacy student interface
4. **Quick Logging** - Log observations
5. Integration with agents backend

**Status Check:**
- ✅ Dashboard loads without errors
- ✅ No IndentationError (we fixed line 2648)
- ✅ Can navigate pages

---

## Complete Test Workflow

### Scenario: Test all 3 services working together

**Step 1: Verify Backend**
```bash
curl http://localhost:8001/api/agents/health
```
✅ Should return healthy status

**Step 2: Get Student List**
```bash
curl -s http://localhost:8001/api/students | jq '.students[] | {id, name, class_code}' | head -20
```
✅ Should list students

**Step 3: Test Mobile PWA**
1. Open http://localhost:5174
2. See student sidebar
3. Click any student
4. See 3 agent analysis cards

**Step 4: Test Streamlit**
1. Open http://localhost:8501
2. Navigate sections
3. Confirm no errors

**Step 5: Test API Docs**
1. Open http://localhost:8001/docs
2. Try "Try it out" on:
   - `/api/agents/health` GET
   - `/api/agents/list` GET
   - `/api/agents/analyze/{student_id}` POST

---

## Expected Student Data

Your database has **40 students**. Check them:

```bash
sqlite3 /Users/cantillonpatrick/Desktop/ptcc_standalone/data/school.db \
  "SELECT id, name, class_code FROM students LIMIT 10;"
```

### Sample Student IDs to Test
- ID: 1
- ID: 5  
- ID: 10
- ID: 20
- ID: 40

All should work in the agents API.

---

## Troubleshooting During Testing

### ❌ Mobile PWA not responding
```bash
# Check if running
lsof -i :5174

# Check logs
tail -50 .ptcc_logs/pwa.log
```

### ❌ Agent analysis missing
```bash
# Check backend logs
tail -100 .ptcc_logs/backend.log

# Test backend directly
curl -X POST http://localhost:8001/api/agents/analyze/1
```

### ❌ CORS errors in console
- Check browser console
- Error like "Access to XMLHttpRequest blocked by CORS"
- Verify backend has correct CORS origins in main.py

### ❌ Student list empty
```bash
# Check database
sqlite3 data/school.db "SELECT COUNT(*) FROM students;"
```

---

## Performance Benchmarks

**Expected Response Times:**

| Operation | Expected | Status |
|-----------|----------|--------|
| Agent health check | <100ms | ⏱️ |
| Agent list | <50ms | ⏱️ |
| Single student analysis | 500-800ms | ⏱️ |
| Mobile PWA page load | 2-3s | ⏱️ |
| Streamlit page load | 3-5s | ⏱️ |

**Test with:**
```bash
time curl -X POST http://localhost:8001/api/agents/analyze/1 > /dev/null
```

---

## Success Indicators

✅ **All Green When:**

1. **Backend API**
   - Health check returns healthy
   - Agent list shows 3 agents
   - Student analysis works for any ID

2. **Mobile PWA**
   - Loads on port 5174
   - Shows student list
   - Displays 3 agent cards per student
   - Details expand/collapse

3. **Streamlit**
   - Loads on port 8501
   - No syntax errors
   - All pages navigate

4. **Integration**
   - PWA fetches from backend
   - Streamlit connects to backend
   - No CORS errors
   - Network requests complete

---

## Test Report Template

```markdown
# Phase 3 Testing Report - [Date]

## Backend API
- [ ] Health check: PASS/FAIL
- [ ] Agent list: PASS/FAIL
- [ ] Student analysis: PASS/FAIL
- Response times: ___ms average

## Mobile PWA  
- [ ] Page loads: PASS/FAIL
- [ ] Student list visible: PASS/FAIL
- [ ] Agent cards show (3): PASS/FAIL
- [ ] Details expand: PASS/FAIL
- [ ] No console errors: PASS/FAIL

## Streamlit
- [ ] Page loads: PASS/FAIL
- [ ] No IndentationError: PASS/FAIL
- [ ] Navigation works: PASS/FAIL

## Integration
- [ ] PWA ↔ Backend: PASS/FAIL
- [ ] Network requests: PASS/FAIL
- [ ] CORS working: PASS/FAIL

## Overall Status
🟢 ALL PASS / 🟡 PARTIAL / 🔴 FAILURES

Issues Found:
1. ...
2. ...

Next Steps:
1. ...
```

---

## Next: Run Full Test Suite

Use these exact commands:

```bash
#!/bin/bash
echo "🧪 PHASE 3 SYSTEM TEST SUITE"
echo ""

echo "1. Backend Health:"
curl -s http://localhost:8001/api/agents/health | jq -r '.status'

echo "2. Agent Count:"
curl -s http://localhost:8001/api/agents/list | jq '.total_agents'

echo "3. Database Students:"
sqlite3 /Users/cantillonpatrick/Desktop/ptcc_standalone/data/school.db \
  "SELECT COUNT(*) as total FROM students;"

echo "4. Mobile PWA:"
curl -s http://localhost:5174 | head -1

echo "5. Streamlit:"
curl -s http://localhost:8501 | head -1

echo ""
echo "✅ Test suite complete!"
```

---

## Questions to Answer

After testing, answer:

1. ✅ Can you access all 3 services?
2. ✅ Do agent cards show for each student?
3. ✅ Are there any console errors?
4. ✅ Do the 3 agents have different analyses?
5. ✅ Are response times acceptable?

---

**Status:** Ready for comprehensive testing
**Phase:** 3 - Intelligent Agents
**Components:** Backend ✓ | Mobile PWA ✓ | Streamlit ✓
