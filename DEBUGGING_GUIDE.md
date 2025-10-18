# PTCC Debugging Guide

Quick reference for diagnosing and fixing common issues.

---

## Before Debugging: Quick Checks

```bash
# 1. Kill all existing processes and start fresh
pkill -f uvicorn
pkill -f streamlit
sleep 2

# 2. Verify services are running
curl -s http://localhost:8001/health  # Should see JSON response
curl -s http://localhost:8501/ > /dev/null && echo "Frontend OK"

# 3. Check database exists and has data
sqlite3 data/school.db "SELECT COUNT(*) FROM students;" # Should return 45

# 4. Check environment
python3 --version  # Should be 3.11+
pip list | grep -E "fastapi|streamlit"
```

---

## Issue: Backend Won't Start

### Symptom
```
Error loading ASGI app. Could not import module "main".
```

### Debug Steps

**Step 1: Check logs**
```bash
tail -100 /tmp/backend.log
```

**Step 2: Check for import errors**
Look for lines like:
- `ModuleNotFoundError: No module named 'PyPDF2'`
- `ImportError: cannot import name 'X' from 'Y'`

### Common Causes & Fixes

#### Cause: Missing Python Package

```bash
# Missing PyPDF2
# Error: ModuleNotFoundError: No module named 'PyPDF2'
# Fix:
cd backend && pip install -r requirements.txt

# Verify
python3 -c "import PyPDF2; print('OK')"
```

#### Cause: Python Path Issues

```bash
# Error: ModuleNotFoundError: No module named 'backend'
# Fix: Ensure you're in project root
cd /Users/cantillonpatrick/Desktop/ptcc_standalone

# Start with full path
uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

#### Cause: Port Already in Use

```bash
# Error: Address already in use
# Debug:
lsof -i :8001
# If output shows process, kill it:
kill -9 <PID>

# Or use different port
uvicorn backend.main:app --port 8002
```

#### Cause: Database Lock

```bash
# Error: database is locked
# Fix: Remove WAL files
rm data/school.db-wal data/school.db-shm

# If needed, start fresh
# (backup first!)
cp data/school.db data/school.db.backup
rm data/school.db
python backend/migrations/create_comprehensive_ptcc_schema.py
```

---

## Issue: Frontend Shows "Could Not Load Students"

### Symptom
```
⚠️ Could not load students data
```

### Debug Steps

**Step 1: Check backend is running**
```bash
curl -s http://localhost:8001/api/students/ | python3 -m json.tool | head -20
```

Expected output: Array of student objects

**If empty array `[]`:**
- Database exists but has no students
- See "Issue: Database has no data"

**If connection error:**
- Backend not running, see "Issue: Backend Won't Start"

**Step 2: Check API_BASE setting**
```bash
grep "API_BASE" frontend/desktop-web/app.py
```

Should be: `API_BASE = "http://localhost:8001"`

**Step 3: Check Streamlit logs**
```bash
tail -100 .ptcc_logs/dashboard.log 2>/dev/null || echo "Log file not found"
```

Look for error messages from `fetch_api()` calls.

### Common Causes & Fixes

#### Cause: API_BASE pointing to wrong port

```python
# In frontend/desktop-web/app.py, line 30
# Wrong:
API_BASE = "http://localhost:8005"

# Correct:
API_BASE = "http://localhost:8001"
```

#### Cause: Backend endpoint returning empty array

```bash
# Verify database has students
sqlite3 data/school.db "SELECT COUNT(*) FROM students;"
# Output: 45 (or empty if 0)

# If 0, see: Issue: Database has no data
# If >0, backend query might be filtering incorrectly

# Test endpoint directly
curl -s "http://localhost:8001/api/students/?class_code=3A" | python3 -m json.tool
```

#### Cause: Frontend treating empty array as error

```python
# In app.py, look for this pattern (WRONG):
if not students_data:
    st.warning("Could not load students")
    return

# Should be (CORRECT):
if students_data is None:  # Only error if API failed
    st.warning("Could not load students")
    return

if isinstance(students_data, list) and len(students_data) > 0:
    # Display students
else:
    st.info("No students found. Try adjusting filters.")
```

---

## Issue: Database Has No Data

### Symptom
```bash
sqlite3 data/school.db "SELECT COUNT(*) FROM students;"
# Output: 0
```

### Debug Steps

**Step 1: Check table exists**
```bash
sqlite3 data/school.db ".tables"
# Should show: students quick_logs assessments incidents ...
```

**Step 2: Check backup exists**
```bash
ls -la data/backups/
```

### Common Causes & Fixes

#### Cause: Database never initialized

```bash
# Create schema
python backend/migrations/create_comprehensive_ptcc_schema.py

# Verify
sqlite3 data/school.db ".tables"
```

#### Cause: Students not ingested from PDF

```bash
# Check mock school PDF exists
ls -la data/mock_school_data/ | grep -i "pdf\|excel"

# Run ingestion script
python backend/ingestion/data_ingestion.py

# Verify
sqlite3 data/school.db "SELECT COUNT(*) FROM students;"
```

#### Cause: Manual data entry needed

```bash
# Add sample student for testing
python3 << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.database_models import Student
from datetime import datetime

engine = create_engine("sqlite:///data/school.db")
Session = sessionmaker(bind=engine)
session = Session()

student = Student(
    name="Test Student",
    class_code="3A",
    year_group="7",
    campus="JC",
    support_level=0,
    support_notes="Test entry",
    last_updated=datetime.now()
)
session.add(student)
session.commit()
print("✓ Sample student added")
session.close()
EOF
```

---

## Issue: PDF Upload Fails

### Symptom
```
Error uploading document: [error message]
```

### Debug Steps

**Step 1: Check PyPDF2 is installed**
```bash
python3 -c "import PyPDF2; print('OK')"
```

**Step 2: Test PDF extraction directly**
```python
python3 << 'EOF'
import PyPDF2
import io

# Test with sample PDF
with open("path/to/test.pdf", "rb") as f:
    pdf_reader = PyPDF2.PdfReader(f)
    print(f"Pages: {len(pdf_reader.pages)}")
    print(f"First page text: {pdf_reader.pages[0].extract_text()[:100]}")
EOF
```

### Common Causes & Fixes

#### Cause: PDF is corrupted or encrypted

```bash
# Test PDF validity
python3 << 'EOF'
import PyPDF2

try:
    with open("your_file.pdf", "rb") as f:
        reader = PyPDF2.PdfReader(f)
        print(f"Valid PDF with {len(reader.pages)} pages")
except Exception as e:
    print(f"Invalid PDF: {e}")
EOF
```

#### Cause: File too large

```bash
# Check file size
ls -lh your_file.pdf

# If >50MB, split or compress first
# MaxPostSize in FastAPI is 25MB by default
```

---

## Issue: Search Returns No Results

### Symptom
```
🔍 No documents found matching 'your query'
```

### Debug Steps

**Step 1: Check documents are indexed**
```bash
ls -la data/chroma/
# Should have some files/subdirs

# Or test ChromaDB directly
python3 << 'EOF'
import chromadb

client = chromadb.PersistentClient(path="data/chroma")
try:
    collection = client.get_collection("documents")
    print(f"Documents indexed: {collection.count()}")
except Exception as e:
    print(f"No documents collection: {e}")
EOF
```

**Step 2: Check RAG engine initialization**
```bash
# Look in backend logs for:
grep "RAG engine" .ptcc_logs/backend.log

# Should see initialization on first use
```

### Common Causes & Fixes

#### Cause: No documents uploaded yet

```bash
# Upload a document first
# Via UI: Visit "📚 Documents" → Upload Files
# Via API:
curl -X POST http://localhost:8001/api/documents/upload \
  -F "file=@your_file.pdf" \
  -F "doc_type=briefing"
```

#### Cause: ChromaDB collection corrupted

```bash
# Backup and rebuild
cp -r data/chroma data/chroma.backup
rm -rf data/chroma

# Restart backend (will initialize fresh)
# Re-upload documents
```

#### Cause: Query too specific or wrong keywords

```bash
# Try broader search terms
# Wrong: "attendance policy section 3.2"
# Better: "attendance"

# Check what's in the index
python3 << 'EOF'
import chromadb

client = chromadb.PersistentClient(path="data/chroma")
collection = client.get_collection("documents")
results = collection.get()
for i, doc in enumerate(results['metadatas'][:5]):
    print(f"{i}: {doc}")
EOF
```

---

## Issue: AI Features Not Working

### Symptom
```
⚠️ Assistant is in fallback mode (GEMINI_API_KEY not set)
```

### Debug Steps

**Step 1: Check API key configuration**
```bash
grep "GEMINI_API_KEY" .env
# Should show: GEMINI_API_KEY=sk_...
```

**If missing:**
```bash
# Add to .env file
echo 'GEMINI_API_KEY=your_key_here' >> .env

# Restart backend
pkill -f uvicorn
sleep 1
uvicorn backend.main:app --host 0.0.0.0 --port 8001 &
```

**Step 2: Verify API key works**
```bash
python3 << 'EOF'
import os
os.environ['GEMINI_API_KEY'] = 'your_key'

from backend.core.llm_integration import LLMIntegration
llm = LLMIntegration()
response = llm.generate("Say hello", provider="gemini")
print(response)
EOF
```

### Common Causes & Fixes

#### Cause: API key invalid or expired

```bash
# Get new API key from:
# https://makersuite.google.com/app/apikey

# Update .env
vi .env
# Edit: GEMINI_API_KEY=new_key_here

# Restart
pkill -f uvicorn
```

#### Cause: Rate limit exceeded

```bash
# Wait 1 minute and retry
# Or check quota: https://console.cloud.google.com

# In meantime, use fallback (no AI)
# This is normal for development
```

#### Cause: Network connectivity issue

```bash
# Test external connectivity
curl -s https://generativelanguage.googleapis.com/v1beta/models \
  -H "x-api-key: $GEMINI_API_KEY" | head -20
```

---

## Issue: Slow Response Times

### Symptom
```
Requests taking >2-3 seconds
```

### Debug Steps

**Step 1: Identify slow component**
```bash
# Add timing to API calls (in app.py)
import time

start = time.time()
students = fetch_api("/api/students/")
elapsed = time.time() - start
print(f"API call took {elapsed:.2f}s")
```

**Step 2: Check backend logs for slow queries**
```bash
grep "SELECT" .ptcc_logs/backend.log | head -20
```

### Common Causes & Fixes

#### Cause: N+1 Query Problem

```python
# Wrong (N+1 queries):
students = db.query(Student).all()
for student in students:
    logs = db.query(QuickLog).filter(QuickLog.student_id == student.id).all()

# Better (single query):
from sqlalchemy.orm import joinedload
students = db.query(Student).options(joinedload(Student.logs)).all()
```

#### Cause: Missing database indices

```bash
# Check existing indices
sqlite3 data/school.db ".indices"

# Add if missing
sqlite3 data/school.db "CREATE INDEX idx_logs_student ON quick_logs(student_id);"
```

#### Cause: Streamlit re-rendering

```python
# Use caching
@st.cache_data
def load_students():
    return fetch_api("/api/students/")

# Or cache at session level
if 'students' not in st.session_state:
    st.session_state.students = fetch_api("/api/students/")
```

---

## Issue: CORS Errors in Browser Console

### Symptom
```
Access to XMLHttpRequest blocked by CORS policy
```

### Debug Steps

**Step 1: Check CORS configuration**
```python
# In backend/main.py, around line 100
# Should have:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit
        "http://localhost:5174",  # React
    ]
)
```

### Common Causes & Fixes

#### Cause: Frontend port not in CORS whitelist

```python
# If frontend on port 8502 (not in list)
# Add to backend/main.py:
allow_origins=[
    "http://localhost:8501",
    "http://localhost:8502",  # Add this
]

# Restart backend
```

#### Cause: Wrong API endpoint format

```python
# Wrong:
fetch("localhost:8001/api/students")  # Missing http://

# Correct:
fetch("http://localhost:8001/api/students")
```

---

## Quick Recovery Procedures

### Full System Reset (NUCLEAR OPTION)

```bash
# 1. Stop everything
pkill -f uvicorn
pkill -f streamlit
pkill -f "npm run"

# 2. Backup current data (just in case)
cp data/school.db data/school.db.backup.$(date +%s)
cp -r data/chroma data/chroma.backup.$(date +%s)

# 3. Rebuild database
rm data/school.db
python backend/migrations/create_comprehensive_ptcc_schema.py

# 4. Clear ChromaDB
rm -rf data/chroma

# 5. Reinstall dependencies
pip install -r backend/requirements.txt
cd frontend/desktop-web && pip install -r requirements.txt
cd frontend/mobile-pwa && npm install

# 6. Start fresh
./start-ptcc.sh
```

### Partial Recovery

```bash
# Just reset frontend
pkill -f streamlit
cd frontend/desktop-web && streamlit run app.py &

# Just reset backend (keep data)
pkill -f uvicorn
uvicorn backend.main:app --port 8001 &

# Verify
curl http://localhost:8001/health
```

---

## Debugging Tools

### Python Interactive Debugging

```bash
# Start Python in project directory
cd /Users/cantillonpatrick/Desktop/ptcc_standalone
python3

# Then in Python:
from backend.core.database import SessionLocal
from backend.models.database_models import Student

db = SessionLocal()
students = db.query(Student).limit(5).all()
for s in students:
    print(f"{s.name} ({s.class_code})")
db.close()
```

### Database Inspection

```bash
# Query with formatting
sqlite3 data/school.db

# Then:
.mode column
.headers on
SELECT id, name, class_code, support_level FROM students LIMIT 10;

# Count by class
SELECT class_code, COUNT(*) FROM students GROUP BY class_code;

# Find specific student
SELECT * FROM students WHERE name LIKE '%Aisha%';
```

### API Testing

```bash
# Simple request
curl http://localhost:8001/api/students/ | python3 -m json.tool

# With parameters
curl "http://localhost:8001/api/students/?class_code=3A&limit=5"

# POST request
curl -X POST http://localhost:8001/api/students/1/logs \
  -H "Content-Type: application/json" \
  -d '{"log_type":"positive","category":"participation"}'

# View all routes
curl http://localhost:8001/docs
```

### Browser DevTools

```
1. Open Chrome/Safari on frontend
2. Press F12 to open DevTools
3. Check Console tab for errors
4. Check Network tab for API calls:
   - Look for failed requests (red)
   - Check response headers for CORS issues
   - Inspect request/response payloads
5. Check Storage tab for session data
```

---

## Last Resort: Contact Points

When nothing works, check these files for error context:

1. **Backend Errors:**
   ```bash
   cat .ptcc_logs/backend.log | tail -200
   ```

2. **Frontend Errors:**
   ```bash
   # Browser console errors (F12)
   # Or Streamlit logs:
   cat .ptcc_logs/dashboard.log | tail -200
   ```

3. **Database Errors:**
   ```bash
   sqlite3 data/school.db "PRAGMA integrity_check;"
   ```

4. **System Info:**
   ```bash
   python3 --version
   pip list | grep -E "fastapi|streamlit|sqlalchemy"
   lsof -i :8001  # Check port usage
   ```

---

## Prevention Tips

1. **Always backup before major changes:**
   ```bash
   cp data/school.db data/school.db.$(date +%Y%m%d_%H%M%S).backup
   ```

2. **Test in isolation:**
   ```bash
   # Test backend alone
   curl http://localhost:8001/api/students/
   
   # Test frontend connection
   python3 -c "import requests; print(requests.get('http://localhost:8001/health').json())"
   ```

3. **Check logs regularly:**
   ```bash
   tail -f .ptcc_logs/backend.log  # Follow in real-time
   ```

4. **Version control:**
   ```bash
   # Commit working states
   git add -A && git commit -m "Checkpoint: working state before [change]"
   ```
