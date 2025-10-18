# Frontend-Backend Integration Guide

## Overview

This document explains the integration between the frontend applications and both the **legacy backend** and the **new safeguarding backend**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Applications                     │
│  - Project Guardian (React/Vite)                            │
│  - Mobile PWA (React/Vite)                                  │
│  - Dashboard (React/Vite)                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            Unified API Service Layer                        │
│  (frontend/shared/apiService.ts)                           │
│  - Compatibility layer for OLD and NEW APIs                │
│  - Automatic version detection                             │
│  - Data format conversion                                  │
└─────────────────────────────────────────────────────────────┘
                ┌───────────────┬────────────────┐
                ▼               ▼                ▼
        ┌──────────────┐ ┌─────────────┐ ┌────────────────┐
        │  OLD API     │ │  NEW API    │ │  Environment   │
        │  (Legacy)    │ │(Safeguarding)   │ Config        │
        │  - /api/*    │ │ /api/v1/*   │ │VITE_*          │
        └──────────────┘ └─────────────┘ └────────────────┘
```

---

## API Service Layer

### Location
`frontend/shared/apiService.ts`

### Features
- ✅ Unified interface for old and new APIs
- ✅ Automatic version detection
- ✅ Authentication token management
- ✅ Data format conversion
- ✅ Error handling
- ✅ Runtime API switching

### Usage

```typescript
// Import the service
import apiService from '@/services/apiService';

// Use old API (legacy)
const students = await apiService.fetchStudents();
const assessment = await apiService.getGuardianAssessment(
  description, yearGroup, incidentHistory
);

// Use new API (safeguarding)
const analysis = await apiService.analyzeStudentData({
  student_id: 'STU12345',
  behavioral_incidents: [...],
  assessments: [...],
  attendance: [...],
  communications: [...]
});

// Check compliance
const compliance = await apiService.checkCompliance();

// Check health
const health = await apiService.checkHealth();

// Utilities
await apiService.isNewAPIAvailable();
apiService.switchAPIVersion(true);
apiService.setAuthToken('token');
```

---

## Environment Configuration

### Frontend Environment Variables

```bash
# Old API (Legacy)
VITE_API_BASE_URL=http://localhost:8000

# New API (Safeguarding)
VITE_NEW_API_BASE_URL=http://localhost:8000/api/v1

# API Version Switch
VITE_USE_NEW_API=true  # Use new API (default: true)
VITE_USE_NEW_API=false # Use old API (fallback)
```

### Example `.env` Files

#### Development (New API)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_NEW_API_BASE_URL=http://localhost:8000/api/v1
VITE_USE_NEW_API=true
```

#### Development (Legacy API)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_NEW_API=false
```

#### Production
```bash
VITE_API_BASE_URL=https://api.example.com
VITE_NEW_API_BASE_URL=https://api.example.com/api/v1
VITE_USE_NEW_API=true
```

---

## Backend Endpoints

### Legacy API (Old)
```
GET  /api/students/           # List all students
GET  /api/search/?q=query     # Search students
POST /api/guardian/assess     # Guardian assessment
GET  /api/safeguarding/       # Legacy safeguarding
```

### New API (Safeguarding)
```
POST /api/v1/analyze          # Analyze student data
GET  /api/v1/compliance       # Check compliance status
GET  /api/v1/health           # Health check
GET  /api/v1/summary/:id      # Get summary
```

---

## Installation & Setup

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment
export DATABASE_URL="postgresql://user:pass@localhost/ptcc"
export JWT_SECRET="your-secret-key"

# Run migrations
python -m backend.main --migrate

# Start server
python -m backend.main

# Server running on http://localhost:8000
```

### 2. Frontend Setup

#### Project Guardian
```bash
cd frontend/project-guardian

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_NEW_API_BASE_URL=http://localhost:8000/api/v1
VITE_USE_NEW_API=true
EOF

# Start development server
npm run dev

# Access at http://localhost:5173
```

#### Mobile PWA
```bash
cd frontend/mobile-pwa

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_NEW_API_BASE_URL=http://localhost:8000/api/v1
VITE_USE_NEW_API=true
EOF

# Start development server
npm run dev

# Access at http://localhost:5173 or scan QR code for PWA
```

#### Dashboard
```bash
cd frontend/dashboard

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_NEW_API_BASE_URL=http://localhost:8000/api/v1
VITE_USE_NEW_API=true
EOF

# Start development server
npm run dev

# Access at http://localhost:5173
```

---

## API Version Migration

### Switching from Old to New API

#### Step 1: Update Environment
```bash
# In frontend .env
VITE_USE_NEW_API=true
```

#### Step 2: Update Component Imports
```typescript
// Before (old API)
import { getAssessment } from './api/guardian';

// After (new API)
import apiService from '@/services/apiService';
```

#### Step 3: Update API Calls
```typescript
// Before (old API)
const result = await getAssessment(description, yearGroup, history);

// After (new API)
const result = await apiService.analyzeStudentData({
  student_id: studentId,
  behavioral_incidents: [],
  assessments: [],
  attendance: [],
  communications: []
});

// Convert result if needed
const assessment = apiService.convertStudentDataToAssessment(result);
```

#### Step 4: Test
```bash
# Verify frontend and backend are communicating
npm run dev  # Start frontend
# Open browser console and check for API calls
```

---

## Data Format Conversion

### Converting Assessment to Student Data

```typescript
import apiService from '@/services/apiService';

// Convert old assessment format to new student data format
const studentData = apiService.convertAssessmentToStudentData(
  assessment,  // Old format
  studentId    // New format requirement
);

// Now use with new API
const result = await apiService.analyzeStudentData(studentData);
```

### Converting Analysis Result to Assessment

```typescript
// Convert new analysis result back to old assessment format
const assessment = apiService.convertStudentDataToAssessment(result);

// Now use with old code expecting assessment format
displayAssessment(assessment);
```

---

## Error Handling

### Common Errors & Solutions

#### Error: "New API is not enabled"
**Cause**: `VITE_USE_NEW_API=false` or not set
**Solution**: 
```bash
export VITE_USE_NEW_API=true
# Restart frontend dev server
```

#### Error: "Cannot connect to server"
**Cause**: Backend not running or wrong URL
**Solution**:
```bash
# Verify backend is running
curl http://localhost:8000/api/v1/health

# Check frontend environment
cat frontend/project-guardian/.env
```

#### Error: "HTTP 401 Unauthorized"
**Cause**: Missing or invalid authentication token
**Solution**:
```typescript
import apiService from '@/services/apiService';

// Set authentication token
apiService.setAuthToken('your-jwt-token');

// Or verify token is valid
const token = localStorage.getItem('auth_token');
console.log('Token:', token);
```

---

## Troubleshooting

### Frontend doesn't connect to backend

1. **Check backend is running**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. **Check environment variables**
   ```bash
   cat frontend/project-guardian/.env
   ```

3. **Check browser console for errors**
   - Open DevTools (F12)
   - Check Console tab for error messages
   - Check Network tab for API calls

4. **Verify API version**
   ```javascript
   // In browser console
   import apiService from '@/services/apiService';
   console.log(apiService.getAPIConfig());
   ```

### API returns 404 errors

1. **Verify correct API version is running**
   ```bash
   # Check new API endpoints
   curl http://localhost:8000/api/v1/health
   
   # Check old API endpoints
   curl http://localhost:8000/api/students/
   ```

2. **Check endpoint paths in frontend**
   - Verify `VITE_NEW_API_BASE_URL` is correct
   - Verify endpoint paths match backend

### CORS errors

1. **Frontend and backend on different ports**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000

2. **Solution**: Backend must have CORS enabled
   ```python
   # In backend/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

---

## Deployment

### Docker Deployment

```bash
# Build frontend
cd frontend/project-guardian
npm run build
docker build -t ptcc-frontend:latest .

# Run both
docker-compose up -d
```

### Environment Variables for Production

```bash
# Frontend .env.production
VITE_API_BASE_URL=https://api.example.com
VITE_NEW_API_BASE_URL=https://api.example.com/api/v1
VITE_USE_NEW_API=true

# Backend .env
DATABASE_URL=postgresql://prod-user:prod-pass@prod-db:5432/ptcc
JWT_SECRET=prod-secret-key
ENVIRONMENT=production
```

---

## Testing

### Manual Testing

```bash
# 1. Start backend
cd backend && python -m backend.main

# 2. Start frontend
cd frontend/project-guardian && npm run dev

# 3. Test in browser
# - Open http://localhost:5173
# - Try student search
# - Submit an analysis
# - Check browser console for API calls
```

### Automated Testing

```bash
# Frontend tests
cd frontend/project-guardian
npm run test

# Backend tests
cd backend
python -m pytest tests/ -v

# End-to-end tests
npm run test:e2e
```

---

## Support & Debugging

### Enable Debug Logging

```typescript
// In frontend component
import apiService from '@/services/apiService';

// Check API config
console.log('API Config:', apiService.getAPIConfig());

// Try health check
apiService.checkHealth()
  .then(result => console.log('Health:', result))
  .catch(err => console.error('Health check failed:', err));
```

### Check Backend Logs

```bash
# In another terminal while running backend
cd backend
tail -f logs/app.log

# Or enable debug logging
export LOG_LEVEL=DEBUG
python -m backend.main
```

---

## Summary

✅ **Frontend** - Multiple UI applications with unified API service
✅ **API Layer** - Compatibility layer for old and new backends
✅ **Environment Config** - Easy switching between API versions
✅ **Error Handling** - Robust error management and recovery
✅ **Documentation** - Complete setup and troubleshooting guide

The frontend-backend integration is fully functional and ready for both legacy and new safeguarding APIs.
