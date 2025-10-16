#!/bin/bash

# PTCC Setup Script
# Installs dependencies, sets up database, and runs tests

set -e  # Exit on error

echo "=================================="
echo "PTCC System Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python $python_version detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "pip upgraded"

# Install requirements
echo ""
echo "Installing requirements..."
echo "(This may take a few minutes...)"
pip install -r requirements.txt --quiet
print_success "Requirements installed"

# Check if .env file exists
echo ""
if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    echo "Creating .env from template..."
    cp .env.template .env
    print_warning "Please edit .env file with your API keys"
else
    print_success ".env file found"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p data
mkdir -p logs
mkdir -p storage
mkdir -p backend/migrations
print_success "Directories created"

# Initialize database
echo ""
echo "Would you like to initialize the database? (y/n)"
read -r response
if [[ "$response" == "y" ]]; then
    echo "Initializing database..."
    python backend/migrations/create_comprehensive_ptcc_schema.py
    if [ $? -eq 0 ]; then
        print_success "Database initialized"
    else
        print_error "Database initialization failed"
    fi
fi

# Run LLM integration tests
echo ""
echo "Would you like to test LLM integration? (y/n)"
read -r response
if [[ "$response" == "y" ]]; then
    echo "Running LLM integration tests..."
    python tests/test_llm_integration.py
    if [ $? -eq 0 ]; then
        print_success "LLM integration tests passed"
    else
        print_warning "LLM integration tests failed (check API key configuration)"
    fi
fi

# Summary
echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Ensure your .env file has the correct API keys"
echo "2. Run 'source venv/bin/activate' to activate the virtual environment"
echo "3. Run 'python tests/test_llm_integration.py' to test LLM integration"
echo "4. Start building your agents and prompts!"
echo ""
echo "To deactivate the virtual environment later, run: deactivate"
echo ""
