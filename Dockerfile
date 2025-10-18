# PTCC Docker Container
# Multi-stage build for Python + Node.js application

# Stage 1: Node.js build for Mobile PWA
FROM node:18-alpine as node-builder

WORKDIR /app/frontend/mobile-pwa
COPY frontend/mobile-pwa/package*.json ./
RUN npm ci --only=production
COPY frontend/mobile-pwa/ ./
RUN npm run build

# Stage 2: Python environment with all services
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements.txt ./
COPY backend/requirements.txt ./backend/
COPY frontend/desktop-web/requirements.txt ./frontend/desktop-web/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt  
RUN pip install --no-cache-dir -r frontend/desktop-web/requirements.txt

# Copy application code
COPY . .

# Copy built PWA from node-builder stage
COPY --from=node-builder /app/frontend/mobile-pwa/dist ./frontend/mobile-pwa/dist

# Create data directory and load sample data
RUN mkdir -p data backend/data .ptcc_logs
RUN python -m backend.scripts.import_sample
RUN cp data/school.db backend/data/school.db

# Create startup script
RUN cat > start-docker.sh << 'EOF'
#!/bin/bash
set -e

echo "🐳 Starting PTCC in Docker..."
echo "Backend: http://localhost:8001"
echo "Mobile PWA: http://localhost:5174"  
echo "Streamlit: http://localhost:8501"
echo ""

# Start backend
echo "Starting backend..."
cd /app/backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend..."
until curl -s http://localhost:8001/api/health > /dev/null 2>&1; do
    sleep 1
done
echo "✅ Backend ready"

# Start Mobile PWA (serve built files)
echo "Starting Mobile PWA..."
cd /app/frontend/mobile-pwa
python -m http.server 5174 --directory dist &
PWA_PID=$!
echo "✅ Mobile PWA ready"

# Start Streamlit
echo "Starting Streamlit..."
cd /app/frontend/desktop-web
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --logger.level=warning &
STREAMLIT_PID=$!

# Wait for streamlit to be ready
echo "Waiting for Streamlit..."
until curl -s http://localhost:8501 > /dev/null 2>&1; do
    sleep 1
done
echo "✅ Streamlit ready"

echo ""
echo "🎉 PTCC is ready!"
echo "📊 Streamlit Dashboard: http://localhost:8501"
echo "📱 Mobile PWA: http://localhost:5174"
echo "🔧 API Documentation: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping PTCC services..."
    kill $BACKEND_PID $PWA_PID $STREAMLIT_PID 2>/dev/null || true
    exit 0
}

# Trap cleanup function on script exit
trap cleanup INT TERM

# Keep container running
wait $STREAMLIT_PID
EOF

# Make startup script executable
RUN chmod +x start-docker.sh

# Expose ports
EXPOSE 8001 8501 5174

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8001/api/health || exit 1

# Set environment variables
ENV PYTHONPATH=/app
ENV JWT_SECRET=dev-secret-key-change-in-production

# Default command
CMD ["./start-docker.sh"]