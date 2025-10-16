#!/bin/bash
# PTCC Daily Startup Script
# Main System: Backend API + Streamlit Desktop App
# Mobile PWA: Optional, triggered from Streamlit

# Display splash screen
clear
echo ""
echo "    ╔═══════════════════════════════════════════════════════════╗"
echo "    ║                                                           ║"
echo "    ║        🏫  PTCC - Personal Teaching Command Center  🏫   ║"
echo "    ║                                                           ║"
echo "    ║    ██████╗ ████████╗ ██████╗ ██████╗                   ║"
echo "    ║    ██╔══██╗╚══██╔══╝██╔════╝██╔════╝                   ║"
echo "    ║    ██████╔╝   ██║   ██║     ██║                        ║"
echo "    ║    ██╔═══╝    ██║   ██║     ██║                        ║"
echo "    ║    ██║        ██║   ╚██████╗╚██████╗                   ║"
echo "    ║    ╚═╝        ╚═╝    ╚═════╝ ╚═════╝                   ║"
echo "    ║                                                           ║"
echo "    ║        Local-First AI Learning Management System         ║"
echo "    ║                                                           ║"
echo "    ╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "    Initializing PTCC system..."
echo ""

# STEP 1: Kill any processes on critical ports (FIRST - most important)
echo "🔍 STEP 1: Clearing ports 8005, 8501, 5173..."
lsof -ti:8005,8501,5173,5174 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 2

# STEP 2: Kill any lingering processes by name
echo "🧹 STEP 2: Cleaning up any lingering processes..."
pkill -9 -f "streamlit" 2>/dev/null || true
pkill -9 -f "npm run dev" 2>/dev/null || true
pkill -9 -f "vite" 2>/dev/null || true
pkill -9 -f "run_backend.py" 2>/dev/null || true
pkill -9 -f "uvicorn" 2>/dev/null || true
sleep 2

# STEP 3: Verify ports are now free
echo "✅ All ports cleared and ready"
echo ""

# STEP 4: Start Backend API
echo ""
echo "🚀 STEP 4: Starting PTCC Backend API (port 8005)..."
cd /Users/cantillonpatrick/Desktop/RAG_2/ptcc

# Test import first
if ! /opt/homebrew/bin/python3.11 -c "from backend.main import app" 2>/dev/null; then
    echo "❌ Backend import failed - checking logs..."
    /opt/homebrew/bin/python3.11 -c "from backend.main import app" 2>&1 | tee /tmp/ptcc_backend_import.log
    exit 1
fi

# Start backend
/opt/homebrew/bin/python3.11 run_backend.py --port 8005 > /tmp/ptcc_backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to be ready  
echo "⏳ Waiting for backend to start (max 25 seconds)..."
for i in {1..25}; do
    # Check if process is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend process died!"
        echo "   Last 10 lines of log:"
        tail -10 /tmp/ptcc_backend.log
        exit 1
    fi
    
    # Check if service is responding
    if curl -s http://localhost:8005/health >/dev/null 2>&1; then
        echo "✅ Backend is healthy"
        break
    fi
    
    if [ $i -eq 25 ]; then
        echo "❌ Backend failed to start after 25 seconds"
        echo "   Check logs: tail -f /tmp/ptcc_backend.log"
        echo "   Process status:"
        ps aux | grep $BACKEND_PID | grep -v grep || echo "   Process not found"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""

# STEP 5: Start Streamlit Desktop App (Main Application)
echo ""
echo "📊 STEP 5: Starting Streamlit Desktop App (port 8501)..."
cd /Users/cantillonpatrick/Desktop/RAG_2/ptcc/frontend/desktop-web
streamlit run app.py --server.port=8501 --server.headless=true > /tmp/ptcc_streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo "   Streamlit PID: $STREAMLIT_PID"

# Wait for Streamlit to be ready
echo "⏳ Waiting for Streamlit to start (max 20 seconds)..."
for i in {1..20}; do
    if curl -s http://localhost:8501/ >/dev/null 2>&1; then
        echo "✅ Streamlit is running"
        echo "🌐 Opening browser..."
        # Launch browser automatically
        sleep 2
        open http://localhost:8501
        break
    fi
    if [ $i -eq 20 ]; then
        echo "⚠️  Streamlit taking longer than expected"
        echo "   Check logs: tail -f /tmp/ptcc_streamlit.log"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

echo ""
echo ""
echo "    ╔═══════════════════════════════════════════════════════════╗"
echo "    ║                                                           ║"
echo "    ║                   🎉 READY TO GO! 🎉                    ║"
echo "    ║                                                           ║"
echo "    ║           ✨ All systems operational ✨                  ║"
echo "    ║                                                           ║"
echo "    ╚═══════════════════════════════════════════════════════════╝"
echo ""
echo ""
echo "🖥️  MAIN APPLICATION (Open in browser):"
echo "   http://localhost:8501"
echo ""
echo "🔧 API BACKEND:"
echo "   http://localhost:8005"
echo "   Health: http://localhost:8005/health"
echo ""
echo "📱 MOBILE PWA:"
echo "   Available from Streamlit dashboard menu"
echo "   Can be launched on-demand from any page"
echo ""
echo "📊 LOGS:"
echo "   Backend:  tail -f /tmp/ptcc_backend.log"
echo "   Streamlit: tail -f /tmp/ptcc_streamlit.log"
echo ""
echo "⏹️  TO STOP: Press Ctrl+C or run:"
echo "   pkill -f streamlit; pkill -f run_backend.py"
echo ""
echo "System is running... Press Ctrl+C to stop"

# Keep script running and clean up on exit
trap 'echo ""; echo "🛑 Stopping PTCC services..."; kill $BACKEND_PID $STREAMLIT_PID 2>/dev/null; echo "✅ All services stopped"; exit 0' INT TERM

# Wait for processes
wait $BACKEND_PID $STREAMLIT_PID 2>/dev/null
