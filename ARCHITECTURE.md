# PTCC Architecture Documentation

## System Overview

PTCC (Personal Teaching Command Center) is a **local-first, AI-powered information management system** designed for specialist teachers managing 400+ students across multiple campuses. It consists of three main components communicating through a REST API.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interfaces                          │
├─────────────────────────────────────────────────────────────┤
│  Desktop Dashboard (Streamlit)  │  Mobile PWA (React/Vite)  │
│       http://localhost:8501     │  http://localhost:5174     │
└────────────────┬─────────────────┴──────────────┬────────────┘
                 │ REST API Calls (CORS-enabled)  │
                 └────────────────┬────────────────┘
                                  ▼
                    ┌──────────────────────────┐
                    │   FastAPI Backend        │
                    │  http://localhost:8001   │
                    │  9 Domain Routers        │
                    └──────────┬───────────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
            ┌────────┐    ┌──────────┐   ┌─────────┐
            │ SQLite │    │ ChromaDB │   │ Gemini  │
            │  Local │    │ Vectors  │   │  API    │
            └────────┘    └──────────┘   └─────────┘
            school.db     Vector Store   Cloud AI
```

---

## Component Architecture

### 1. Backend API (FastAPI)

**Location:** `backend/main.py`  
**Framework:** FastAPI with Uvicorn ASGI server  
**Port:** 8001

#### Router Organization (9 Domain Routers)

| Router | Prefix | Purpose | Key Endpoints |
|--------|--------|---------|---------------|
| `briefing` | `/api/briefing` | Daily teacher briefing generation | `/today`, `/schedule`, `/incidents` |
| `search` | `/api/search` | Semantic search across documents | `/documents`, `/students`, `/logs` |
| `students` | `/api/students` | Student data management & quick logs | `/`, `/{id}`, `/logs`, `/classes/list` |
| `agents` | `/api/agents` | AI agent operations | `/at-risk`, `/behavior`, `/learning-paths` |
| `chat` | `/api/chat` | Conversational AI interface | `/completions`, `/quick-actions` |
| `documents` | `/api/documents` | Document upload & indexing | `/upload`, `/search`, `/list` |
| `workflows` | `/api/workflows` | Workflow execution & orchestration | `/execute`, `/status` |
| `classroom-tools` | `/api/classroom-tools` | In-lesson tools | `/attendance`, `/quick-log` |
| `safeguarding` | `/api/safeguarding` | Privacy-preserving compliance checks | `/analysis`, `/flags` |

#### Core Modules

```
backend/
├── main.py                           # FastAPI app + lifespan management
├── core/
│   ├── database.py                   # SQLAlchemy ORM, connection pooling
│   ├── config.py                     # YAML-based configuration
│   ├── llm_integration.py            # LLM provider abstraction (Gemini/Claude/Ollama)
│   ├── rag_engine.py                 # ChromaDB semantic search
│   ├── briefing_engine.py            # Briefing generation logic
│   ├── safeguarding_orchestrator.py  # Privacy-preserving analysis
│   ├── agent_orchestrator.py         # Multi-agent coordination
│   ├── workflow_engine.py            # Workflow execution
│   └── logging_config.py             # Centralized logging
├── models/
│   └── database_models.py            # SQLAlchemy models (Student, Log, Assessment, etc.)
├── api/
│   ├── briefing.py, search.py, students.py, ... # 9 routers
└── ingestion/
    └── data_ingestion.py             # PDF parsing, data import
```

#### Request Flow

```
1. Client → Request → FastAPI endpoint
2. Endpoint → Validation with Pydantic
3. FastAPI → Dependency injection (get_db, get_rag_engine)
4. Business logic → Database query OR LLM call OR RAG search
5. Response → Serialized to JSON → Client
```

#### Key Features

- **Async/Await:** All endpoints async for concurrent requests
- **Dependency Injection:** Database sessions managed via `Depends(get_db)`
- **Error Handling:** HTTPException for all API errors with status codes
- **CORS:** Configured for Streamlit (8501) and React (5174)
- **Lifespan Management:** Database init, RAG setup on startup

---

### 2. Frontend - Desktop Dashboard (Streamlit)

**Location:** `frontend/desktop-web/app.py`  
**Framework:** Streamlit (Python web framework)  
**Port:** 8501

#### Page Structure

```
app.py (Main Page)
├── Sidebar Navigation (unified across all pages)
├── Pages (Dynamic via page selection)
│   ├── 01_📅_Briefing.py           # Daily briefing + AI assistant
│   ├── 02_🤖_Teacher_Assistant.py   # AI tools & suggestions
│   ├── 03_👥_Students.py             # Student list, details, logs
│   ├── 04_🔍_Search.py               # Semantic search
│   ├── 05_📊_Analytics.py            # Dashboards
│   ├── 06_📚_Documents.py            # Upload & manage
│   └── 07_⚙️_Settings.py             # Configuration
└── Session State Management
    └── Caching, history, filters
```

#### Key Components

**API Communication:**
```python
def fetch_api(endpoint, params=None):
    """Fetch data from API"""
    response = requests.get(f"{API_BASE}{endpoint}", params=params)
    return response.json() if response.status_code == 200 else None
```

**Session State Patterns:**
- `st.session_state.briefing_chat_history` - Stores chat messages
- `st.session_state.briefing_chat_context` - Stores search context
- User input caching for better UX

**Sidebar Navigation:**
```python
with st.sidebar:
    st.title("PTCC")
    page = st.selectbox("Navigate", [
        "📅 Daily Briefing",
        "👥 Students",
        "🔍 Search",
        ...
    ])
```

#### Frontend Quirks & Workarounds

**Quirk 1: Empty List vs. Error**
- Empty API response `[]` should display empty state, not error
- Fix: Check `if response is None` for errors, `if len(response) == 0` for empty

**Quirk 2: Real-time Updates**
- Streamlit re-runs entire script on every interaction
- Use `st.rerun()` strategically to avoid infinite loops

**Quirk 3: Image/File Uploads**
- `st.file_uploader` returns UploadedFile object
- Must use `.read()` to get bytes before sending to API

---

### 3. Frontend - Mobile PWA (React/Vite)

**Location:** `frontend/mobile-pwa/`  
**Framework:** React with Vite bundler  
**Port:** 5174

#### Component Structure

```
src/
├── components/
│   ├── Dashboard.tsx         # Main mobile interface
│   ├── QuickLog.tsx          # Log entry capture
│   ├── StudentCard.tsx       # Student summary
│   └── Chat.tsx              # Mobile chat interface
├── pages/
│   └── Home.tsx              # PWA entry point
├── services/
│   └── api.ts                # API client
└── App.tsx                   # Root component
```

#### Key Features

- **Progressive Web App:** Works offline, installable
- **Responsive Design:** Optimized for mobile devices
- **Quick Logging:** Fast entry of behavioral/academic notes
- **Real-time Sync:** Syncs with backend when online

---

### 4. Database (SQLite)

**Location:** `data/school.db`

#### Schema Overview

```
students
├── id (PK)
├── name
├── class_code
├── year_group
├── campus
├── support_level (0-3)
├── support_notes
└── last_updated

quick_logs
├── id (PK)
├── student_id (FK → students)
├── timestamp
├── log_type (positive/negative/neutral)
├── category
├── points
└── note

assessments
├── id (PK)
├── student_id (FK → students)
├── assessment_type
├── subject
├── score/max_score
├── percentage
└── date

incidents
├── id (PK)
├── student_id (FK → students)
├── severity
├── category
└── timestamp
```

#### Connection Management

```python
# SQLAlchemy with SQLite StaticPool
engine = create_engine(
    "sqlite:///data/school.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Generator-based session management
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Why StaticPool?** SQLite doesn't support multi-threaded connections. StaticPool reuses single connection safely.

---

### 5. Vector Store (ChromaDB)

**Location:** `data/chroma/`

#### Purpose
- Semantic search across documents
- Similarity matching for student incidents
- Intelligent document retrieval

#### Collections

| Collection | Documents | Use Case |
|------------|-----------|----------|
| `documents` | Uploaded PDFs, emails, briefs | Search across all documents |
| `student_profiles` | Student data embeddings | Find similar students |
| `incidents` | Historical incident descriptions | Pattern matching |

#### RAG Engine

```python
class RAGEngine:
    def index_document(self, path, content, metadata):
        """Add document to ChromaDB"""
        # Chunk content into smaller pieces
        # Generate embeddings via sentence-transformers
        # Store in ChromaDB with metadata
    
    def search(self, query, top_k=5, filters=None):
        """Semantic search"""
        # Query → Embedding → ChromaDB search → Results with scores
```

**Deferred Initialization:** RAG engine not initialized on startup (for speed). Initialized on first use.

---

### 6. AI Integration (Gemini API)

**Provider:** Google Gemini  
**Configuration:** GEMINI_API_KEY in `.env`

#### LLM Provider Abstraction

```python
class LLMIntegration:
    def generate(self, prompt, provider="gemini", **kwargs):
        """Provider-agnostic API"""
        if provider == "gemini":
            return self._call_gemini(prompt, **kwargs)
        elif provider == "claude":
            return self._call_claude(prompt, **kwargs)
        elif provider == "ollama":
            return self._call_ollama(prompt, **kwargs)
```

#### Agent Types

| Agent | Purpose | Endpoint |
|-------|---------|----------|
| **AtRiskStudentAgent** | Identify struggling students | `/api/agents/at-risk` |
| **ClassroomBehaviorAgent** | Behavior pattern analysis | `/api/agents/behavior` |
| **PersonalizedLearningPathAgent** | Suggest learning paths | `/api/agents/learning-paths` |

---

## Data Flow Examples

### Example 1: Loading Student List

```
1. Frontend: User clicks "👥 Students" page
   └─ Calls: fetch_api("/api/students/", {"class_code": "3A"})

2. Backend: GET /api/students/?class_code=3A
   └─ Route handler: get_students(class_code="3A", db=SessionLocal())
   └─ Query: db.query(Student).filter(Student.class_code == "3A")
   └─ Response: [StudentResponse(...), ...]

3. Database: Executes SELECT * FROM students WHERE class_code = '3A'
   └─ Returns: 20 rows

4. Frontend: Receives JSON array
   └─ Converts to DataFrame
   └─ Displays in st.dataframe()
```

### Example 2: Semantic Document Search

```
1. Frontend: User types "attendance policy" in search
   └─ Calls: fetch_api("/api/search", {"query": "attendance policy"})

2. Backend: GET /api/search?query=attendance+policy
   └─ Route handler: search_documents(query, db, rag_engine)
   └─ RAG Engine: Convert query → embedding → ChromaDB search
   └─ ChromaDB: Find top 5 documents with similarity score
   └─ Response: [{"filename": "policy.pdf", "excerpt": "...", "score": 0.92}, ...]

3. Frontend: Displays results with relevance scores
```

### Example 3: Generate Briefing with AI

```
1. Frontend: User visits "📅 Daily Briefing" page
   └─ Calls: fetch_api("/api/briefing/today")

2. Backend: GET /api/briefing/today
   └─ Route handler: get_daily_briefing(db, rag_engine, llm)
   └─ Pipeline:
      a) Query database: today's schedule, incidents, key students
      b) RAG search: "relevant documents for today"
      c) LLM prompt: "Generate briefing from: [schedule] [incidents] [docs]"
      d) LLM generates markdown briefing with context

3. Response: {"briefing": "# Today's Briefing\n...", "context": {...}}

4. Frontend: Displays formatted briefing markdown
```

---

## Configuration System

### YAML Configuration

**File:** `config/config.yaml`

```yaml
school:
  name: "Mock School"
  campuses: ["JC", "SC"]
  year_groups: [7, 8, 9, 10, 11]

llm:
  default_provider: "gemini"
  context_window: 4000
  temperature: 0.7

rag:
  chunk_size: 500
  overlap: 100
  similarity_threshold: 0.7

database:
  path: "data/school.db"
  backup_enabled: true
```

### Environment Variables

```bash
# .env file (not committed)
GEMINI_API_KEY=your-api-key-here
DEFAULT_LLM_PROVIDER=gemini
JWT_SECRET=your-jwt-secret
DEBUG=false
```

---

## Error Handling Strategy

### API Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Student data returned |
| 404 | Not found | Student ID doesn't exist |
| 400 | Bad request | Invalid filter parameter |
| 500 | Server error | Database connection failed |

### Frontend Error Handling

```python
# Pattern 1: Silent failure with warning
if not students_data:
    st.warning("Could not load students")
    return

# Pattern 2: Specific error messages
try:
    response = requests.get(...)
except requests.exceptions.ConnectionError:
    st.error("Cannot connect to backend")
except requests.exceptions.Timeout:
    st.error("Request timed out")
```

### Backend Error Logging

```python
# Pattern: Log + raise exception
logger.error(f"Error getting students: {e}", exc_info=True)
raise HTTPException(status_code=500, detail="Failed to get students")
```

---

## Performance Considerations

### Database Optimization

**Current Indexes:**
- Primary keys on all tables
- Foreign key indices (auto-created)
- No additional indices (add as needed)

**Query Performance:**
- Student list query: ~50ms (45 records)
- Search by class: ~30ms (index-assisted)
- Incident query: ~100ms (may need indexing)

**Scalability Notes:**
- SQLite suitable for <100K records
- For 400+ students across multiple years: Still fine for SQLite
- Consider PostgreSQL migration if >1M records or >10 concurrent users

### Frontend Performance

- **Page Load:** ~2-3 seconds (includes Streamlit startup)
- **API Requests:** ~200-500ms (network + processing)
- **Chart Rendering:** ~1s (Streamlit limitation)

### RAG Performance

- **First Query:** ~500ms (includes ChromaDB load)
- **Subsequent Queries:** ~200-300ms (cached)
- **Document Indexing:** ~1s per MB

---

## Security Considerations

### Current State

⚠️ **NOT PRODUCTION-READY**

- No authentication/authorization
- No rate limiting
- No input sanitization
- CORS allows all methods (should restrict)
- JWT_SECRET is default

### Recommendations for Production

1. **Authentication:** Implement teacher login with OAuth2/JWT
2. **Authorization:** Role-based access (teacher, admin, safeguarding officer)
3. **Data Privacy:** Encrypt sensitive fields (support_notes, incidents)
4. **Audit Logging:** Track all data access and modifications
5. **HTTPS/TLS:** Use SSL certificates
6. **Rate Limiting:** Prevent API abuse
7. **Input Validation:** Sanitize all user inputs

---

## Deployment Patterns

### Local Development (Current)

```bash
# Terminal 1: Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8001

# Terminal 2: Frontend
streamlit run frontend/desktop-web/app.py

# Terminal 3: Mobile PWA (optional)
cd frontend/mobile-pwa && npm run dev
```

### Docker Deployment (Recommended)

```dockerfile
# Multi-stage build
FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ backend/
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0"]
```

### Kubernetes Deployment (For Scale)

```yaml
# Deployment manifest
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ptcc-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ptcc
  template:
    spec:
      containers:
      - name: api
        image: ptcc-backend:latest
        ports:
        - containerPort: 8001
```

---

## Testing Architecture

### Test Structure

```
tests/
├── unit/
│   ├── test_database.py           # ORM tests
│   ├── test_llm_integration.py    # LLM mocking
│   └── test_rag_engine.py         # RAG functionality
├── integration/
│   ├── test_api_endpoints.py      # Full API tests
│   └── test_data_flow.py          # End-to-end
└── conftest.py                    # Pytest fixtures
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Coverage report
pytest tests/ --cov=backend --cov-report=html

# Specific test
pytest tests/test_api_endpoints.py::test_get_students -v
```

---

## Monitoring & Debugging

### Log Files

- **Backend:** `.ptcc_logs/backend.log`
- **Frontend:** `.ptcc_logs/dashboard.log`
- **Mobile PWA:** `.ptcc_logs/pwa.log`

### Health Checks

```bash
# Backend health
curl http://localhost:8001/health

# API test
curl http://localhost:8001/api/students/ | python -m json.tool

# Database test
sqlite3 data/school.db ".tables"

# Streamlit logs
tail -100 ~/.streamlit/logs/2025-10-17_*.log
```

### Debug Mode

```bash
# Enable debug logging in .env
DEBUG=true

# Verbose backend logs
PYTHONPATH=/project LOG_LEVEL=DEBUG python -m backend.main

# Frontend debug
streamlit run app.py --logger.level=debug
```

---

## Known Architectural Limitations

| Limitation | Impact | Solution |
|-----------|--------|----------|
| SQLite single-process | No concurrent writes | Use PostgreSQL |
| Streamlit re-runs entire script | Slower UX | Use React for critical paths |
| No caching layer | Repeated DB queries | Add Redis |
| Synchronous I/O in some agents | Blocks requests | Use async/await everywhere |
| No request queuing | Rate limit issues | Add job queue (Celery/RQ) |

---

## Next Architectural Improvements

### Phase 1 (Next 2 weeks)
- [ ] Add request logging middleware
- [ ] Implement simple caching (functools.lru_cache)
- [ ] Add database connection pooling metrics
- [ ] Create monitoring dashboard

### Phase 2 (Weeks 3-4)
- [ ] Migrate to PostgreSQL
- [ ] Add Redis caching layer
- [ ] Implement proper auth (OAuth2)
- [ ] Add request rate limiting

### Phase 3 (Month 2)
- [ ] Microservices split (search, agents, RAG)
- [ ] Async job queue for AI processing
- [ ] Caching layer for vector embeddings
- [ ] Multi-tenant support (multi-school)

---

## Contact Points

- **API Documentation:** http://localhost:8001/docs (Swagger UI)
- **Database Issues:** Check `.ptcc_logs/backend.log` for SQL errors
- **Frontend Issues:** Browser console (F12) + Streamlit logs
- **Performance Issues:** Use `time` module in Python or browser DevTools
