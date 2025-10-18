# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**PTCC (Personal Teaching Command Center)** is a local-first, AI-powered information management system designed for specialist teachers managing 400+ students across multiple campuses. It's a full-stack application with three main components:

1. **Backend API** (FastAPI) - Core business logic and safeguarding
2. **Desktop Dashboard** (Streamlit) - Teacher-facing interface  
3. **Mobile PWA** (React/Vite) - In-lesson quick-logging interface

## Quick Start Commands

### Start Everything (Recommended - Fast Version)
```bash
./start-ptcc-fast.sh
```
This launches all components sequentially with automatic health checks:
- Backend API on port 8001
- Mobile PWA on port 5174 (access via Streamlit sidebar link)
- Streamlit Dashboard on port 8501 (main entry point)

The fast launcher skips pip install if dependencies already exist, reducing startup time significantly.

### Start Everything (Original Script)
```bash
./start-ptcc.sh
```
Alternative launcher that installs/updates all dependencies before starting services.

### Individual Component Startup

**Backend API Only:**
```bash
cd backend
pip install -r requirements.txt
python -m backend.main
# Runs on http://localhost:8001
```

**Desktop Dashboard Only:**
```bash
cd frontend/desktop-web
pip install -r requirements.txt
python run.py
# Runs on http://localhost:8501
```

**Mobile PWA Only:**
```bash
cd frontend/mobile-pwa
npm install
npm run dev
# Runs on http://localhost:5174
```

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_llm_integration.py -v
```

### Run Single Test
```bash
pytest tests/test_llm_integration.py::test_function_name -v
```

### System Integration Test
```bash
python test_system_integration.py
```

### Coverage Report
```bash
pytest tests/ --cov=backend --cov-report=html
```

## Linting & Code Quality

### Python Linting
```bash
flake8 backend/ --max-line-length=120
black backend/ --check
mypy backend/
isort backend/ --check-only
```

### Auto-format Code
```bash
black backend/
isort backend/
```

### Frontend Linting
```bash
cd frontend/mobile-pwa
npm run lint
```

## Database Management

### Initialize Database
```bash
python scripts/simplified_migration.py
```

### Check Database Health
```bash
curl http://localhost:8001/health
```

### Backup Database
```bash
python -c "from backend.core.database import backup_database; backup_database()"
```

## Development Workflow

### Environment Setup
1. Copy `.env.template` to `.env` and configure:
   - `GEMINI_API_KEY` - Your Google Gemini API key
   - `DEFAULT_LLM_PROVIDER` - Set to "gemini" for cloud, "ollama" for local
   - `JWT_SECRET` - Change from default in production

2. Activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or: venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   cd backend && pip install -r requirements.txt
   cd frontend/desktop-web && pip install -r requirements.txt
   cd frontend/mobile-pwa && npm install
   ```

### API Development
- **Main file**: `backend/main.py` - FastAPI app initialization
- **API routes**: `backend/api/` - Organized by feature
- **Core systems**: `backend/core/` - Database, LLM integration, safeguarding
- **Models**: `backend/models/database_models.py` - SQLAlchemy schemas

### Frontend Development
- **Desktop**: `frontend/desktop-web/app.py` - Streamlit application (runs on port 8501)
  - Sidebar navigation with links to all features
  - "📱 Apps" section with links to Mobile PWA
- **Mobile**: `frontend/mobile-pwa/src/` - React components with Vite (runs on port 5174)
  - Two main views: Logger (quick logging) and Agents (AI analysis)
  - Desktop-first responsive design

### Database Development
- **SQLite location**: `data/school.db`
- **Migrations**: `backend/migrations/` - Schema creation scripts
- **Models**: `backend/models/database_models.py` - ORM definitions

## System Architecture

### Three-Layer Architecture

```
┌──────────────────────────────────────────┐
│     User Interfaces                      │
├──────────────────────────────────────────┤
│  Desktop (Streamlit)  │  Mobile PWA (React)
└────────────┬──────────┴──────────────┬───┘
             │ API Calls               │
             └────────────┬────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ API Routes │  │ AI Agents  │  │ Safeguard  │
    │ (9 routers)│  │ & LLM      │  │ System     │
    └────┬───────┘  └────┬───────┘  └────┬───────┘
         │                │               │
         └────────────────┼───────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
          ┌─────────┐ ┌─────────┐ ┌─────────┐
          │ SQLite  │ │ ChromaDB│ │ Gemini  │
          │ Database│ │ Vectors │ │ API     │
          └─────────┘ └─────────┘ └─────────┘
```

### API Router Organization
- **briefing**: Daily teacher briefings
- **search**: Semantic search across documents
- **students**: Student data management
- **agents**: AI teacher tools (at-risk identifier, behavior manager, learning path)
- **chat**: Conversational interface
- **workflows**: Workflow orchestration
- **classroom-tools**: Classroom-specific features
- **cca**: Co-curricular activities
- **guardian**: Parent communication
- **safeguarding**: Privacy-preserving student analysis

### Core Components
- **database.py**: SQLite connection, session management, health checks
- **config.py**: YAML-based configuration with defaults
- **llm_integration.py**: LLM provider abstraction (Gemini, Claude, Ollama)
- **rag_engine.py**: Semantic search using ChromaDB
- **briefing_engine.py**: Daily briefing generation
- **safeguarding_orchestrator.py**: Privacy-preserving compliance checks
- **agent_orchestrator.py**: Multi-agent coordination
- **workflow_engine.py**: Workflow execution

## Key Architectural Patterns

### Configuration Management
- YAML-based config in `config/config.yaml`
- Fallback to defaults in `backend/core/config.py`
- Environment variables in `.env`

### Database Access
- SQLAlchemy ORM with SQLite
- Generator-based session management in `get_db()`
- Single connection pool (StaticPool for SQLite)

### LLM Integration
- Provider-agnostic abstraction layer
- Supports Gemini (cloud), Claude, and Ollama (local)
- Context window and token management

### Error Handling
- FastAPI HTTPException for API errors
- Logging via `logging_config.py`
- Health checks on critical components

## Privacy & Security

This system is **local-first** and **privacy-preserving**:
- All data stored locally in SQLite
- No external cloud storage of sensitive data
- Safeguarding system anonymizes/tokenizes student identifiers
- GDPR-compliant data export and deletion
- Optional end-to-end encryption (database encryption flag in config)

## Data Directories

```
data/
├── school.db              # Main SQLite database
├── chroma/                # Vector embeddings for semantic search
├── processed/             # Processed data files
└── backups/               # Automatic database backups
```

## Debugging

### Backend Debugging
- Check logs: `.ptcc_logs/backend.log`
- Enable debug mode: Set `DEBUG=true` in `.env`
- API docs: `http://localhost:8001/docs` (Swagger UI)
- Health endpoint: `http://localhost:8001/health`

### Frontend Debugging
- Desktop logs: `.ptcc_logs/dashboard.log`
- PWA logs: `.ptcc_logs/pwa.log`
- Browser dev tools: F12 in desktop/mobile apps

#### CSS Responsive Design Issues (React/Web Apps)
**Problem**: Dynamic CSS class switching works in JavaScript but container dimensions don't change visually.

**Root Cause**: CSS specificity conflicts when multiple stylesheets contain competing rules.

**Symptoms**:
- State changes correctly (buttons show active states)
- CSS classes apply to DOM elements
- Container width/layout remains unchanged

**Diagnostic Steps**:
1. **Check for conflicting CSS rules**:
   ```bash
   # Find all width/max-width rules in the project
   grep -r "max-width\|width:" frontend/ --include="*.css" --include="*.scss"
   ```

2. **Browser DevTools inspection**:
   - Inspect element and check Computed styles
   - Look for crossed-out CSS rules (overridden)
   - Verify CSS classes are being applied

**Solutions**:

3. **CSS Specificity Override** - Use `!important` to force styles:
   ```css
   /* Example: Device mode classes */
   .container.mobile { width: 375px !important; max-width: 375px !important; }
   .container.tablet { width: 1024px !important; max-width: 1024px !important; }
   .container.desktop { width: 100vw !important; max-width: 100vw !important; }
   ```

4. **Visual Debugging** - Add colored borders during development:
   ```css
   .container.mobile { border: 5px solid #ff0000 !important; }
   .container.tablet { border: 5px solid #00ff00 !important; }
   .container.desktop { border: 5px solid #0000ff !important; }
   ```

5. **Browser Cache**: Hard refresh to ensure latest CSS loads:
   - Chrome/Safari: Cmd+Shift+R (macOS) or Ctrl+Shift+R (Windows)
   - Or disable cache in DevTools Network tab

**Prevention**:
- Use CSS-in-JS libraries (styled-components, emotion) for scoped styles
- Implement CSS naming conventions (BEM, CSS Modules)
- Keep responsive breakpoints in a single stylesheet

### Database Debugging
```bash
sqlite3 data/school.db ".tables"  # List all tables
sqlite3 data/school.db "SELECT COUNT(*) FROM students;"  # Query counts
```

## Performance Considerations

- Database queries typically <100ms
- AI agent processing <2 seconds
- Semantic search <500ms
- Frontend load <3 seconds
- Vector embeddings cached in ChromaDB

## Common Development Tasks

### Add New API Endpoint
1. Create route function in appropriate `backend/api/*.py` file
2. Import router in `backend/main.py`
3. Include router in app with `app.include_router()`

### Add Database Table
1. Define SQLAlchemy model in `backend/models/database_models.py`
2. Model automatically included in `create_tables()`
3. Run `python backend/migrations/create_comprehensive_ptcc_schema.py`

### Use LLM API
```python
from backend.core.llm_integration import LLMIntegration
llm = LLMIntegration()
response = llm.generate(prompt="Your prompt", provider="gemini")
```

### Query Student Data
```python
from backend.core.database import SessionLocal
from backend.models.database_models import Student
db = SessionLocal()
students = db.query(Student).filter(...).all()
```

### Semantic Search
```python
from backend.core.rag_engine import RAGEngine
rag = RAGEngine()
results = rag.search("query text", top_k=5)
```

## File Organization Standards

- `backend/api/` - Each file handles one domain
- `backend/core/` - Shared infrastructure only
- `backend/models/` - Database schemas only
- `backend/ingestion/` - Data parsing and import
- `tests/` - Unit and integration tests
- `scripts/` - Setup and utility scripts
- `config/` - Configuration files

## Integration Points

### Desktop (Streamlit) ↔ Backend
- Streamlit app on port 8501 makes REST calls to `http://localhost:8001/api/*`
- CORS configured in `backend/main.py` for port 8501
- Sidebar includes link to Mobile PWA for seamless navigation

### Mobile PWA (React) ↔ Backend  
- React app on port 5174 makes REST calls to `http://localhost:8001/api/*`
- CORS configured for port 5174
- Can be accessed from Streamlit sidebar via "📱 Apps" section
- Two views: "📝 Logger" for quick logging, "🤖 Agents" for AI analysis
- **Device Mode Toggle**: Built-in responsive design switcher (Mobile 375px, Tablet 1024px, Desktop full-width)

### Safeguarding System
- Runs on startup in `backend/main.py` lifespan
- Provides privacy-preserving student analysis
- Integrated with AI agents for risk assessment

## Important Notes

- Do **not** commit `.env` or database files to version control
- Keep `.env.template` updated with new required variables
- All student data must remain confidential and stored locally
- Responses from LLMs may require post-processing for teacher context
- ChromaDB vector store is embedded (single-node, perfect for local use)
- Backup database regularly before major operations
