# PTCC Data Collection Strategy - Production Implementation

## Problem Statement
Manual PDF uploads don't scale. Need automatic data collection from existing school systems to populate:
- Daily briefings
- Meeting notes
- Policy documents
- Behavioral logs
- Assessment data

## Recommended Solution: Multi-Source Automated Collection

### 1. Email Integration (Daily Briefings)
**Source:** Staff emails containing briefings, announcements, updates

**Implementation:**
```python
# Pseudo-code
scheduler.daily(9:00 AM):
    - Connect to school email (Gmail/Office365)
    - Search for emails in "Briefings" folder from last 24h
    - Extract subject, body, attachments
    - Parse for key information (dates, student names, actions)
    - Store in database with source tracking
    - Index in ChromaDB
```

**Data captured:**
- Daily briefing content
- Action items
- Important dates
- Staff announcements

**Setup effort:** 2-3 hours (IMAP setup + credential management)

---

### 2. Google Drive Monitoring (Collaborative Docs)
**Source:** Shared folders for meeting notes, planning documents, policies

**Implementation:**
```python
scheduler.every(6 hours):
    - List files in designated Google Drive folders
    - Check for changes since last scan
    - Download modified documents
    - Extract text (Google Docs → PDF → text)
    - Update database with new version
    - Update ChromaDB embeddings
    - Track document versions
```

**Data captured:**
- Meeting notes
- Lesson plans
- Policy documents
- Planning documents
- Collaborative decisions

**Setup effort:** 3-4 hours (Google API setup + folder permissions)

---

### 3. Calendar Integration (Meeting Context)
**Source:** School calendar for meetings, assemblies, events

**Implementation:**
```python
scheduler.daily(after school):
    - Query calendar API for day's events
    - Extract event descriptions and attendees
    - Link to participants (teachers, year groups)
    - Create context for briefing
    - Store timeline of school events
```

**Data captured:**
- Important meetings
- School events
- Staff development days
- Assembly dates/topics

**Setup effort:** 1-2 hours (Calendar API setup)

---

### 4. Behavioral Data Integration (If available)
**Source:** ClassCharts or similar SIS behavior logging

**Implementation:**
```python
scheduler.every(2 hours):
    - Connect to ClassCharts API (if available)
    - Query for recent behavior incidents
    - Extract student name, incident type, notes
    - Map to internal student database
    - Store in QuickLog table
    - Update student profiles
```

**Data captured:**
- Behavioral incidents (real-time)
- Reward points
- Detentions
- Pastoral notes

**Setup effort:** 2-3 hours (API integration + student mapping)

---

## Architecture for Automated Collection

```
┌─────────────────────────────────────────────────┐
│         Data Sources                             │
├────────────┬──────────────┬──────────┬───────────┤
│   Email    │ Google Drive │ Calendar │ ClassCharts
└────────────┴──────────────┴──────────┴───────────┘
             │              │         │      │
             └──────────────┼─────────┴──────┘
                            ↓
                  Async Task Scheduler
                    (APScheduler)
                            ↓
            ┌───────────────────────────────┐
            │  Extraction/Parsing Layer     │
            │  - Text extraction           │
            │  - Metadata parsing          │
            │  - Student/staff mapping     │
            └───────────────────────────────┘
                            ↓
            ┌───────────────────────────────┐
            │  Data Storage Layer           │
            │  - SQL (permanent records)    │
            │  - ChromaDB (embeddings)      │
            │  - Version tracking          │
            └───────────────────────────────┘
```

---

## Implementation Priority

### Phase 1 (Week 1) - Email Integration
- Set up Gmail/Office365 connection
- Parse daily briefing emails
- Store briefing text in database
- Index in ChromaDB

**Effort:** 4-6 hours  
**Impact:** Eliminates manual briefing entry

### Phase 2 (Week 2) - Google Drive Monitoring
- Set up Google Drive API
- Monitor designated folders
- Extract and store documents
- Full-text search capability

**Effort:** 6-8 hours  
**Impact:** Captures collaborative knowledge automatically

### Phase 3 (Week 3) - Calendar Integration
- Connect to school calendar
- Extract event details
- Link to briefings/context

**Effort:** 3-4 hours  
**Impact:** Contextual event reminders

### Phase 4 (Week 4+) - Behavioral Data
- Integrate with ClassCharts (if available)
- Real-time incident logging
- Student profile updates

**Effort:** 4-6 hours  
**Impact:** Automatic behavioral tracking

---

## Key Considerations

### Privacy & Security
- ✅ All data remains on-premise (local SQLite)
- ✅ No external cloud storage of student data
- ✅ Audit logging of all data access
- ✅ Role-based access controls
- ⚠️ Need secure credential storage for API keys

### Data Freshness
- Email: Daily (9 AM scheduled)
- Drive: Every 6 hours (automated)
- Calendar: Daily
- Behavioral: Every 2 hours (if available)

### Error Handling
- Retry failed connections (3 attempts, exponential backoff)
- Alert admins on collection failures
- Log all errors for debugging
- Graceful degradation (system works even if some sources fail)

### Credential Management
```python
# Use environment variables for sensitive credentials
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")  # App-specific password
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CLASSCHARTS_TOKEN = os.getenv("CLASSCHARTS_TOKEN")
```

---

## Database Schema Addition

```sql
-- Track data source and freshness
CREATE TABLE data_source_metadata (
    id INTEGER PRIMARY KEY,
    source_type VARCHAR(50),  -- 'email', 'gdrive', 'calendar', 'classcharts'
    last_sync DATETIME,
    next_sync DATETIME,
    status VARCHAR(20),  -- 'success', 'failed', 'pending'
    error_message TEXT,
    records_synced INTEGER,
    sync_duration FLOAT
);

-- Track document versions for collaborative docs
CREATE TABLE document_versions (
    id INTEGER PRIMARY KEY,
    document_id INTEGER,
    version_number INTEGER,
    modified_date DATETIME,
    modified_by VARCHAR(255),
    content TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
```

---

## Next Steps

1. **Define which data sources are available** in your school
2. **Prioritize by impact** (briefings first, usually highest ROI)
3. **Set up API credentials** for chosen sources
4. **Implement Phase 1** (email) as proof of concept
5. **Test with small dataset** before full rollout
6. **Monitor sync quality** and adjust parsing logic

This transforms PTCC from manual-upload to **truly automated knowledge management system**.