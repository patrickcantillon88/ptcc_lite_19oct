#!/bin/bash

# PTCC Demo Deployment Script
# Quick setup for stakeholder presentations

echo "🏫 PTCC Personal Teaching Command Center"
echo "======================================="

# Check for Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker found - Using containerized deployment"
    
    # Build and run Docker container
    echo "🔨 Building PTCC container..."
    docker build -t ptcc-demo . --quiet
    
    echo "🚀 Starting PTCC services..."
    docker run -d --name ptcc-demo \
        -p 8501:8501 \
        -p 5174:5174 \
        -p 8001:8001 \
        ptcc-demo
    
    # Wait for services
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Health check
    if curl -s http://localhost:8001/health > /dev/null; then
        echo "✅ Backend API: http://localhost:8001"
    fi
    
    if curl -s http://localhost:8501 > /dev/null; then
        echo "✅ Dashboard: http://localhost:8501"
    fi
    
    if curl -s http://localhost:5174 > /dev/null; then
        echo "✅ Mobile PWA: http://localhost:5174"
    fi
    
    echo ""
    echo "🎯 DEMO READY!"
    echo "Main Entry Point: http://localhost:8501"
    echo ""
    echo "To stop demo: docker stop ptcc-demo"
    
else
    echo "⚠️  Docker not found - Using native deployment"
    echo "This requires Python 3.11+ and Node.js 18+"
    
    # Run native startup script
    if [ -f "./start-ptcc-fast.sh" ]; then
        ./start-ptcc-fast.sh
    else
        echo "❌ Native startup script not found"
        echo "Please install Docker or run: ./start-ptcc-fast.sh manually"
    fi
fi

# Open browser (macOS/Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8501
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:8501
fi