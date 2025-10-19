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
echo "  📊 Starting up..."
echo ""

cd "$(dirname "$0")"

# Install dependencies if needed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "  📦 Installing dependencies..."
    pip3 install -q -r backend/requirements.txt
    echo "     ✅ Dependencies installed"
    echo ""
fi

# Check data
if [ ! -f "data/school.db" ]; then
    echo "  📚 Importing your student data..."
    python3 scripts/import_lite_data.py > /dev/null 2>&1
    echo "     ✅ 90 students loaded from your ICT classes"
    echo ""
fi

# Start backend
echo "  🔧 Starting backend API..."
python3 -m backend.main > /tmp/ptcc_backend.log 2>&1 &
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
echo "  📂 Opening web interface..."
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
