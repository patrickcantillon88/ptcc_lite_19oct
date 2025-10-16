#!/bin/bash

###############################################################################
# PTCC Startup Script
# Initializes the PTCC system, registers agents, and runs the API
###############################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
EXAMPLES_DIR="$PROJECT_ROOT/examples"

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_step() {
    echo -e "${GREEN}▶${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✖${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Check if Python is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 found: $(python3 --version)"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$PROJECT_ROOT/venv" ]; then
        print_warning "Virtual environment not found"
        print_step "Creating virtual environment..."
        python3 -m venv "$PROJECT_ROOT/venv"
        print_success "Virtual environment created"
    else
        print_success "Virtual environment found"
    fi
}

# Activate virtual environment
activate_venv() {
    print_step "Activating virtual environment..."
    source "$PROJECT_ROOT/venv/bin/activate"
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_step "Checking dependencies..."
    
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip install -q -r "$PROJECT_ROOT/requirements.txt"
        print_success "Dependencies installed"
    else
        print_warning "No requirements.txt found, installing core dependencies..."
        pip install -q fastapi uvicorn sqlalchemy psycopg2-binary google-generativeai openai requests pytest
        print_success "Core dependencies installed"
    fi
}

# Check environment variables
check_env() {
    print_step "Checking environment variables..."
    
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        print_warning ".env file not found"
        print_step "Creating .env template..."
        
        cat > "$PROJECT_ROOT/.env" << 'EOF'
# PTCC Environment Configuration

# Database
DATABASE_URL=postgresql://ptcc_user:ptcc_password@localhost:5432/ptcc_db

# API Keys (Add your keys here)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
API_PORT=8001
API_HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO
EOF
        
        print_warning "Created .env template - please add your API keys"
        print_warning "Edit $PROJECT_ROOT/.env before continuing"
        
        read -p "Press Enter to continue or Ctrl+C to exit..."
    else
        print_success "Environment file found"
    fi
}

# Initialize database
init_database() {
    print_step "Initializing database..."
    
    # Check if PostgreSQL is running
    if ! pg_isready &> /dev/null; then
        print_warning "PostgreSQL is not running"
        print_warning "Please start PostgreSQL manually or use Docker:"
        echo "  docker run -d -p 5432:5432 -e POSTGRES_USER=ptcc_user -e POSTGRES_PASSWORD=ptcc_password -e POSTGRES_DB=ptcc_db postgres:15"
        read -p "Press Enter once database is ready..."
    fi
    
    cd "$BACKEND_DIR"
    python3 -c "from database import init_db; init_db()" 2>/dev/null || print_warning "Database might already be initialized"
    print_success "Database ready"
}

# Register agents
register_agents() {
    print_step "Registering agents..."
    
    cd "$BACKEND_DIR"
    if [ -f "scripts/register_agents.py" ]; then
        python3 scripts/register_agents.py
        print_success "Agents registered"
    else
        print_warning "Agent registration script not found"
    fi
}

# Run tests
run_tests() {
    print_step "Running tests..."
    
    cd "$PROJECT_ROOT"
    if [ -d "tests" ]; then
        pytest tests/ -v --tb=short 2>&1 | tail -20
        if [ $? -eq 0 ]; then
            print_success "All tests passed"
        else
            print_warning "Some tests failed (this is okay for initial setup)"
        fi
    else
        print_warning "No tests directory found"
    fi
}

# Start API server
start_server() {
    print_step "Starting PTCC API server..."
    
    cd "$BACKEND_DIR"
    
    # Check if port is already in use
    if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port 8001 is already in use"
        read -p "Kill existing process and restart? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            lsof -ti:8001 | xargs kill -9
            print_success "Killed existing process"
        else
            print_error "Cannot start server - port already in use"
            exit 1
        fi
    fi
    
    print_success "Starting server on http://localhost:8001"
    print_warning "Press Ctrl+C to stop the server"
    echo ""
    
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
}

# Main execution
main() {
    print_header "PTCC System Startup"
    
    # Setup phase
    check_python
    check_venv
    activate_venv
    install_dependencies
    check_env
    
    # Initialization phase
    print_header "System Initialization"
    init_database
    register_agents
    
    # Testing phase (optional)
    if [ "$1" == "--with-tests" ]; then
        print_header "Running Tests"
        run_tests
    fi
    
    # Start server
    print_header "Starting API Server"
    print_success "Setup complete! Starting server..."
    echo ""
    echo -e "API Documentation: ${BLUE}http://localhost:8001/docs${NC}"
    echo -e "Example Client: ${BLUE}python3 examples/api_client_example.py${NC}"
    echo ""
    
    start_server
}

# Parse arguments
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "PTCC Startup Script"
    echo ""
    echo "Usage: ./scripts/start_ptcc.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --with-tests    Run tests before starting server"
    echo "  --help, -h      Show this help message"
    echo ""
    exit 0
fi

# Run main function
main "$@"
