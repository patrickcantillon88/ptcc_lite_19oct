# PTCC Docker Setup

## Quick Start

### Option 1: Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop services
docker-compose down
```

### Option 2: Docker Commands
```bash
# Build the image
docker build -t ptcc-demo .

# Run the container
docker run -p 8501:8501 -p 5174:5174 -p 8001:8001 ptcc-demo

# Run in background
docker run -d -p 8501:8501 -p 5174:5174 -p 8001:8001 --name ptcc ptcc-demo

# Stop container
docker stop ptcc
```

## Access URLs
Once running, open your browser to:
- **Streamlit Dashboard**: http://localhost:8501
- **Mobile PWA**: http://localhost:5174
- **Backend API**: http://localhost:8001/docs

## What This Gives You

### For Development
- **Consistent Environment**: Same Python/Node versions everywhere
- **Clean Slate**: Fresh database with 160 sample students every time
- **No Dependency Issues**: Everything packaged inside container
- **Easy Reset**: `docker-compose down && docker-compose up --build`

### For Demos
- **Professional**: Send single file, runs identically everywhere
- **IT-Friendly**: Standard Docker deployment, no custom setup
- **Offline Ready**: All dependencies included, no internet required
- **Health Checks**: Built-in monitoring and restart capabilities

### For Distribution
- **Share the Image**: `docker save ptcc-demo | gzip > ptcc-demo.tar.gz`
- **Load Anywhere**: `docker load < ptcc-demo.tar.gz`
- **Version Control**: Tag images with versions
- **Multi-Platform**: Build for different architectures

## Container Details

### What's Inside
- **Python 3.11**: Backend and Streamlit
- **Node.js 18**: PWA build process
- **SQLite**: Database with 160 synthetic students
- **All Dependencies**: No external requirements
- **Startup Script**: Manages all three services

### Build Process
1. **Stage 1**: Build React PWA (production optimized)
2. **Stage 2**: Python environment with all services
3. **Data Loading**: 160 synthetic students pre-loaded
4. **Service Orchestration**: Backend → PWA → Streamlit startup sequence

### Health Monitoring
- **Health Check**: Pings backend API every 30 seconds
- **Service Dependencies**: PWA waits for backend, Streamlit waits for both
- **Graceful Shutdown**: Ctrl+C stops all services cleanly

## Development Workflow

### Build and Test Locally
```bash
# Build image
docker build -t ptcc-demo .

# Run and watch logs
docker run --rm -p 8501:8501 -p 5174:5174 -p 8001:8001 ptcc-demo

# Quick test
curl http://localhost:8001/api/health
```

### Debug Issues
```bash
# Get shell in running container
docker exec -it ptcc bash

# View logs
docker logs ptcc

# Check processes
docker exec ptcc ps aux
```

### Development with Volume Mounts
```bash
# Mount source code for live development
docker run -p 8501:8501 -p 5174:5174 -p 8001:8001 \
  -v $(pwd):/app \
  ptcc-demo
```

## Distribution Options

### Save/Load Image
```bash
# Save image to file
docker save ptcc-demo | gzip > ptcc-demo.tar.gz

# Load on another machine
gunzip -c ptcc-demo.tar.gz | docker load

# Run loaded image
docker run -p 8501:8501 -p 5174:5174 -p 8001:8001 ptcc-demo
```

### Docker Hub (Optional)
```bash
# Tag for Docker Hub
docker tag ptcc-demo your-username/ptcc-demo:latest

# Push to Docker Hub
docker push your-username/ptcc-demo:latest

# Others can run with
docker run -p 8501:8501 -p 5174:5174 -p 8001:8001 your-username/ptcc-demo
```

## Production Considerations

### Security
- Change `JWT_SECRET` environment variable
- Add authentication layer
- Use HTTPS reverse proxy
- Network segmentation

### Performance
- Use production WSGI server (gunicorn)
- Add Redis for session management
- Configure proper logging
- Monitor resource usage

### Deployment
```yaml
# Production docker-compose.yml
version: '3.8'
services:
  ptcc:
    image: ptcc-demo:latest
    ports:
      - "8501:8501"
      - "5174:5174"
      - "8001:8001"
    environment:
      - JWT_SECRET=${JWT_SECRET}
    restart: always
    volumes:
      - ptcc_data:/app/data
```

## Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find what's using the port
lsof -i :8501

# Use different ports
docker run -p 9501:8501 -p 6174:5174 -p 9001:8001 ptcc-demo
```

**Build Fails**
```bash
# Clean build (no cache)
docker build --no-cache -t ptcc-demo .

# Check build logs
docker build -t ptcc-demo . 2>&1 | tee build.log
```

**Services Won't Start**
```bash
# Check container logs
docker logs ptcc

# Get shell and debug
docker exec -it ptcc bash
```

**Memory Issues**
```bash
# Check Docker memory allocation
docker stats

# Increase Docker memory in Docker Desktop settings
```

## Comparison: Docker vs Native

| Feature | Native Setup | Docker |
|---------|-------------|---------|
| **First Run** | 10-15 minutes setup | 2-3 minutes build |
| **Consistency** | "Works on my machine" | Identical everywhere |
| **Dependencies** | Manual install | Automatic |
| **Distribution** | Complex | Single file |
| **IT Evaluation** | Setup required | Just works |
| **Development** | Full access | Containerized |

## Next Steps

### For Demos
1. Build image: `docker build -t ptcc-demo .`
2. Test locally: `docker run -p 8501:8501 -p 5174:5174 -p 8001:8001 ptcc-demo`
3. Save for sharing: `docker save ptcc-demo | gzip > ptcc-demo.tar.gz`
4. Send to stakeholders with simple run instructions

### For Production
1. Review security configuration
2. Set up proper environment variables
3. Configure reverse proxy (nginx)
4. Set up monitoring and backup
5. Plan multi-user authentication

The Docker setup gives you professional distribution and eliminates "it works on my machine" problems completely.