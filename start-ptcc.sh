#!/bin/bash

# PTCC (Privacy-Preserving Teaching Command Center) Launcher
# Starts backend, mobile PWA, and Streamlit dashboard with visual feedback
# Updated for new system structure with three integrated components

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Load environment variables from .env file
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(cat "$SCRIPT_DIR/.env" | grep -v '^#' | xargs)
fi

# Configuration
BACKEND_PORT=8001
PWA_PORT=5174
DASHBOARD_PORT=8501
BACKEND_DIR="$SCRIPT_DIR/backend"
PWA_DIR="$SCRIPT_DIR/frontend/project-guardian"
DASHBOARD_DIR="$SCRIPT_DIR/frontend/desktop-web"
LOG_DIR="$SCRIPT_DIR/.ptcc_logs"

mkdir -p "$LOG_DIR"

# Display splash screen
clear
echo -e "${PURPLE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║     ${CYAN}█████╗ ████████╗ ██████╗ ██████╗${PURPLE}                   ║"
echo "║     ${CYAN}██╔══██╗╚══██╔══╝██╔════╝██╔════╝${PURPLE}                   ║"
echo "║     ${CYAN}██████╔╝   ██║   ██║     ██║${PURPLE}                        ║"
echo "║     ${CYAN}██╔═══╝    ██║   ██║     ██║${PURPLE}                        ║"
echo "║     ${CYAN}██║        ██║   ╚██████╗╚██████╗${PURPLE}                   ║"
echo "║     ${CYAN}╚═╝        ╚═╝    ╚═════╝ ╚═════╝${PURPLE}                   ║"
echo "║                                                                ║"
echo "║   Personal Teaching Command Center                            ║"
echo "║   Privacy-Preserving Safeguarding System                      ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Initializing system...${NC}"
echo ""

# Function to print status
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success")
            echo -e "${GREEN}✓${NC} $message"
            ;;
        "error")
            echo -e "${RED}✗${NC} $message"
            ;;
        "info")
            echo -e "${CYAN}ℹ${NC} $message"
            ;;
        "warning")
            echo -e "${YELLOW}⚠${NC} $message"
            ;;
    esac
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local service=$2
    local port=$3
    local max_attempts=30
    local attempt=0
    
    echo -ne "${CYAN}  Waiting for $service...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "\r${GREEN}✓${NC} $service ready on port $port      "
            return 0
        fi
        attempt=$((attempt + 1))
        echo -ne "\r${CYAN}  Waiting for $service ($attempt/$max_attempts)...${NC}"
        sleep 1
    done
    
    echo -e "\r${YELLOW}⚠${NC} $service taking longer than expected"
    return 1
}

echo ""
print_status "info" "Checking system requirements..."

if [ ! -d "$BACKEND_DIR" ]; then
    print_status "error" "Backend directory not found: $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$PWA_DIR" ]; then
    print_status "error" "Digital Citizenship app directory not found: $PWA_DIR"
    exit 1
fi

if [ ! -d "$DASHBOARD_DIR" ]; then
    print_status "error" "Dashboard directory not found: $DASHBOARD_DIR"
    exit 1
fi

print_status "success" "All directories found"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}▶ Clearing ports...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Kill any processes on the ports
for port in $BACKEND_PORT $PWA_PORT $DASHBOARD_PORT; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        pid=$(lsof -Pi :$port -sTCP:LISTEN -t)
        print_status "warning" "Killing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null || true
    fi
done

# Kill any lingering processes
for pattern in "python.*backend" "npm run dev" "vite" "streamlit"; do
    pkill -9 -f "$pattern" 2>/dev/null || true
done

sleep 1
print_status "success" "Ports cleared"

echo ""
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}▶ Installing Backend Dependencies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    print_status "info" "Creating virtual environment with Python 3.11..."
    /opt/homebrew/bin/python3.11 -m venv venv
fi

# Activate venv and install requirements
print_status "info" "Installing Python requirements..."
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -q -r requirements.txt 2>/dev/null || pip install -r requirements.txt
    PYTHON_CMD="$(pwd)/venv/bin/python"
else
    # If no venv, use python3.11 directly
    /opt/homebrew/bin/python3.11 -m pip install -q -r requirements.txt 2>/dev/null || /opt/homebrew/bin/python3.11 -m pip install -r requirements.txt
    PYTHON_CMD="/opt/homebrew/bin/python3.11"
fi

print_status "success" "Backend dependencies ready"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}▶ Starting Backend API (port $BACKEND_PORT)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

export JWT_SECRET="${JWT_SECRET:-dev-secret-key-change-in-production}"
cd "$SCRIPT_DIR"
nohup $PYTHON_CMD -m uvicorn backend.main:app --host 0.0.0.0 --port $BACKEND_PORT > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
print_status "info" "Backend PID: $BACKEND_PID"

if ! wait_for_service "http://localhost:$BACKEND_PORT/health" "Backend API" "$BACKEND_PORT"; then
    print_status "error" "Backend failed to start"
    print_status "info" "Check logs: tail -f $LOG_DIR/backend.log"
    tail -30 "$LOG_DIR/backend.log"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}▶ Installing Digital Citizenship App Dependencies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$PWA_DIR"
print_status "info" "Installing npm dependencies..."
if [ ! -d "node_modules" ]; then
    npm install --silent 2>/dev/null || npm install
else
    print_status "success" "npm dependencies already installed"
fi
print_status "success" "Digital Citizenship app dependencies ready"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}▶ Starting Digital Citizenship App (port $PWA_PORT)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$PWA_DIR"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/pwa.log" 2>&1 &
PWA_PID=$!
print_status "info" "Mobile PWA PID: $PWA_PID"

if ! wait_for_service "http://localhost:$PWA_PORT" "Mobile PWA" "$PWA_PORT"; then
    print_status "warning" "Mobile PWA taking longer than expected"
    print_status "info" "Check logs: tail -f $LOG_DIR/pwa.log"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}▶ Installing Dashboard Dependencies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$DASHBOARD_DIR"
print_status "info" "Installing Streamlit and dependencies..."
/opt/homebrew/bin/python3.11 -m pip install -q -r requirements.txt 2>/dev/null || /opt/homebrew/bin/python3.11 -m pip install -r requirements.txt
print_status "success" "Dashboard dependencies ready"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}▶ Starting Streamlit Dashboard (port $DASHBOARD_PORT)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

export VITE_NEW_API_BASE_URL="http://localhost:$BACKEND_PORT/api"
export VITE_API_BASE_URL="http://localhost:$BACKEND_PORT"
export MOBILE_PWA_URL="http://localhost:$PWA_PORT"

cd "$DASHBOARD_DIR"
nohup /opt/homebrew/bin/python3.11 -m streamlit run app.py --logger.level=warning --server.port=$DASHBOARD_PORT > "$LOG_DIR/dashboard.log" 2>&1 &
DASHBOARD_PID=$!
print_status "info" "Streamlit Dashboard PID: $DASHBOARD_PID"

if ! wait_for_service "http://localhost:$DASHBOARD_PORT" "Streamlit Dashboard" "$DASHBOARD_PORT"; then
    print_status "warning" "Streamlit Dashboard taking longer than expected"
    print_status "info" "Check logs: tail -f $LOG_DIR/dashboard.log"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ ALL SERVICES STARTED SUCCESSFULLY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✓${NC} Backend API       http://localhost:$BACKEND_PORT"
echo -e "${GREEN}✓${NC} Mobile PWA        http://localhost:$PWA_PORT"
echo -e "${GREEN}✓${NC} Dashboard         http://localhost:$DASHBOARD_PORT"
echo ""
echo -e "${CYAN}CTRL+C to stop all services${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
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

# Keep the script running
while true; do
    sleep 1
    # Check if any process died
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_status "error" "Backend API stopped unexpectedly"
        cleanup
    fi
done

# Cleanup when Streamlit exits
kill $BACKEND_PID 2>/dev/null || true
