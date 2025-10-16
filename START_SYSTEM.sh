#!/bin/bash
# PTCC Complete System Startup Script
# Run this to start all services fresh

echo "==============================================="
echo "🏫 PTCC - Personal Teaching Command Center"
echo "==============================================="
echo ""

# Kill any existing processes
echo "Step 1: Cleaning up any existing processes..."
pkill -9 -f "npm run dev" 2>/dev/null
pkill -9 -f "vite" 2>/dev/null
pkill -9 -f "run_backend.py" 2>/dev/null
sleep 2
echo "✅ Cleaned up old processes"
echo ""

# Verify ports are free
echo "Step 2: Verifying ports are available..."
if lsof -i :5173 :5174 :8005 2>/dev/null | grep LISTEN; then
    echo "⚠️ Warning: Some ports still in use"
else
    echo "✅ Ports 5173, 5174, 8005 are free"
fi
echo ""

# Start Backend
echo "Step 3: Starting Backend on port 8005..."
cd /Users/cantillonpatrick/Desktop/RAG_2/ptcc
python3 run_backend.py --port 8005 &
BACKEND_PID=$!
sleep 5
echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""

# Test Backend
echo "Step 4: Testing Backend..."
if curl -s http://localhost:8005/health | grep -q "healthy"; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID
    exit 1
fi
echo ""

# Start Frontend
echo "Step 5: Starting Frontend on port 5174..."
cd /Users/cantillonpatrick/Desktop/RAG_2/ptcc/frontend/mobile-pwa
npm run dev -- --port 5174 &
FRONTEND_PID=$!
sleep 8
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""

# Test Frontend
echo "Step 6: Testing Frontend..."
if curl -s http://localhost:5174/ | grep -q "<!DOCTYPE"; then
    echo "✅ Frontend is running"
else
    echo "⚠️ Frontend may be loading, trying network access..."
fi
echo ""

# Display URLs
echo "==============================================="
echo "🎉 SYSTEM READY!"
echo "==============================================="
echo ""
echo "📱 MOBILE ACCESS:"
echo "  URL: http://172.16.28.76:5174"
echo ""
echo "💻 DESKTOP ACCESS:"
echo "  URL: http://localhost:5174"
echo ""
echo "🔗 API BACKEND:"
echo "  URL: http://localhost:8005"
echo "  Health: http://localhost:8005/health"
echo ""
echo "==============================================="
echo "Press Ctrl+C to stop all services"
echo "==============================================="
echo ""

# Keep processes running
wait
