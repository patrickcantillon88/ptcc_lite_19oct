# PTCC System Administration Guide

## System Overview

The Personal Teaching Command Center (PTCC) is a production-ready, local-first AI-powered system for managing student data and providing intelligent teaching insights. This guide covers system administration, maintenance, and deployment procedures.

## 🏗️ System Architecture

### Core Components
- **Backend**: FastAPI-based REST API server
- **Database**: SQLite with SQLAlchemy ORM
- **AI Agents**: Three specialized teacher assistant agents
- **Frontend**: Streamlit desktop web interface + React PWA
- **Search**: ChromaDB vector database for semantic search
- **Ingestion**: Automated data import and processing

### Data Flow
1. **Import**: Raw data files → Processing pipeline → Database
2. **AI Processing**: Database queries → Agent analysis → Insights
3. **User Interface**: API calls → Frontend rendering → User interaction
4. **Search**: Document indexing → Vector embeddings → Query results

## 🚀 Deployment

### Prerequisites
- Python 3.8+
- Node.js 16+ (for mobile PWA)
- 4GB RAM minimum, 8GB recommended
- 10GB free disk space

### Production Installation

#### 1. Environment Setup
```bash
# Clone repository
git clone <ptcc-repository>
cd ptcc

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r backend/requirements.txt
```

#### 2. Database Initialization
```bash
# Initialize database schema
python scripts/init_db.py

# Import BIS HCMC dataset
python scripts/simplified_migration.py
```

#### 3. Configuration
Edit `config/config.yaml`:
```yaml
school:
  name: "BIS HCMC"
  campuses:
    - name: "Main Campus"
      code: "JC"

system:
  debug: false
  log_level: "INFO"
  auto_backup: true
```

#### 4. Start Services
```bash
# Start backend (production)
python run_backend.py

# Start desktop web interface
cd frontend/desktop-web
pip install -r requirements.txt
python run.py

# Start mobile PWA (development)
cd ../mobile-pwa
npm install
npm run dev
```

## ⚙️ Configuration Management

### Core Configuration Files
- `config/config.yaml`: Main system configuration
- `backend/requirements.txt`: Python dependencies
- `frontend/desktop-web/requirements.txt`: Desktop interface dependencies
- `frontend/mobile-pwa/package.json`: Mobile PWA dependencies

### Key Configuration Options

#### School Settings
```yaml
school:
  name: "BIS HCMC"
  campuses: [{name: "Main Campus", code: "JC"}]
  year_groups: ["7", "8", "9", "10", "11"]
  houses: ["Red", "Blue", "Green", "Yellow"]
```

#### System Settings
```yaml
system:
  debug: false
  log_level: "INFO"
  auto_backup: true
  backup_time: "23:59"
  max_search_results: 10
```

#### AI Agent Configuration
```yaml
briefing:
  include_ai_insights: true

search:
  include_student_data: true
```

## 🔧 Maintenance Procedures

### Daily Maintenance

#### 1. System Health Check
```bash
# Run integration tests
python test_system_integration.py

# Check backend health
curl http://localhost:8005/health

# Verify agent status
curl http://localhost:8005/api/agents/health
```

#### 2. Database Backup
```bash
# Manual backup
cp data/school.db data/backups/school_manual_$(date +%Y%m%d_%H%M%S).db

# Verify backup integrity
python -c "
import sqlite3
conn = sqlite3.connect('data/backups/school_manual_*.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM students')
print(f'Students in backup: {cursor.fetchone()[0]}')
conn.close()
"
```

#### 3. Log Rotation
```bash
# Check log size
ls -lh logs/ptcc.log

# Rotate if > 100MB
mv logs/ptcc.log logs/ptcc.log.$(date +%Y%m%d)
touch logs/ptcc.log
```

### Weekly Maintenance

#### 1. Search Index Optimization
```bash
# Rebuild search index
curl -X POST http://localhost:8005/api/search/index/rebuild

# Verify index status
curl http://localhost:8005/api/search/index/status
```

#### 2. Database Optimization
```bash
# Vacuum database (SQLite maintenance)
python -c "
import sqlite3
conn = sqlite3.connect('data/school.db')
conn.execute('VACUUM')
conn.close()
print('Database vacuumed')
"
```

#### 3. Update Dependencies
```bash
# Update Python packages
pip install --upgrade -r backend/requirements.txt

# Update Node.js packages
cd frontend/mobile-pwa && npm update
```

### Monthly Maintenance

#### 1. System Performance Review
- Review system logs for errors
- Check API response times
- Verify data integrity
- Assess storage usage

#### 2. Security Updates
```bash
# Update all packages
pip install --upgrade pip setuptools wheel
pip install --upgrade -r backend/requirements.txt

# Security audit
pip install safety
safety check
```

#### 3. Data Archiving
```bash
# Archive old logs
tar -czf logs/archive/logs_$(date +%Y%m).tar.gz logs/ptcc.log.*

# Clean old backups (keep last 10)
cd data/backups
ls -t *.db | tail -n +11 | xargs rm -f
```

## 📊 Monitoring

### System Metrics

#### API Performance
```bash
# Monitor response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8005/health

# Check API documentation access
curl http://localhost:8005/docs
```

#### Database Health
```bash
# Database size
du -h data/school.db

# Connection test
python -c "
from backend.core.database import get_db
db = next(get_db())
db.execute('SELECT 1')
db.close()
print('Database connection OK')
"
```

#### AI Agent Status
```bash
# Agent health check
curl http://localhost:8005/api/agents/health

# Individual agent testing
curl -X POST http://localhost:8005/api/agents/at-risk/analyze \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "analysis_type": "individual"}'
```

### Log Analysis
```bash
# Error count
grep -c "ERROR" logs/ptcc.log

# Recent errors
tail -20 logs/ptcc.log | grep ERROR

# API request patterns
grep "api/" logs/ptcc.log | head -10
```

## 🔧 Troubleshooting

### Common Issues

#### Backend Won't Start
**Symptoms**: Port binding errors, import failures
**Solutions**:
```bash
# Check port availability
lsof -i :8005

# Kill conflicting process
kill -9 <PID>

# Check Python imports
python -c "import backend.main"
```

#### Database Corruption
**Symptoms**: SQL errors, data inconsistencies
**Solutions**:
```bash
# Restore from backup
cp data/backups/school_backup_recent.db data/school.db

# Rebuild database
python scripts/init_db.py
python scripts/simplified_migration.py
```

#### Search Index Issues
**Symptoms**: Search returns no results
**Solutions**:
```bash
# Rebuild index
curl -X POST http://localhost:8005/api/search/index/rebuild

# Check index status
curl http://localhost:8005/api/search/index/status
```

#### AI Agent Failures
**Symptoms**: Agent endpoints return errors
**Solutions**:
```bash
# Check agent health
curl http://localhost:8005/api/agents/health

# Restart backend service
pkill -f "python run_backend.py"
python run_backend.py
```

### Performance Issues

#### Slow API Responses
```bash
# Check database query performance
python -c "
import time
from backend.core.database import get_db

start = time.time()
db = next(get_db())
result = db.execute('SELECT COUNT(*) FROM students')
end = time.time()
print(f'Query time: {end-start:.3f}s')
db.close()
"
```

#### High Memory Usage
```bash
# Monitor memory usage
ps aux | grep python | grep ptcc

# Restart services if needed
systemctl restart ptcc-backend
```

## 🔄 Backup and Recovery

### Automated Backups
```yaml
# In config.yaml
system:
  auto_backup: true
  backup_time: "23:59"
```

### Manual Backup Procedure
```bash
#!/bin/bash
# backup.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="data/backups"

# Database backup
cp data/school.db "$BACKUP_DIR/school_backup_$TIMESTAMP.db"

# Configuration backup
cp config/config.yaml "$BACKUP_DIR/config_$TIMESTAMP.yaml"

# Verify backup
if [ -f "$BACKUP_DIR/school_backup_$TIMESTAMP.db" ]; then
    echo "Backup completed: $TIMESTAMP"
else
    echo "Backup failed!"
    exit 1
fi
```

### Recovery Procedure
```bash
#!/bin/bash
# restore.sh
BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Stop services
pkill -f "python run_backend.py"

# Restore database
cp "$BACKUP_FILE" data/school.db

# Restart services
python run_backend.py &

echo "Recovery completed from $BACKUP_FILE"
```

## 🚀 Scaling and Optimization

### Performance Tuning

#### Database Optimization
```sql
-- Create indexes for common queries
CREATE INDEX idx_students_class_year ON students(class_code, year_group);
CREATE INDEX idx_logs_student_date ON quick_logs(student_id, timestamp);
CREATE INDEX idx_assessments_student ON assessments(student_id);
```

#### API Optimization
```python
# Enable response compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Implement caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
FastAPICache.init(RedisBackend(redis_client), prefix="ptcc-cache")
```

### High Availability Setup
```bash
# Load balancer configuration (nginx example)
upstream ptcc_backend {
    server localhost:8005;
    server localhost:8006 backup;
}

server {
    listen 80;
    location / {
        proxy_pass http://ptcc_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔒 Security

### Access Control
```yaml
# In config.yaml
security:
  password_required: true
  database_encryption: true
  session_timeout: 3600
```

### Network Security
- Run behind reverse proxy (nginx/caddy)
- Use HTTPS in production
- Implement rate limiting
- Regular security updates

### Data Protection
- Encrypt sensitive student data
- Implement data retention policies
- Regular security audits
- GDPR compliance measures

## 📈 Monitoring and Alerting

### System Monitoring
```bash
# Install monitoring tools
pip install psutil prometheus-client

# Basic health check endpoint
@app.get("/metrics")
def metrics():
    return generate_latest()
```

### Alert Configuration
```yaml
alerts:
  disk_space_threshold: 90  # percent
  memory_threshold: 85      # percent
  error_rate_threshold: 5   # errors per minute
  response_time_threshold: 2  # seconds
```

## 📚 Training and Documentation

### User Training Materials
- `USER_GUIDE.md`: Comprehensive user guide
- `README.md`: System overview and setup
- Video tutorials (planned)
- Interactive walkthroughs

### Administrator Resources
- This administration guide
- API documentation (`/docs`)
- System architecture diagrams
- Troubleshooting runbooks

## 🎯 Best Practices

### Operational Excellence
1. **Regular Backups**: Daily automated backups
2. **Monitoring**: Continuous system monitoring
3. **Updates**: Regular dependency updates
4. **Testing**: Pre-deployment testing procedures

### Security First
1. **Principle of Least Privilege**: Minimal required permissions
2. **Regular Audits**: Security and access reviews
3. **Data Encryption**: Encrypt sensitive data at rest
4. **Network Security**: Secure communication channels

### Performance Optimization
1. **Resource Monitoring**: Track system resource usage
2. **Query Optimization**: Optimize database queries
3. **Caching**: Implement appropriate caching layers
4. **Load Testing**: Regular performance testing

---

**Version**: PTCC 1.0.0 Production
**Last Updated**: October 2025
**System Status**: Production Ready ✅