# PTCC Fast Launcher

## Overview

**`start-ptcc-fast.sh`** is an optimized startup script that skips pip dependency installation if packages are already installed. This prevents the system from hanging during `pip install` and gets all services running faster.

## Why Use This?

- **No pip wait time** - Dependencies installed? Skip to starting services immediately
- **Sequential startup** - Services start one after another (not concurrent)
- **Better error reporting** - Clear feedback on what's running and what failed
- **Clean logging** - Each service logs to `.ptcc_logs/`
- **Safe cleanup** - Kills any existing processes before starting

## Quick Start

```bash
cd /Users/cantillonpatrick/Desktop/ptcc_standalone
./start-ptcc-fast.sh
```

## What It Does

1. **Cleanup** - Kills any existing Backend, PWA, Streamlit processes
2. **Backend API** (port 8001)
   - Starts FastAPI with uvicorn
   - Waits for health check to pass
3. **Mobile PWA** (port 5174)
   - Starts Vite dev server
   - Waits for server ready
4. **Streamlit Dashboard** (port 8501)
   - Starts teacher dashboard
   - Waits for dashboard ready

## When Services Are Ready

```
✓ ALL SERVICES STARTED SUCCESSFULLY

✓ Backend API       http://localhost:8001
✓ Mobile PWA        http://localhost:5174
✓ Dashboard         http://localhost:8501

🌐 Open browser: http://localhost:5174
   Click 🤖 Agents → Select student → See analysis
```

## Accessing the System

**Desktop (Recommended):**
- Open `http://localhost:5174` in browser
- Click "🤖 Agents" tab
- Select a student
- See AI analysis with 3 cards: At-Risk Identifier, Learning Path, Behavior Manager

**Streamlit Dashboard:**
- `http://localhost:8501` for teacher briefings and workflows

**Backend API:**
- `http://localhost:8001/docs` for Swagger UI
- `http://localhost:8001/api/health` for health check

## Logs

All logs go to `.ptcc_logs/`:
- `backend.log` - Backend API server logs
- `pwa.log` - Vite dev server logs
- `dashboard.log` - Streamlit dashboard logs

**View logs in real-time:**
```bash
tail -f .ptcc_logs/backend.log
tail -f .ptcc_logs/pwa.log
tail -f .ptcc_logs/dashboard.log
```

## Troubleshooting

### Service won't start
Check the corresponding log file for error details:
```bash
cat .ptcc_logs/backend.log | tail -50
```

### Ports already in use
Services use fixed ports (8001, 5174, 8501). If they're occupied, either:
1. Kill existing processes: `pkill -f python.*backend` (and similar)
2. Edit the script to use different ports (lines 14-16)

### Dependencies missing
If services fail to start due to missing packages:
```bash
# Backend dependencies
cd backend && pip install -r requirements.txt

# Mobile PWA dependencies
cd frontend/mobile-pwa && npm install

# Desktop dependencies
cd frontend/desktop-web && pip install -r requirements.txt
```

Then re-run `./start-ptcc-fast.sh`.

### Ctrl+C doesn't stop services
If services don't stop cleanly, manually kill them:
```bash
pkill -9 -f "python.*backend"
pkill -9 -f "npm run dev"
pkill -9 -f "streamlit"
```

## Performance Impact

- **Original script** - Waits for pip install (5-15 seconds) even if deps installed
- **Fast launcher** - Checks deps exist, starts immediately (< 1 second overhead)
- **Startup time** - Usually complete in 30-45 seconds vs 50-60 seconds

## When to Use Original vs Fast

**Use `start-ptcc.sh` if:**
- Dependencies are not installed
- You need to ensure all packages are up to date
- You're first-time setup

**Use `start-ptcc-fast.sh` if:**
- Dependencies already installed
- You're testing/developing iteratively
- You want faster startup cycles

## Environment Variables

Set before running:
```bash
export JWT_SECRET="your-secret-key"  # Defaults to dev key
./start-ptcc-fast.sh
```

## API Integration Points

Once running, the system is ready for:

### Quick Logging (Mobile)
- `POST /api/quick-log` - Record instant lesson events
- Fast mobile interface on 5174

### Agent Analysis (Desktop)
- `GET /api/agents/at-risk/{student_id}` - Risk assessment
- `GET /api/agents/learning-path/{student_id}` - Learning recommendations
- `GET /api/agents/behavior-manager/{student_id}` - Behavior analysis
- Optimized desktop UI on 5174

### Streamlit Dashboard
- Teacher briefings and AI workflows
- Full system management
- Running on 8501

## Next Steps

1. Run the fast launcher: `./start-ptcc-fast.sh`
2. Open `http://localhost:5174` in your browser
3. Navigate to Agents tab to see desktop-optimized AI analysis
4. Check agent cards for student insights
5. Use Streamlit (8501) for comprehensive teacher dashboard
