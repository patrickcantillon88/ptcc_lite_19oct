#!/bin/bash

# PTCC Fast Launcher - Sequential startup (skips pip if deps exist)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Config
BACKEND_PORT=8001
PWA_PORT=5173
GUARDIAN_PORT=5174
CLASSROOM_PORT=5175
CCA_PORT=5176
BEHAVIOUR_PORT=5177
# New Classroom Management Tools
INTERVENTION_PORT=5178
PROGRESS_PORT=5179
SEATING_PORT=5180
GROUP_PORT=5181
DIFF_PORT=5182
# Assessment Analytics Apps
QUIZ_UPLOAD_PORT=5183
PERF_TRENDS_PORT=5184
PROGRESS_LEVELS_PORT=5185
AT_RISK_PORT=5186
ASSESSMENT_OVERVIEW_PORT=5187
DOCUMENTATION_PORT=5189
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
    
    echo -ne "${YELLOW}⏳${NC} Waiting for $service..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "\r${GREEN}✓${NC} $service is ready!                   "
            return 0
        fi
        attempt=$((attempt + 1))
        echo -ne "\r${YELLOW}⏳${NC} $service ($attempt/$max_attempts)..."
        sleep 1
    done
    
    echo -e "\r${RED}✗${NC} $service timeout after $max_attempts attempts"
    return 1
}

# Clear screen
clear

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     PTCC FAST LAUNCHER - Sequential Startup (No Pip Wait)     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Kill any existing processes
echo ""
print_status "info" "Cleaning up existing processes..."
pkill -9 -f "python.*backend" 2>/dev/null || true
pkill -9 -f "npm run dev" 2>/dev/null || true
pkill -9 -f "vite" 2>/dev/null || true
pkill -9 -f "node.*vite" 2>/dev/null || true
pkill -9 -f "streamlit" 2>/dev/null || true
# Kill processes on specific ports
lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$PWA_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$GUARDIAN_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$CLASSROOM_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$CCA_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$BEHAVIOUR_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$INTERVENTION_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$PROGRESS_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$SEATING_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$GROUP_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$DIFF_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$QUIZ_UPLOAD_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$PERF_TRENDS_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$PROGRESS_LEVELS_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$AT_RISK_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$ASSESSMENT_OVERVIEW_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$DOCUMENTATION_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$DASHBOARD_PORT | xargs kill -9 2>/dev/null || true
sleep 2
print_status "success" "Cleanup complete"

# ============================================================================
# STEP 1: Start Backend
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 1: Starting Backend API (port $BACKEND_PORT)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

print_status "info" "Starting backend..."
export JWT_SECRET="${JWT_SECRET:-dev-secret-key-change-in-production}"
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
cd "$SCRIPT_DIR/backend"
/opt/homebrew/bin/python3.11 -m uvicorn backend.main:app --host 0.0.0.0 --port $BACKEND_PORT > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
print_status "info" "Backend PID: $BACKEND_PID"

if ! wait_for_service "http://localhost:$BACKEND_PORT/api/health" "Backend API" 15; then
    print_status "error" "Backend failed to start. Check logs:"
    tail -20 "$LOG_DIR/backend.log"
    exit 1
fi

# ============================================================================
# STEP 2: Start Documentation App (Demo-Ready First!)
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 2: Starting Documentation App (port $DOCUMENTATION_PORT)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/documentation-app"
# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    print_status "info" "Installing documentation app dependencies..."
    npm install > "$LOG_DIR/documentation.log" 2>&1
fi
print_status "info" "Starting Vite dev server..."
nohup npm run dev >> "$LOG_DIR/documentation.log" 2>&1 &
DOCUMENTATION_PID=$!
print_status "info" "Documentation PID: $DOCUMENTATION_PID"

if ! wait_for_service "http://localhost:$DOCUMENTATION_PORT" "Documentation App" 15; then
    print_status "error" "Documentation App failed to start. Check logs:"
    tail -20 "$LOG_DIR/documentation.log"
    exit 1
fi

# Small delay to prevent resource conflicts
sleep 1

# Documentation app is ready (will open later with dashboard)

# ============================================================================
# STEP 3: Start Mobile PWA (Lesson Console)
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 3: Starting Mobile PWA (port $PWA_PORT)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/mobile-pwa"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/pwa.log" 2>&1 &
PWA_PID=$!
print_status "info" "PWA PID: $PWA_PID"

if ! wait_for_service "http://localhost:$PWA_PORT" "Mobile PWA" 15; then
    print_status "error" "Mobile PWA failed to start. Check logs:"
    tail -20 "$LOG_DIR/pwa.log"
    exit 1
fi

# Small delay to prevent resource conflicts
sleep 1

# ============================================================================
# STEP 4: Start Digital Citizenship App (Project Guardian)
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 4: Starting Digital Citizenship App (port $GUARDIAN_PORT)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/project-guardian"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/guardian.log" 2>&1 &
GUARDIAN_PID=$!
print_status "info" "Guardian PID: $GUARDIAN_PID"

if ! wait_for_service "http://localhost:$GUARDIAN_PORT" "Digital Citizenship App" 15; then
    print_status "error" "Digital Citizenship App failed to start. Check logs:"
    tail -20 "$LOG_DIR/guardian.log"
    exit 1
fi

# ============================================================================
# STEP 5: Start Classroom Tools App
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 5: Starting Classroom Tools App (port $CLASSROOM_PORT)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/classroom-tools"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/classroom.log" 2>&1 &
CLASSROOM_PID=$!
print_status "info" "Classroom PID: $CLASSROOM_PID"

if ! wait_for_service "http://localhost:$CLASSROOM_PORT" "Classroom Tools App" 15; then
    print_status "error" "Classroom Tools App failed to start. Check logs:"
    tail -20 "$LOG_DIR/classroom.log"
    exit 1
fi

# ============================================================================
# STEP 6: Start CCA Comments App
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 6: Starting CCA Comments App"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/cca-comments"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/cca.log" 2>&1 &
CCA_PID=$!
print_status "info" "CCA PID: $CCA_PID"

if ! wait_for_service "http://localhost:$CCA_PORT" "CCA Comments App" 15; then
    print_status "error" "CCA Comments App failed to start. Check logs:"
    tail -20 "$LOG_DIR/cca.log"
    exit 1
fi

# ============================================================================
# STEP 7: Start Behaviour Management App
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 7: Starting Behaviour Management App"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/behaviour-management"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/behaviour.log" 2>&1 &
BEHAVIOUR_PID=$!
print_status "info" "Behaviour PID: $BEHAVIOUR_PID"

if ! wait_for_service "http://localhost:$BEHAVIOUR_PORT" "Behaviour Management App" 15; then
    print_status "error" "Behaviour Management App failed to start. Check logs:"
    tail -20 "$LOG_DIR/behaviour.log"
    exit 1
fi

# ============================================================================
# STEP 8: Start Intervention Priority App
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 8: Starting Intervention Priority App"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/intervention-priority"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/intervention.log" 2>&1 &
INTERVENTION_PID=$!
print_status "info" "Intervention PID: $INTERVENTION_PID"

if ! wait_for_service "http://localhost:$INTERVENTION_PORT" "Intervention Priority App" 15; then
    print_status "error" "Intervention Priority App failed to start. Check logs:"
    tail -20 "$LOG_DIR/intervention.log"
    exit 1
fi

# ============================================================================
# STEP 9: Start Progress Dashboard App
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 9: Starting Progress Dashboard App"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/progress-dashboard"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/progress.log" 2>&1 &
PROGRESS_PID=$!
print_status "info" "Progress PID: $PROGRESS_PID"

if ! wait_for_service "http://localhost:$PROGRESS_PORT" "Progress Dashboard App" 15; then
    print_status "error" "Progress Dashboard App failed to start. Check logs:"
    tail -20 "$LOG_DIR/progress.log"
    exit 1
fi

# ============================================================================
# STEP 10: Start Seating Chart App
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 10: Starting Seating Chart App"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/seating-chart"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/seating.log" 2>&1 &
SEATING_PID=$!
print_status "info" "Seating PID: $SEATING_PID"

if ! wait_for_service "http://localhost:$SEATING_PORT" "Seating Chart App" 15; then
    print_status "error" "Seating Chart App failed to start. Check logs:"
    tail -20 "$LOG_DIR/seating.log"
    exit 1
fi

# ============================================================================
# STEP 11: Start Group Formation App
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 11: Starting Group Formation App"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/group-formation"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/group.log" 2>&1 &
GROUP_PID=$!
print_status "info" "Group PID: $GROUP_PID"

if ! wait_for_service "http://localhost:$GROUP_PORT" "Group Formation App" 15; then
    print_status "error" "Group Formation App failed to start. Check logs:"
    tail -20 "$LOG_DIR/group.log"
    exit 1
fi

# ============================================================================
# STEP 12: Start Differentiation App
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 12: Starting Differentiation App"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/differentiation"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/differentiation.log" 2>&1 &
DIFF_PID=$!
print_status "info" "Differentiation PID: $DIFF_PID"

if ! wait_for_service "http://localhost:$DIFF_PORT" "Differentiation App" 15; then
    print_status "error" "Differentiation App failed to start. Check logs:"
    tail -20 "$LOG_DIR/differentiation.log"
    exit 1
fi

# ============================================================================
# STEP 13: Start Quiz Upload App (Assessment Analytics)
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 13: Starting Quiz Upload App"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/quiz-upload"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/quiz-upload.log" 2>&1 &
QUIZ_UPLOAD_PID=$!
print_status "info" "Quiz Upload PID: $QUIZ_UPLOAD_PID"

if ! wait_for_service "http://localhost:$QUIZ_UPLOAD_PORT" "Quiz Upload App" 15; then
    print_status "error" "Quiz Upload App failed to start. Check logs:"
    tail -20 "$LOG_DIR/quiz-upload.log"
    exit 1
fi

# ============================================================================
# STEP 14: Start Performance Trends App (Assessment Analytics)
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 14: Starting Performance Trends App"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/performance-trends"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/perf-trends.log" 2>&1 &
PERF_TRENDS_PID=$!
print_status "info" "Performance Trends PID: $PERF_TRENDS_PID"

if ! wait_for_service "http://localhost:$PERF_TRENDS_PORT" "Performance Trends App" 15; then
    print_status "error" "Performance Trends App failed to start. Check logs:"
    tail -20 "$LOG_DIR/perf-trends.log"
    exit 1
fi

# ============================================================================
# STEP 15: Start Progress Levels App (Assessment Analytics)
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 15: Starting Progress Levels App"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/progress-levels"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/progress-levels.log" 2>&1 &
PROGRESS_LEVELS_PID=$!
print_status "info" "Progress Levels PID: $PROGRESS_LEVELS_PID"

if ! wait_for_service "http://localhost:$PROGRESS_LEVELS_PORT" "Progress Levels App" 15; then
    print_status "error" "Progress Levels App failed to start. Check logs:"
    tail -20 "$LOG_DIR/progress-levels.log"
    exit 1
fi

# ============================================================================
# STEP 16: Start At-Risk Students App (Assessment Analytics)
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 16: Starting At-Risk Students App"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/at-risk-students"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/at-risk.log" 2>&1 &
AT_RISK_PID=$!
disown
print_status "info" "At-Risk Students PID: $AT_RISK_PID"

if ! wait_for_service "http://localhost:$AT_RISK_PORT" "At-Risk Students App" 15; then
    print_status "error" "At-Risk Students App failed to start. Check logs:"
    tail -20 "$LOG_DIR/at-risk.log"
    exit 1
fi

# ============================================================================
# STEP 17: Start Assessment Analytics Overview App
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 17: Starting Assessment Analytics Overview"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/assessment-analytics-overview"
print_status "info" "Starting Vite dev server..."
nohup npm run dev > "$LOG_DIR/assessment-overview.log" 2>&1 &
ASSESSMENT_OVERVIEW_PID=$!
print_status "info" "Assessment Analytics Overview PID: $ASSESSMENT_OVERVIEW_PID"

if ! wait_for_service "http://localhost:$ASSESSMENT_OVERVIEW_PORT" "Assessment Analytics Overview App" 15; then
    print_status "error" "Assessment Analytics Overview failed to start. Check logs:"
    tail -20 "$LOG_DIR/assessment-overview.log"
    exit 1
fi

# ============================================================================
# STEP 18: Start Streamlit Dashboard
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}STEP 18: Starting Streamlit Dashboard (port $DASHBOARD_PORT)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$SCRIPT_DIR/frontend/desktop-web"
print_status "info" "Starting Streamlit..."
nohup streamlit run app.py --logger.level=warning --server.port=$DASHBOARD_PORT --server.headless true > "$LOG_DIR/dashboard.log" 2>&1 &
DASHBOARD_PID=$!
print_status "info" "Streamlit PID: $DASHBOARD_PID"

if ! wait_for_service "http://localhost:$DASHBOARD_PORT" "Streamlit Dashboard" 15; then
    print_status "error" "Streamlit failed to start. Check logs:"
    tail -20 "$LOG_DIR/dashboard.log"
    exit 1
fi

# Open Streamlit Dashboard in browser
print_status "info" "Opening main PTCC Dashboard in browser..."
open "http://localhost:$DASHBOARD_PORT"

# Wait a moment then open documentation in new tab
print_status "info" "Opening System Documentation..."
sleep 3
open "http://localhost:$DOCUMENTATION_PORT"

# ============================================================================
# SUCCESS MESSAGE
# ============================================================================
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ PTCC System Started Successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}📊 Dashboard:${NC}        http://localhost:$DASHBOARD_PORT"
echo -e "${CYAN}📋 Documentation:${NC}    http://localhost:$DOCUMENTATION_PORT"
echo -e "${CYAN}📱 Mobile PWA:${NC}       http://localhost:$PWA_PORT"
echo -e "${CYAN}🛑️ Digital Citizen:${NC}  http://localhost:$GUARDIAN_PORT"
echo -e "${CYAN}🛠️ Classroom Tools:${NC}   http://localhost:$CLASSROOM_PORT"
echo -e "${CYAN}📝 CCA Comments:${NC}     http://localhost:$CCA_PORT"
echo -e "${CYAN}📊 Behaviour Mgmt:${NC}   http://localhost:$BEHAVIOUR_PORT"
echo ""
echo -e "${BLUE}📚 Classroom Management Tools:${NC}"
echo -e "${CYAN}🚨 Intervention:${NC}     http://localhost:$INTERVENTION_PORT"
echo -e "${CYAN}📈 Progress:${NC}         http://localhost:$PROGRESS_PORT"
echo -e "${CYAN}🪑 Seating Chart:${NC}    http://localhost:$SEATING_PORT"
echo -e "${CYAN}👥 Group Formation:${NC}  http://localhost:$GROUP_PORT"
echo -e "${CYAN}🎯 Differentiation:${NC}  http://localhost:$DIFF_PORT"
echo ""
echo -e "${BLUE}📊 Assessment Analytics:${NC}"
echo -e "${CYAN}📤 Quiz Upload:${NC}      http://localhost:$QUIZ_UPLOAD_PORT"
echo -e "${CYAN}📈 Performance Trends:${NC} http://localhost:$PERF_TRENDS_PORT"
echo -e "${CYAN}📊 Progress Levels:${NC}  http://localhost:$PROGRESS_LEVELS_PORT"
echo -e "${CYAN}⚠️ At-Risk Students:${NC} http://localhost:$AT_RISK_PORT"
echo -e "${CYAN}📊 Analytics Overview:${NC} http://localhost:$ASSESSMENT_OVERVIEW_PORT"
echo ""
echo -e "${CYAN}🔧 API Docs:${NC}         http://localhost:$BACKEND_PORT/docs"
echo ""
echo -e "${BLUE}💡 All logs available in: $LOG_DIR${NC}"
echo -e "${BLUE}⏹️  To stop all services, run: ./stop-all.sh${NC}"
echo ""
echo -e "${CYAN}Press CTRL+C to stop all services${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping PTCC services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $PWA_PID 2>/dev/null || true
    kill $GUARDIAN_PID 2>/dev/null || true
    kill $CLASSROOM_PID 2>/dev/null || true
    kill $CCA_PID 2>/dev/null || true
    kill $BEHAVIOUR_PID 2>/dev/null || true
    kill $INTERVENTION_PID 2>/dev/null || true
    kill $PROGRESS_PID 2>/dev/null || true
    kill $SEATING_PID 2>/dev/null || true
    kill $GROUP_PID 2>/dev/null || true
    kill $DIFF_PID 2>/dev/null || true
    kill $QUIZ_UPLOAD_PID 2>/dev/null || true
    kill $PERF_TRENDS_PID 2>/dev/null || true
    kill $PROGRESS_LEVELS_PID 2>/dev/null || true
    kill $AT_RISK_PID 2>/dev/null || true
    kill $ASSESSMENT_OVERVIEW_PID 2>/dev/null || true
    kill $DOCUMENTATION_PID 2>/dev/null || true
    kill $DASHBOARD_PID 2>/dev/null || true
    sleep 2
    print_status "success" "All services stopped"
    exit 0
}

trap cleanup INT TERM

# Keep running
while true; do
    sleep 5
done
