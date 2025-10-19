#!/bin/bash

# PTCC Lite V1 - Splash Screen Startup

clear

cat << "EOF"

╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                    ███████╗ ██████╗ ██╗     ███████╗                      ║
║                    ██╔════╝██╔═══██╗██║     ██╔════╝                      ║
║                    ███████╗██║   ██║██║     █████╗                        ║
║                    ╚════██║██║   ██║██║     ██╔══╝                        ║
║                    ███████║╚██████╔╝███████╗███████╗                      ║
║                    ╚══════╝ ╚═════╝ ╚══════╝╚══════╝                      ║
║                                                                            ║
║                   🚀 PTCC LITE V1 - TEACHER'S COMMAND CENTER 🚀          ║
║                                                                            ║
║                         Your ICT Classes. Your Data. Your Time.          ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

EOF

sleep 1

echo ""
echo "  📊 Starting up... [1/6]"
echo ""

cd "$(dirname "$0")"

# Clean up old venv if corrupted
if [ -d "venv" ] && [ ! -f "venv/bin/python3" ]; then
    echo "  🧹 [2/6] Cleaning corrupted venv..."
    rm -rf venv
    echo "     ✅ Cleaned"
    echo ""
fi

# Setup virtual environment
if [ ! -d "venv" ]; then
    echo "  📦 [2/6] Creating virtual environment..."
    python3 -m venv venv
    echo "     ✅ Virtual environment created"
    echo ""
fi

# Paths
VENV_PYTHON="${PWD}/venv/bin/python3"
VENV_PIP="${PWD}/venv/bin/pip"

# Install dependencies
echo "  📚 [3/6] Installing dependencies..."
echo "     ⏳ FastAPI, Uvicorn, SQLAlchemy, Pandas..."
"$VENV_PIP" install -q -r backend/requirements.txt
echo "     ✅ All dependencies installed"
echo ""

# Check data
if [ ! -f "data/school.db" ]; then
    echo "  📥 [4/6] Importing your student data..."
    echo "     ⏳ Processing CAT4 scores, class rosters, quizzes..."
    "$VENV_PYTHON" scripts/import_lite_data.py > /dev/null 2>&1
    echo "     ✅ 90 students loaded from your ICT classes"
    echo ""
fi

# Start backend
echo "  🔧 [5/6] Starting backend API..."
echo "     ⏳ Launching FastAPI server on port 8001..."
"$VENV_PYTHON" -m backend.main > /tmp/ptcc_backend.log 2>&1 &
BACKEND_PID=$!
sleep 4

# Check if running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "     ❌ Backend failed to start"
    cat /tmp/ptcc_backend.log
    exit 1
fi

echo "     ✅ Backend running on http://localhost:8001"
echo ""

# Open UI
echo "  📂 [6/6] Opening web interface..."
echo "     ⏳ Launching browser..."
open "file://$(pwd)/frontend/ptcc-lite.html"
sleep 1
echo "     ✅ Web UI ready"
echo ""

echo ""
cat << "EOF"
╔════════════════════════════════════════════════════════════════════════════╗
║                         ✨ READY TO USE! ✨                              ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  📋 YOUR ICT CLASSES:                                                     ║
║     👥 Class Roster      - See all students, CAT4 scores, assessments    ║
║     📝 Incident Logger   - Log incidents in <10 seconds                  ║
║     📊 Weekly Patterns   - See incident trends automatically             ║
║     📋 Pre-Lesson Brief  - At-risk students before you teach             ║
║                                                                            ║
║  🔗 API:    http://localhost:8001/api/lite/                              ║
║  📚 Docs:   http://localhost:8001/docs                                    ║
║                                                                            ║
║  ⏹️  To stop: Press Ctrl+C                                                ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

EOF

echo ""
echo "  🎓 Tomorrow's workflow:"
echo "     1. Open this app"
echo "     2. Click 'Pre-Lesson Briefing' → Select your class"
echo "     3. See at-risk students before lesson starts"
echo "     4. During lesson: Log key moments (3-5 per class)"
echo "     5. After lesson: Check patterns and trends"
echo ""
echo "  💾 Your data is safe. All stored locally on this Mac."
echo ""
echo "  🚀 Let's go. Ready to get your time back? Use it."
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# Keep running
wait $BACKEND_PID
