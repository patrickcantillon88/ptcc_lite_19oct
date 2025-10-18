# System Documentation

## API Documentation

### Overview
The Privacy-Preserving Safeguarding System provides REST APIs for student safety analysis and risk assessment.

### Base URL
```
https://api.ptcc-safeguarding.example.com/api/v1
```

### Authentication
All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

### Endpoints

#### POST /analyze
Analyze student data for safeguarding concerns.

```json
Request:
{
  "student_id": "STU12345",
  "data": {
    "behavioral_incidents": [...],
    "assessments": [...],
    "attendance": [...],
    "communications": [...]
  }
}

Response:
{
  "status": "success",
  "data": {
    "student_token": "TOKEN_STU_ABC",
    "risk_level": "HIGH",
    "patterns": [...],
    "recommendations": [...]
  }
}
```

#### GET /compliance
Check system compliance status.

```json
Response:
{
  "status": "compliant",
  "checks": {
    "ferpa": "passed",
    "gdpr": "passed",
    "encryption": "passed"
  }
}
```

#### GET /health
Health check endpoint.

```json
Response:
{
  "status": "healthy",
  "services": {
    "database": "ok",
    "llm_client": "ok"
  }
}
```

## Database Schema

### students table
```sql
CREATE TABLE students (
  id UUID PRIMARY KEY,
  student_token VARCHAR(50) UNIQUE,
  school_id UUID,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### incidents table
```sql
CREATE TABLE incidents (
  id UUID PRIMARY KEY,
  student_id UUID REFERENCES students(id),
  incident_type VARCHAR(50),
  severity VARCHAR(20),
  timestamp TIMESTAMP
);
```

### assessments table
```sql
CREATE TABLE assessments (
  id UUID PRIMARY KEY,
  student_id UUID REFERENCES students(id),
  subject VARCHAR(100),
  performance_level VARCHAR(20),
  timestamp TIMESTAMP
);
```

## Deployment Guide

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Redis 6.0+
- Docker (optional)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd ptcc_standalone

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/ptcc"
export REDIS_URL="redis://localhost:6379"
export JWT_SECRET="<your-secret-key>"

# Run migrations
python -m backend.main --migrate

# Start server
python -m backend.main
```

### Docker Deployment

```bash
docker build -t ptcc-safeguarding .
docker run -p 8000:8000 --env-file .env ptcc-safeguarding
```

## Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET`: JWT signing key
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING)
- `CORS_ORIGINS`: Allowed CORS origins

## Troubleshooting

### Database Connection Issues
- Check PostgreSQL is running
- Verify DATABASE_URL format
- Check credentials

### LLM Service Issues
- Verify LLM API key
- Check network connectivity
- Review rate limits

### Performance Issues
- Check database indexes
- Monitor memory usage
- Review slow queries in logs

## Security Checklist

- [ ] Enable HTTPS/TLS
- [ ] Set strong JWT secret
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Regular backups configured
- [ ] Update dependencies regularly
- [ ] Review access logs
- [ ] Monitor for security alerts
