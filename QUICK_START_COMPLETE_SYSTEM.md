# Quick Start - Complete System Setup ⚡

## 30-Second Overview

Your Privacy-Preserving Safeguarding System now has **three integrated interfaces**:

1. **Backend API** (localhost:8000) - Core safeguarding system
2. **Mobile PWA** (localhost:5174) - Tablet/mobile interface  
3. **Desktop Dashboard** (localhost:8501) - Streamlit desktop app with PWA launcher

All three are now **fully integrated** and talk to each other!

---

## Start Everything (3 Terminal Windows)

### Terminal 1: Backend API
```bash
cd backend
pip install -r requirements.txt
export JWT_SECRET="dev-secret-key"
python -m backend.main
```
✅ Backend ready on http://localhost:8000

### Terminal 2: Mobile PWA
```bash
cd frontend/mobile-pwa
npm install
npm run dev
```
✅ Mobile interface ready on http://localhost:5174

### Terminal 3: Desktop Dashboard
```bash
cd frontend/desktop-web
pip install -r requirements.txt
streamlit run app.py
```
✅ Dashboard ready on http://localhost:8501

---

## Verify Everything Works

### 1. Check Dashboard Loads
- Open browser: http://localhost:8501
- Sidebar shows "✅ Backend Connected" (green)
- If red ❌, backend isn't running

### 2. Test PWA Launch
- In dashboard sidebar, find "📱 Mobile Interface"
- Click "🚀 Launch" button
- Should open mobile PWA in new browser tab

### 3. Navigate Dashboard
- Daily Briefing: Check API data loads
- Settings: View API configuration
- Any page: Verify no API errors

---

## System Architecture

```
┌─────────────────────────────────────────┐
│     Desktop Dashboard (Streamlit)        │
│     http://localhost:8501               │
│  - Daily Briefing                       │
│  - Classroom Tools                      │
│  - AI Agents                            │
│  - 📱 PWA Launcher Button ◄────┐        │
└─────────────────────────────────┼───────┘
                 │                │
                 │ API Calls      │
                 ▼                │
┌─────────────────────────────────┼───────┐
│   Backend API (Python/FastAPI)   │       │
│   http://localhost:8000          │       │
│  - /health                       │       │
│  - /api/v1/*                     │       │
│  - Student data                  │       │
│  - Compliance checks             │       │
└─────────────────────────────────────────┘
         ▲
         │ API Calls
         │
┌────────┴──────────────────────────────┐
│   Mobile PWA (React)                   │
│   http://localhost:5174                │
│  - Responsive design                   │
│  - Tablet/mobile optimized             │
│  - Same backend integration            │
└────────────────────────────────────────┘
```

---

## Key Components

### Backend (http://localhost:8000)
- Safeguarding risk assessment
- Student data management
- Compliance tracking
- API endpoints at `/api/v1/*`
- Health check: `/health`

### Mobile PWA (http://localhost:5174)
- React-based interface
- Progressive Web App
- Tablet/mobile friendly
- Uses shared API service
- Connects to backend

### Desktop Dashboard (http://localhost:8501)
- Streamlit interface
- Teacher-focused tools
- AI agents integration
- PWA launcher button
- System status display

---

## Configuration

### Environment Variables

**Desktop Dashboard** (`frontend/desktop-web/`)
```bash
VITE_NEW_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_BASE_URL=http://localhost:8000
MOBILE_PWA_URL=http://localhost:5174
```

**Mobile PWA** (`frontend/mobile-pwa/`)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_NEW_API_BASE_URL=http://localhost:8000/api/v1
```

### Production URLs

Replace `localhost` with your domain:
```bash
VITE_NEW_API_BASE_URL=https://api.yourdomain.com/api/v1
VITE_API_BASE_URL=https://api.yourdomain.com
MOBILE_PWA_URL=https://mobile.yourdomain.com
```

---

## Usage Guide

### For Teachers (Desktop Dashboard)

1. Open http://localhost:8501
2. Check "Daily Briefing" for schedule & alerts
3. Use "Classroom Tools" for differentiation & seating
4. Launch mobile PWA if needed for mobile access

### For Mobile/Tablet (PWA)

1. Open http://localhost:5174 on mobile/tablet
2. Add to home screen for app-like experience
3. Same features as desktop, optimized for touch
4. Works offline with service workers

### For Administrators (Backend)

1. API base: http://localhost:8000
2. Safeguarding endpoints: `/api/v1/*`
3. Health check: `curl http://localhost:8000/health`
4. Database: SQLite (local) or configured backend

---

## Testing APIs

### Test New Safeguarding API
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get students
curl http://localhost:8000/api/v1/students

# Analyze student data
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1}'
```

### Test Legacy API
```bash
curl http://localhost:8000/health
```

### Test Dashboard Connection
```bash
# From dashboard terminal
# Check sidebar - should show ✅ Backend Connected
```

---

## Common Issues & Solutions

### Dashboard Shows ❌ Backend Disconnected

```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Check environment variables
echo $VITE_NEW_API_BASE_URL

# Restart dashboard
# Stop: Ctrl+C
# Start: streamlit run app.py
```

### PWA Launch Button Doesn't Work

```bash
# Check PWA is running
curl http://localhost:5174

# Verify environment variable
echo $MOBILE_PWA_URL

# Try manual URL in browser
# http://localhost:5174
```

### Data Not Loading on Pages

```bash
# Check API endpoints
curl http://localhost:8000/api/v1/students

# Check backend logs for errors
# Look for messages like "Database error" or "Query failed"

# Verify database exists
ls -la backend/data/
```

### Ports Already in Use

```bash
# Find process on port
lsof -i :8000  # Backend
lsof -i :5174  # PWA
lsof -i :8501  # Dashboard

# Kill process
kill -9 <PID>
```

---

## Stopping Services

### Stop All (Ctrl+C in each terminal)
```bash
# Terminal 1: Ctrl+C (Backend)
# Terminal 2: Ctrl+C (Mobile PWA)
# Terminal 3: Ctrl+C (Dashboard)
```

### Clean Shutdown
```bash
# If processes hang:
pkill -f "python -m backend.main"
pkill -f "vite"
pkill -f "streamlit"
```

---

## Next Steps

- [ ] Start all three services (3 terminals)
- [ ] Verify dashboard shows ✅ Backend Connected
- [ ] Test PWA launch button
- [ ] Navigate dashboard pages
- [ ] Open mobile PWA on tablet/mobile
- [ ] Check all interfaces work together

---

## Documentation Reference

- **Backend API**: See `FRONTEND_BACKEND_INTEGRATION.md`
- **Desktop Dashboard**: See `DESKTOP_DASHBOARD_UPDATE.md`
- **Mobile PWA**: See `frontend/mobile-pwa/README.md`
- **System Overview**: See `INTEGRATION_COMPLETE.md`

---

## Support

If something isn't working:

1. **Check Services**: Verify all 3 terminals are running
2. **Check URLs**: Verify correct ports (8000, 5174, 8501)
3. **Check Logs**: Look for error messages in each terminal
4. **Check Connectivity**: `curl` each service endpoint
5. **Check Configuration**: Review environment variables

---

**Ready?** Open 3 terminals and follow "Start Everything" section above! 🚀
