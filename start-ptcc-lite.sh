#!/bin/bash
# PTCC Lite Launcher

echo "🚀 Starting PTCC Lite V1..."
cd "$(dirname "$0")"

if [ ! -f "data/school.db" ]; then
    echo "📚 Importing data..."
    python3 scripts/import_lite_data.py
fi

echo "🔧 Starting backend..."
python3 -m backend.main &
BACKEND_PID=$!
sleep 3

echo "✅ Backend running (PID: $BACKEND_PID)"
echo "📂 Opening web UI..."
open "file://$(pwd)/frontend/ptcc-lite.html"

echo ""
echo "✨ PTCC Lite ready!"
echo "🔗 API: http://localhost:8001/api/lite/"
echo "Press Ctrl+C to stop"
echo ""

wait $BACKEND_PID
