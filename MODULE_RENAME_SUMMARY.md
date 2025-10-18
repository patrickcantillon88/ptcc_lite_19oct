# Module Renaming Summary

**Date:** October 17, 2025  
**Changes:** Updated module naming throughout codebase for consistency

## Renaming Changes

### 1. **Project Guardian → Digital Citizenship**

#### Backend Changes
- **Old File:** `backend/api/guardian.py`
- **New File:** `backend/api/digital_citizenship.py`
- **Changes Made:**
  - Renamed file
  - Updated logger name: `api.guardian` → `api.digital_citizenship`
  - Updated health check messages
  - Updated docstring

#### Main.py Changes
- **Old Import:** `from .api.guardian import router as guardian_router`
- **New Import:** `from .api.digital_citizenship import router as digital_citizenship_router`
- **Old Router Registration:** `app.include_router(guardian_router, prefix="/api/guardian", tags=["guardian"])`
- **New Router Registration:** `app.include_router(digital_citizenship_router, prefix="/api/digital-citizenship", tags=["digital-citizenship"])`

#### Frontend Changes (app.py)
- **Function Renamed:** `show_project_guardian()` → `show_digital_citizenship()`
- **Function Docstring:** "Project Guardian..." → "Digital Citizenship..."
- **Page Title:** "🛡️ Project Guardian" → "🛡️ Digital Citizenship"
- **API Endpoint:** `/api/guardian/assess` → `/api/digital-citizenship/assess`
- **Form ID:** `guardian_form` → `digital_citizenship_form`
- **Form Keys:** `guardian_*` → `dc_*`
- **React App Reference:** "Project Guardian React App" → "Digital Citizenship React App"
- **Navigation Menu:** "Project Guardian" → "Digital Citizenship"

---

### 2. **ICT Behavior → Behaviour Management**

#### Backend Changes
- **Old File:** `backend/api/ict_behavior.py`
- **New File:** `backend/api/behaviour_management.py`
- **Changes Made:**
  - Renamed file
  - Updated logger name: `api.ict_behavior` → `api.behaviour_management`
  - Updated docstring: "ICT Behavior Management" → "Behaviour Management"
  - Updated log categories: `ict_strike` → `behaviour_strike`, `ict_positive` → `behaviour_positive`

#### Main.py Changes
- **Old Import:** `from .api.ict_behavior import router as ict_behavior_router`
- **New Import:** `from .api.behaviour_management import router as behaviour_management_router`
- **Old Router Registration:** `app.include_router(ict_behavior_router, prefix="/api/behaviour-management", tags=["behaviour-management"])`
- **New Router Registration:** `app.include_router(behaviour_management_router, prefix="/api/behaviour-management", tags=["behaviour-management"])`

#### Frontend Changes (app.py)
- **Function Renamed:** `show_ict_behavior()` → `show_behaviour_management()`
- **Function Docstring:** "ICT Behavior Management..." → "Behaviour Management..."
- **Page Title:** "💻 ICT Behavior Management" → "💻 Behaviour Management"
- **API Endpoints:** 
  - `/api/ict-behavior/lesson/start` → `/api/behaviour-management/lesson/start`
  - `/api/ict-behavior/lesson/end` → `/api/behaviour-management/lesson/end`
- **Session State Variables:**
  - `ict_session_id` → `lesson_session_id`
  - `ict_class_code` → `lesson_class_code`
  - `ict_lesson_active` → `lesson_active`
- **Session Keys:** `ict_*` → `lesson_*`
- **Navigation Menu:** "ICT Behavior" → "Behaviour Management"

---

## API Endpoint Changes

### Before Renaming
| Module | Endpoint | Tags |
|--------|----------|------|
| guardian | `/api/guardian/...` | `guardian` |
| ict_behavior | `/api/behaviour-management/...` | `behaviour-management` |

### After Renaming
| Module | Endpoint | Tags |
|--------|----------|------|
| digital_citizenship | `/api/digital-citizenship/...` | `digital-citizenship` |
| behaviour_management | `/api/behaviour-management/...` | `behaviour-management` |

---

## Files Modified

### Backend
1. ✅ Created: `backend/api/digital_citizenship.py` (from guardian.py)
2. ✅ Created: `backend/api/behaviour_management.py` (from ict_behavior.py)
3. ✅ Modified: `backend/main.py` - Updated imports and router registrations

### Frontend
4. ✅ Modified: `frontend/desktop-web/app.py`
   - Updated 11 occurrences across the file
   - Function names, variables, API endpoints, UI labels

---

## Consistency Checks

### Navigation Menu (Updated ✅)
```python
[
    "Daily Briefing",
    "Students",
    "Classroom Tools",
    "CCA Comments",
    "Behaviour Management",     # was "ICT Behavior"
    "Quiz Analytics",
    "Digital Citizenship",      # was "Project Guardian"
    "Search",
    "Import",
    "AI Agents",
    "Settings"
]
```

### API Documentation
- Swagger/OpenAPI docs at `http://localhost:8001/docs` will now show:
  - `/api/digital-citizenship/...` endpoints
  - `/api/behaviour-management/...` endpoints

### Logging
- All debug logs now reference correct module names
- Easier tracking of requests to renamed endpoints

---

## Verification Steps

To verify all changes are working:

```bash
# 1. Start backend
cd /Users/cantillonpatrick/Desktop/ptcc_standalone
uvicorn backend.main:app --host 0.0.0.0 --port 8001

# 2. Check API documentation
# Visit: http://localhost:8001/docs
# Verify you see:
#   - /api/digital-citizenship/assess
#   - /api/behaviour-management/lesson/start
#   - /api/behaviour-management/lesson/end

# 3. Start frontend
cd frontend/desktop-web
streamlit run app.py

# 4. Check navigation menu
# Should show "Behaviour Management" and "Digital Citizenship"
# Not "ICT Behavior" or "Project Guardian"

# 5. Test endpoints
curl http://localhost:8001/api/digital-citizenship/health
curl http://localhost:8001/api/behaviour-management/lesson/current
```

---

## Status: ✅ COMPLETE

All references to old names have been updated:
- ✅ Backend module files renamed
- ✅ Backend imports and routes updated
- ✅ Frontend function names updated
- ✅ Frontend API endpoint calls updated
- ✅ Frontend UI labels updated
- ✅ Frontend session state variables updated
- ✅ Frontend navigation menu updated

**Next Steps:** Restart both backend and frontend services to apply changes.
