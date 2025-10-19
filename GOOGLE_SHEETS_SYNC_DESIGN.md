# Google Sheets Sync Design - PTCC Multi-User Scenario

## The Scenario

- **Mr P**: Maintains student data in Google Sheet (source of truth)
- **Mr A**: Uses PTCC for analysis and decision-making
- **Question**: How do their workflows interact?

---

## Answer to Your Questions

### Question 1: Does Mr P's data automatically reach Mr A's RAG system?

**YES ✅**

```
Mr P enters data in Google Sheet
        ↓
Scheduled job detects changes (every 6 hours)
        ↓
Data synced to PTCC SQL database
        ↓
Data re-indexed in ChromaDB
        ↓
Mr A's RAG searches include Mr P's data
        ↓
Risk analysis includes latest information
```

**Timeline:**
- Mr P updates sheet: 9:00 AM
- Next sync: 3:00 PM (6-hour interval)
- Mr A's search: Includes Mr P's data ✅

**Benefit:** Mr A doesn't need to ask "Is this still current?" - system is always in sync

---

### Question 2: Do Mr A's changes go back to Mr P's sheet?

**NO ❌ (By Design)**

**Why?** Because we want to respect Mr P's workflow choice:
- Mr P chose Google Sheets
- Mr A chose PTCC
- They shouldn't interfere with each other's tools

**Current Design:**
```
Mr P's Sheet ──(read-only sync)──→ PTCC Database
Mr A's PTCC Updates ──(stay in)──→ PTCC Only
```

**Mr A's analysis lives in PTCC:**
- Risk alerts
- Pattern analysis
- Quick logs
- Follow-up notes

**Mr P sees summaries (optional export):**
- Can export PTCC insights as spreadsheet
- Can import summaries back to sheet if needed
- But not automatic two-way sync

---

## Architecture

### Data Flow Diagram

```
┌──────────────────┐
│   Mr P's Sheet   │
│  (Student Data)  │
└────────┬─────────┘
         │
         │ (1) Scheduled sync
         │     every 6 hours
         │
         ↓
    ┌─────────────────┐
    │  Google Sheets  │
    │  API             │
    │  (Read-Only)    │
    └────────┬────────┘
             │
             ↓
    ┌──────────────────┐
    │   Sync Handler   │
    │  - Fetch rows    │
    │  - Parse data    │
    │  - Check changes │
    └────────┬─────────┘
             │
             ↓
    ┌──────────────────┐
    │  PTCC Database   │
    │  - Update/Create │
    │  - Log changes   │
    └────────┬─────────┘
             │
             ↓
    ┌──────────────────┐
    │  ChromaDB        │
    │  - Re-index      │
    │  - Update vectors│
    └────────┬─────────┘
             │
             ↓
    ┌──────────────────┐
    │   Mr A's RAG     │
    │   - Searches now │
    │     include new  │
    │     data         │
    └──────────────────┘
```

---

## Implementation

### Schedule the sync (in FastAPI lifespan)

```python
# backend/main.py

from apscheduler.schedulers.background import BackgroundScheduler
from backend.integrations.google_sheets_sync import sync_google_sheet_handler

scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    # Sync Google Sheet every 6 hours
    scheduler.add_job(
        sync_google_sheet_handler,
        "interval",
        hours=6,
        id="google_sheets_sync",
        name="Sync Google Sheets to PTCC"
    )
    scheduler.start()
    logger.info("Google Sheets sync scheduler started")

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()
```

### Environment variables needed

```bash
# .env

# Google Sheets API credentials (service account)
GOOGLE_TYPE=service_account
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY_ID=xxx
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
GOOGLE_CLIENT_EMAIL=ptcc-sync@project.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=xxx
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token

# PTCC Google Sheets config
GOOGLE_SHEET_ID=1BxiMVs0XRA5nFMKtqontzfqWQmxvAgqDZNYUq3Xw-Jc
GOOGLE_SHEET_NAME=Students
```

### Google Sheet format (expected columns)

| name | class_code | year_group | campus | support_level | support_notes |
|------|-----------|-----------|--------|---------------|---------------|
| Alice Johnson | 3A | 3 | Campus A | 2 | Anxiety support needed |
| Bob Smith | 3A | 3 | Campus A | 1 | No additional support |
| Charlie Brown | 4B | 4 | Campus B | 3 | EHCP review scheduled |

---

## Sync Metadata Tracking

The system logs every sync:

```sql
-- What gets tracked
source_type: "google_sheets"
last_sync: 2025-10-18 15:00:00
status: "success" / "partial" / "failed"
records_synced: 45
error_message: "3 rows failed validation"
```

**This lets you:**
- See when data was last updated
- Debug why specific imports failed
- Monitor sync health
- Audit data lineage

---

## Advanced Option: Two-Way Sync (If Needed Later)

If you want Mr A's changes to go back to Mr P's sheet:

```python
# When Mr A updates a student in PTCC:
1. Save to PTCC database
2. Find corresponding row in Google Sheet
3. Update that row
4. Log: "Updated by Mr A at 14:30"
```

**But with conflict resolution:**
```
If Mr P and Mr A edit same student at same time:
    - PTCC detects conflict
    - Merges if possible
    - Alerts admin if unclear
    - Last-write-wins as fallback
```

**Recommendation:** Start with one-way (current), add two-way later if needed.

---

## Benefits of This Approach

✅ **Mr P continues using sheets** - No forced migration  
✅ **Mr A gets fresh data** - Automatic sync every 6 hours  
✅ **No conflicts** - One-way sync is simple and reliable  
✅ **Auditable** - Every change is logged  
✅ **Scalable** - Works with Mr P, Mr A, Mr B, Mr C...  
✅ **Privacy preserved** - Data stays on-premise

---

## Next Steps

1. **Set up Google Sheets API credentials** (service account)
2. **Create Google Sheet** with student data template
3. **Configure .env variables** with sheet ID and credentials
4. **Deploy scheduler** to sync every 6 hours
5. **Test with 5 students** to verify data flows correctly
6. **Monitor syncs** for 1 week to ensure reliability
7. **Gradually migrate** existing data to Google Sheet

**Time to implement:** 4-6 hours

This design scales from 2 teachers to 50+ teachers, each using their preferred tool while staying synchronized through PTCC.