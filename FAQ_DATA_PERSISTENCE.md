# PTCC Data & Integration FAQ

## Data Storage & Persistence

### Q: Where is my incident data stored when I log it?

**A:** Your incident data is stored in a **SQLite database file** located at `/data/school.db` on your server's hard drive.

When you log an incident (e.g., "Alice was disruptive"), this data is saved to a table called `quick_logs`. Think of this like a permanent filing cabinet—once data is filed away, it stays there until you explicitly delete it. The data includes:
- Which student had the incident
- What time it happened
- The type of incident (positive, negative, neutral)
- The category (disruptive, excellent contribution, etc.)
- Any notes you added
- Strike level (for behavior management)
- Consequences assigned

**Why this matters:** This is real, persistent storage. It's not temporary or fleeting.

---

### Q: When I close the app or restart the server, does my data get wiped?

**A:** **No, your data is completely safe.** This is one of the most important features of PTCC.

Here's what happens:

**When you close the app:**
1. The application connection to the database closes
2. BUT the database file (`school.db`) remains on your hard drive
3. Your data is exactly as you left it

**When you restart the app:**
1. The app reconnects to the same `school.db` file
2. All your historical data loads automatically
3. You see everything you've ever logged—from day one

**Real-world example:**
- Monday: You log 5 incidents for Alice
- Tuesday morning: The server restarts (power outage, system update, etc.)
- Tuesday afternoon: You log in and Alice still has 5 incidents in the system
- The data was never lost

**What this means:** You could restart the app 100 times and every single incident you've logged will still be there.

---

### Q: What data is lost when the app closes?

**A:** Only temporary, session-based information is lost. **Your actual data remains.**

**Lost on restart (temporary):**
- Who's currently logged in
- Your screen position (scroll location)
- Which tab you had open
- In-memory cache calculations
- Unsaved browser state

**Kept on restart (permanent):**
- ✅ Every incident you logged
- ✅ Strike levels and consequences
- ✅ Student profiles and support levels
- ✅ Risk assessments
- ✅ All historical data
- ✅ Everything in the database

Think of it like closing a filing cabinet and reopening it the next day—your files are still organized inside exactly as you left them.

---

## Real-Time Integration with Other Tools

### Q: If I log an incident in Lesson Console, does it automatically update Behaviour Management and Risk Tools?

**A:** **Yes, absolutely.** This is automatic and happens in real-time.

Here's the complete journey of an incident:

**Step 1: You log the incident**
- You're in Lesson Console during class
- You see Alice is disruptive
- You click "Log Incident" and add a note

**Step 2: PTCC backend receives it**
- Your log goes to the PTCC backend API
- The system validates the data (checks that the student exists, etc.)
- Data is immediately saved to the database

**Step 3: Risk assessment is updated**
- PTCC counts how many incidents Alice has had recently
- If it's her 2nd negative incident, the system marks her as at-risk
- Her support level increases automatically
- Any staff member viewing "At-Risk Students" now sees Alice flagged

**Step 4: External tools are notified**
- PTCC automatically sends a message to your Behaviour Management tool
- It includes: student name, incident type, strike level, timestamp, and notes
- Your Behaviour Management system now has this incident recorded
- It can trigger automatic consequences (detention, parent contact, etc.)

**Step 5: Search system is updated**
- The incident is added to the RAG (search) system
- If you later search "students with disruptive incidents," Alice appears in results
- Search is instantly updated with the new data

**Timeline:** This all happens in about 1-2 seconds from the moment you log the incident.

**Real-world scenario:**
- 14:05: You log "Alice was disruptive"
- 14:05:30: Risk system flags her as at-risk
- 14:05:45: Admin gets notification that Alice reached 2nd strike
- 14:06: Parent portal in Behaviour Management shows new incident
- 14:06:15: Search now returns Alice when you search for "disruptive incidents"

---

### Q: If the Behaviour Management tool logs an incident, does PTCC see it?

**A:** **Yes, it works both ways.** This is called "bidirectional integration."

Here's how external tools can push data back to PTCC:

**If another system logs an incident:**
1. Your Behaviour Management tool or ClassCharts logs an incident for a student
2. That system sends a webhook (automatic message) to PTCC
3. PTCC receives the data and validates it
4. PTCC creates a record in its `quick_logs` table
5. The incident now appears in PTCC as if you logged it manually

**What this enables:**
- If admin logs an incident in one system, PTCC sees it
- If a different teacher logs it in ClassCharts, PTCC knows about it
- All systems stay in sync automatically
- You never miss data entered in other places

**Real-world example:**
- PE teacher logs incident in Behaviour Management tool: "Alice argumentative in class"
- You don't log it separately—the system handles it
- Next morning, you open PTCC and see Alice has 3 incidents total (including PE teacher's)
- No manual double-entry needed

---

## Data Synchronization & System Integration

### Q: How do I know if data synced correctly between systems?

**A:** PTCC logs every sync operation and tracks success/failure.

When you log an incident, the system records:
- **What was sent:** Student ID, incident type, timestamp, notes
- **Where it was sent:** Risk tool, Behaviour Management, RAG index
- **Success or failure:** Did each system receive it?
- **Timestamp:** Exactly when it happened

You can view this audit trail in the admin dashboard to verify everything synced correctly.

**If something fails:**
- PTCC won't crash or lose data
- The incident is saved to the database (safe)
- Admin gets an alert that external sync failed
- You can retry or investigate why the external tool didn't receive it

---

### Q: What happens if the Behaviour Management tool is down? Will my PTCC data be lost?

**A:** **No, your PTCC data is completely safe.**

Here's what happens:

**If external tool is unavailable:**
1. You log an incident in PTCC
2. PTCC saves it to its database (✅ safe)
3. PTCC tries to send it to Behaviour Management tool
4. Behaviour Management is down (unreachable)
5. PTCC logs the failure
6. Admin gets an alert
7. Your data in PTCC stays intact ✅

**The incident is not lost.** It's saved locally. Once the external tool comes back online, PTCC can retry sending it, or admin can manually sync.

**Key principle:** PTCC never sacrifices local data for external systems. If external tools are unavailable, PTCC continues working normally.

---

## Multi-User & Teacher Independence

### Q: If one teacher uses PTCC and another uses just Google Sheets, can their data sync?

**A:** **Yes, this is one of PTCC's strengths.**

**Teacher A (using PTCC):**
- Logs incidents in PTCC Lesson Console
- Data saved to database
- Automatically synced to Behaviour Management

**Teacher B (using Google Sheets):**
- Maintains student data in Google Sheets
- Every 6 hours, PTCC syncs that data automatically
- Incidents appear in PTCC as if logged in the system

**What happens:**
- Teacher A's PTCC data and Teacher B's Google Sheets data merge into one unified view
- When you search "at-risk students," you see incidents from both sources
- When you log an incident, it's available to both teachers

**No manual data entry needed.** The system handles bringing all sources together.

---

## Risk Assessment & Automated Flagging

### Q: How does PTCC know a student is at-risk?

**A:** PTCC automatically analyzes incident patterns and updates risk levels.

**The system works like this:**

1. **Tracks incidents:** Every negative incident is logged with a timestamp
2. **Counts recent incidents:** "How many negative incidents in the past 7 days?"
3. **Sets strike level:** 
   - 1st-2nd incident = Strike 1 (Warning)
   - 3rd-4th incident = Strike 2 (Admin notified)
   - 5th+ incident = Strike 3 (HOD consultation)
4. **Updates support level:** If strikes increase, the student's support level rises
5. **Flags as at-risk:** If support level reaches 3+, student appears in "At-Risk" view
6. **Alerts staff:** Relevant staff members get notified

**Real example:**
- Monday: Alice logs in 1 negative incident (Strike 1)
- Tuesday: Alice logs in 2 more negative incidents (Strike 2 - Admin notified)
- Wednesday: Admin reviews, updates support level, flags for intervention
- Thursday: You open PTCC and immediately see Alice highlighted as at-risk
- The system did all this automatically based on the data

---

## Search & Historical Data

### Q: Once data is logged, how do I find it later?

**A:** PTCC indexes all data in a searchable system (RAG - Retrieval-Augmented Generation).

You can search using natural language:
- "Show me all disruptive incidents this week"
- "Which students have 3+ incidents?"
- "Students in Year 7 with support needs"
- "Positive feedback logged in PE"

**How it works:**
1. Each incident is converted into searchable text
2. Text is indexed in ChromaDB (a search database)
3. You search using teacher language (not technical queries)
4. Results appear instantly with source and context

**Storage location:** Search index is stored in `/data/chroma/` on disk (also persistent).

---

## Data Backup & Safety

### Q: What if the database file gets corrupted or deleted?

**A:** This is why regular backups are critical.

**Protection you should have:**
- Daily automated backups of `school.db`
- Backups stored in a separate location
- Version history for recovery

**If corruption happens:**
1. PTCC can't start (database is unreadable)
2. Restore from backup
3. Lose only data from the last backup interval (e.g., last 24 hours)
4. All backup data is restored

**Prevention:**
- Backup daily to secure location
- Test restores monthly
- Monitor database health alerts
- Use server-level backup solutions

---

## Summary: The Bottom Line

| Question | Answer | Why It Matters |
|----------|--------|------------------|
| Is my data safe if I close the app? | ✅ Yes, completely | You can restart anytime without worry |
| Does data disappear on server restart? | ❌ No, it stays | Data is permanent on disk |
| Do I need to re-enter data each session? | ❌ No, ever | Historical data loads automatically |
| Does PTCC integrate with other tools? | ✅ Yes, automatically | No manual data entry between systems |
| Can other tools push data to PTCC? | ✅ Yes, via webhook | All sources stay synchronized |
| What if external tool is down? | ✅ PTCC works normally | Local data never depends on external systems |
| Can I find past incidents easily? | ✅ Yes, searchable | All data indexed and instantly findable |
| Is there a backup system? | Should be configured | Essential for disaster recovery |

---

## Questions About Your Specific Scenario

### "Teacher A uses Behaviour Management tool, Teacher B uses PTCC—are they in sync?"

**Yes.** Teacher A's incidents entered in Behaviour Management are automatically sent to PTCC via webhook. Teacher B sees them in PTCC. Both teachers see unified data.

### "I logged 50 incidents yesterday—will they still be there tomorrow?"

**Yes.** Every incident is permanent in the database. All 50 will load when you restart.

### "If I mark a student as at-risk, does that update everywhere?"

**Yes.** The risk flag is updated in the database, automatically synced to external tools, and searchable in PTCC. All systems reflect the change.

### "Can I restore data from a specific date if something goes wrong?"

**Yes, if backups exist.** Restore from your most recent backup before the problem occurred.

This is what production-ready data architecture looks like: **persistent, synchronized, searchable, and resilient.** 🎯