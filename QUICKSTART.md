# PTCC Quick Start Guide

Complete setup and usage guide for the PTCC Agent Orchestration System.

## Prerequisites

- Python 3.9+
- PostgreSQL 13+ (or Docker)
- API keys for LLM providers (Gemini/OpenAI)

## Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Make startup script executable (if not already)
chmod +x scripts/start_ptcc.sh

# Run complete setup and start server
./scripts/start_ptcc.sh

# Or with tests
./scripts/start_ptcc.sh --with-tests
```

The script will:
- Check Python installation
- Create/activate virtual environment
- Install dependencies
- Configure environment variables
- Initialize database
- Register agents
- Start API server on http://localhost:8001

### Option 2: Manual Setup

#### 1. Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Environment

Create `.env` file in project root:

```env
# Database
DATABASE_URL=postgresql://ptcc_user:ptcc_password@localhost:5432/ptcc_db

# API Keys
GEMINI_API_KEY=your_actual_gemini_api_key
OPENAI_API_KEY=your_actual_openai_api_key

# Server
API_PORT=8001
API_HOST=0.0.0.0
```

#### 3. Start PostgreSQL

Using Docker (recommended):
```bash
docker run -d \
  -p 5432:5432 \
  -e POSTGRES_USER=ptcc_user \
  -e POSTGRES_PASSWORD=ptcc_password \
  -e POSTGRES_DB=ptcc_db \
  --name ptcc-postgres \
  postgres:15
```

Or use local PostgreSQL installation.

#### 4. Initialize Database

```bash
cd backend
python3 -c "from database import init_db; init_db()"
```

#### 5. Register Agents

```bash
cd backend
python3 scripts/register_agents.py
```

#### 6. Start Server

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Verify Installation

### 1. Check API Health

```bash
curl http://localhost:8001/health
```

Expected output:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. View API Documentation

Open browser to: http://localhost:8001/docs

### 3. List Registered Agents

```bash
curl http://localhost:8001/api/orchestration/agents
```

## Using the API

### Python Client

```python
from examples.api_client_example import PTCCClient

# Create client
client = PTCCClient()

# Create lesson plan
lesson = client.create_lesson_plan(
    grade="5th",
    subject="Science",
    topic="Solar System",
    user_id="teacher123"
)

print(lesson['lesson_plan'])
```

Run the full example:
```bash
python3 examples/api_client_example.py
```

### cURL Examples

#### Create Lesson Plan
```bash
curl -X POST "http://localhost:8001/api/orchestration/quick/lesson-plan" \
  -H "Content-Type: application/json" \
  -d '{
    "grade": "5th",
    "subject": "Science",
    "topic": "Solar System",
    "duration": "45 minutes",
    "user_id": "teacher123"
  }'
```

#### Generate Assessment
```bash
curl -X POST "http://localhost:8001/api/orchestration/quick/assessment" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Solar System",
    "grade": "5th",
    "question_count": 5,
    "user_id": "teacher123"
  }'
```

#### Compose Feedback
```bash
curl -X POST "http://localhost:8001/api/orchestration/quick/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "student_name": "Alex",
    "assignment": "Solar System Project",
    "score": 88,
    "strengths": ["Creative presentation", "Good research"],
    "improvements": ["Add more details", "Include diagrams"],
    "user_id": "teacher123"
  }'
```

#### Get Task History
```bash
curl "http://localhost:8001/api/orchestration/tasks/history?limit=10"
```

#### Get System Statistics
```bash
curl "http://localhost:8001/api/orchestration/stats/overview"
```

## System Components

### Core Systems

1. **Memory System** - Personalized context and interaction history
2. **Alignment System** - Ethical AI and bias detection
3. **Governance System** - Policy enforcement and risk management
4. **Prompt System** - Template management and optimization
5. **LLM Integration** - Multi-provider AI model access

### Database Models

- User profiles and preferences
- Context layers (6-layer system)
- Interaction history
- Prompts and versions
- CPD records
- Governance policies
- Alignment checks

## Architecture

```
ptcc/
├── backend/
│   ├── core/              # Core system implementations
│   │   ├── memory_system.py
│   │   ├── alignment_system.py
│   │   ├── governance_system.py
│   │   ├── prompt_system.py
│   │   └── llm_integration.py
│   ├── models/            # Database models
│   └── migrations/        # Database migrations
├── tests/                 # Test suites
├── .env                   # Environment configuration (API keys)
└── requirements.txt       # Python dependencies
```

## Common Tasks

### Running Tests

```bash
# LLM integration tests
python tests/test_llm_integration.py

# All tests
pytest tests/
```

### Database Operations

```bash
# Initialize database
python backend/migrations/create_comprehensive_ptcc_schema.py

# Check database tables
sqlite3 ptcc.db ".tables"
```

### Adding New Prompts

```python
from ptcc.backend.core.prompt_system import PromptLibraryManager

manager = PromptLibraryManager()
prompt = manager.create_prompt(
    prompt_name="Assessment Generator",
    prompt_category="assessment",
    prompt_template="Create {{num_questions}} questions about {{topic}}",
    description="Generates assessment questions",
    variables=["num_questions", "topic"]
)
```

## Configuration

### Environment Variables

Key settings in `.env`:

- `GEMINI_API_KEY` - Your Gemini API key (already set)
- `DATABASE_URL` - Database connection string
- `DEFAULT_LLM_PROVIDER` - Default AI provider (gemini)
- `DEFAULT_LLM_MODEL` - Default model (gemini-1.5-pro)
- `ENABLE_ALIGNMENT_CHECKS` - Enable AI alignment checks (true)

### Feature Flags

Enable/disable features in `.env`:

- `ENABLE_ALIGNMENT_CHECKS` - AI value alignment
- `ENABLE_BIAS_DETECTION` - Bias detection
- `ENABLE_GOVERNANCE_CHECKS` - Policy compliance
- `ENABLE_AUDIT_LOGGING` - Audit trail logging

## Next Steps

1. **Explore the Examples**
   - Run `python tests/test_llm_integration.py` to see LLM in action
   - Check `IMPLEMENTATION_SUMMARY.md` for detailed documentation

2. **Build Your First Agent**
   - Use the prompt system to create templates
   - Add memory tracking for personalization
   - Enable alignment checks for safety

3. **Customize for Your Needs**
   - Add custom prompts for your subject area
   - Configure alignment rules for your institution
   - Set up governance policies

4. **Monitor and Optimize**
   - Track prompt performance
   - Run A/B tests on variations
   - Analyze user interaction patterns

## Troubleshooting

### API Key Issues

If you get API key errors:
1. Check `.env` file has correct `GEMINI_API_KEY`
2. Verify the key is valid at [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
3. Restart your Python session after changing `.env`

### Import Errors

If you get import errors:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Database Errors

If database initialization fails:
```bash
# Remove old database
rm ptcc.db

# Reinitialize
python backend/migrations/create_comprehensive_ptcc_schema.py
```

## Resources

- **Documentation**: See `IMPLEMENTATION_SUMMARY.md`
- **Models**: Check `backend/models/` for all database schemas
- **Examples**: Look in `tests/` for usage examples
- **Configuration**: Review `.env.template` for all options

## Support

For issues or questions:
1. Check the documentation in `IMPLEMENTATION_SUMMARY.md`
2. Review test files for usage examples
3. Examine the source code - it's well-commented!

---

**Ready to build amazing AI-powered educational tools!** 🚀
