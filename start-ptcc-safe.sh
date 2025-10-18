#!/bin/bash

# PTCC Safe Launcher - Sequential startup with health checks
# Ensures each service is fully ready before starting the next

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Config
BACKEND_PORT=8001
PWA_PORT=5174
DASHBOARD_PORT=8501
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

LOG_DIR="$SCRIPT_DIR/.ptcc_logs"
mkdir -p "$LOG_DIR"

print_status() {
    local status=$1
    local message=$2
    case $status in
        "success") echo -e "${GREEN}✓${NC} $message" ;;
        "error") echo -e "${RED}✗${NC} $message" ;;
        "info") echo -e "${CYAN}ℹ${NC} $message" ;;
        "wait") echo -e "${YELLOW}⏳${NC} $message" ;;
    esac
}

wait_for_service() {
    local url=$1
    local service=$2
    local max_attempts=$3
    local attempt=0
    
    print_status "wait" "Waiting for $service to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            print_status "success" "$service is ready!"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -ne "\r${YELLOW}⏳${NC} $service ready in $attempt/$max_attempts attempts..."
        sleep 1
    done
    
    print_status "error" "$service failed to start after $max_attempts attempts"
    return 1
}

# Clear screen
clear

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     PTCC SAFE LAUNCHER - Sequential Startup                   ║"
echo "║     with Health Checks & Lazy Loading                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Kill any existing processes
echo ""
print_status "info" "Cleaning up existing processes..."
pkill -9 -f "python.*backend" 2>/dev/null || true
pkill -9 -f "npm run dev" 2>/dev/null || true
pkill -9 -f "vite" 2>/dev/null || true
pkill -9 -f "streamlit" 2>/dev/null || true
sleep 2
print_status "success" "Cleanup complete"

# ============================================================================
# STEP 1: Start Backend
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 1: Starting Backend API (port $BACKEND_PORT)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/backend"
print_status "info" "Installing Python dependencies..."
python3 -m pip install --break-system-packages -q -r requirements.txt 2>/dev/null || python3 -m pip install --break-system-packages -r requirements.txt > /dev/null

print_status "info" "Starting backend..."
export JWT_SECRET="${JWT_SECRET:-dev-secret-key-change-in-production}"
nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port $BACKEND_PORT > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
print_status "info" "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
if ! wait_for_service "http://localhost:$BACKEND_PORT/api/health" "Backend API" 30; then
    print_status "error" "Backend failed to start. Check logs:"
    tail -20 "$LOG_DIR/backend.log"
    exit 1
fi

# ============================================================================
# STEP 2: Start Mobile PWA
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 2: Starting Mobile PWA (port $PWA_PORT)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/mobile-pwa"
print_status "info" "Checking npm dependencies..."
[ ! -d "node_modules" ] && npm install --silent 2>/dev/null || true

print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/pwa.log" 2>&1 &
PWA_PID=$!
print_status "info" "PWA PID: $PWA_PID"

# Wait for frontend to be ready
if ! wait_for_service "http://localhost:$PWA_PORT" "Mobile PWA" 30; then
    print_status "error" "Mobile PWA failed to start. Check logs:"
    tail -20 "$LOG_DIR/pwa.log"
    exit 1
fi

# ============================================================================
# STEP 3: Start Streamlit Dashboard
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 3: Starting Streamlit Dashboard (port $DASHBOARD_PORT)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/desktop-web"
print_status "info" "Installing Streamlit dependencies..."
python3 -m pip install --break-system-packages -q -r requirements.txt 2>/dev/null || python3 -m pip install --break-system-packages -r requirements.txt > /dev/null

print_status "info" "Starting Streamlit..."
nohup streamlit run app.py --logger.level=warning --server.port=$DASHBOARD_PORT > "$LOG_DIR/dashboard.log" 2>&1 &
DASHBOARD_PID=$!
print_status "info" "Streamlit PID: $DASHBOARD_PID"

# Wait for Streamlit to be ready
if ! wait_for_service "http://localhost:$DASHBOARD_PORT" "Streamlit Dashboard" 30; then
    print_status "error" "Streamlit failed to start. Check logs:"
    tail -20 "$LOG_DIR/dashboard.log"
    exit 1
fi

# ============================================================================
# ALL SERVICES READY
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ ALL SERVICES STARTED SUCCESSFULLY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✓ Backend API${NC}       http://localhost:$BACKEND_PORT"
echo -e "${GREEN}✓ Mobile PWA${NC}        http://localhost:$PWA_PORT"
echo -e "${GREEN}✓ Dashboard${NC}         http://localhost:$DASHBOARD_PORT"
echo ""
echo -e "${YELLOW}🌐 Open your browser:${NC} http://localhost:$PWA_PORT"
echo -e "${YELLOW}   Click 🤖 Agents tab → Select a student → See analysis${NC}"
echo ""
echo -e "${CYAN}Press CTRL+C to stop all services${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping PTCC services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $PWA_PID 2>/dev/null || true
    kill $DASHBOARD_PID 2>/dev/null || true
    sleep 2
    print_status "success" "All services stopped"
    exit 0
}

trap cleanup INT TERM

# Keep running and monitor services
while true; do
    sleep 5
    
    # Check if backend crashed
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_status "error" "Backend crashed! Restarting..."
        cd "$SCRIPT_DIR/backend"
        nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port $BACKEND_PORT > "$LOG_DIR/backend.log" 2>&1 &
        BACKEND_PID=$!
    fi
done
