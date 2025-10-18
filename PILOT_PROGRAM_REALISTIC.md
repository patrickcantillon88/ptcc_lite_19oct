# PTCC Pilot Program: 3-6 Teachers, Minimal Budget

## The Real Scenario
- **Teachers**: 3-6 specialist teachers
- **Students**: ~200-400 across their classes
- **Infrastructure**: School server (hosting data only)
- **API Access**: Google Workspace (already available)
- **Devices**: Teacher laptops + mobile for logging
- **Budget**: Near-zero (system cost), small admin time
- **Timeline**: 2-week setup, 8-week pilot

---

## What This System ACTUALLY Delivers (Realistic)

### 1. Smart Information Layer Over Google Workspace
**What it does:**
- Pulls data from Google Sheets (student lists, support notes)
- Syncs from Google Calendar (lesson schedules, meetings)
- Searches across Google Drive documents (policies, lesson plans)
- **Creates unified interface** - instead of checking 3 different places, one search

**Real example:**
```
Without PTCC:
"Show me students with anxiety support needs"
→ Teacher checks Google Drive folder (4 minutes)
→ Opens 3 different support plan PDFs
→ Manually finds anxiety strategies section
→ Total time: 8-10 minutes

With PTCC:
"Show me students with anxiety support needs"
→ Search returns all matching students + strategies
→ Total time: 10 seconds
```

**This works TODAY with minimal setup:**
- No special software installation needed (web-based)
- Google Sheets API already available
- Just needs API authentication (1 hour admin setup)

---

### 2. Quick Incident Logging During Lessons
**What it does:**
- Teachers log incidents on mobile (30-second workflow)
- Supports positive/negative/neutral with categories
- Works offline, syncs when connected
- Logs saved permanently to school server

**Real workflow:**
```
Monday Period 3:
Teacher notices Sarah showing anxiety
→ Opens PTCC mobile app
→ "Sarah" + "Anxious" + brief note
→ Hit "Log" (10 seconds)
→ Continue teaching

System automatically:
- Records to school database
- Counts toward Sarah's support tracking
- Makes searchable
```

**Time savings:**
- Old way: Mental note, remember later, maybe write down
- New way: Instant logged, automatically tracked
- **Gain**: Always have complete incident history (vs patchy memory)

---

### 3. Unified Student Profile View
**What it does:**
- Shows all logged incidents for any student
- Pulls existing support notes from Google Drive
- Calendar integration (shows lesson times, meetings)
- All in one searchable interface

**Real benefit:**
```
Teacher meeting with parent about Jamie:

Without PTCC:
"Let me check... I think Jamie has had 3 incidents"
→ Takes time to gather notes
→ May miss some details
→ Parent goes home uncertain

With PTCC:
"Let me show you what we've tracked..."
→ Pull up Jamie's profile
→ Show exact dates, incidents, patterns
→ "Last incident was Tuesday when tired"
→ Parent sees systematic approach
```

---

### 4. Search Across All Documents
**What it does:**
- Teachers can search: "What anxiety strategies have we tried with Sarah?"
- Searches uploaded support plans, policies, meeting notes
- Works across all documents in project
- Returns exact locations with context

**Real use:**
```
Teacher preparing differentiation for ADHD student:
"Show me successful strategies from previous lessons"
→ Searches all lesson notes, support plans
→ Finds: "Movement breaks every 15 mins worked well"
→ Immediately useful for next lesson
```

---

### 5. Pattern Identification (Simple)
**What it does:**
- System counts incidents by student
- Flags if one student suddenly increases incidents
- Shows patterns: "Sarah often has incidents Monday mornings"
- No ML required - just counting + trending

**Real alerts:**
```
System notices:
"Jamie has 4 incidents in last 2 days (unusual)"
→ Alert sent to teacher
→ Teacher can intervene early
→ Parent can be involved

Vs old way:
→ Teacher might not notice pattern until crisis
→ No early intervention
```

---

## What You DON'T Get (Don't Need)

❌ AI agents making predictions  
❌ Machine learning models  
❌ Predictive risk scoring  
❌ Complex analytics dashboards  
❌ Expensive integrations  

**These are nice-to-haves AFTER pilot proves value.**

---

## Minimum Infrastructure Setup

### On School Server
```
1. SQLite database file
   - Location: /school-data/ptcc/school.db
   - Size: ~100MB for 400 students + 1 year logs
   - Backup: Automated nightly
   
2. API endpoint
   - Just needs to be accessible to teacher devices
   - Can be: school server, NAS, or even laptop running continuously
   - No special hardware needed
```

### API Configuration (Admin Work)
```
Google Sheets API:
- 1 hour: Enable API in Google Cloud Console
- 5 mins: Generate service account credentials
- 10 mins: Share sheets with service account
- Total: ~1.5 hours one-time setup

Google Drive API:
- 15 mins: Enable Drive API
- 10 mins: Grant folder access
- Total: ~25 mins one-time setup

Google Calendar API:
- 15 mins: Enable Calendar API
- 10 mins: Grant calendar access
- Total: ~25 mins one-time setup
```

**Total admin time: ~3 hours initial setup, then fully automated**

---

## Teacher Requirements

### Per Teacher
```
Hardware:
- 1 Laptop (Windows/Mac/Linux - any OS works)
- 1 Mobile device (iOS or Android)
- WiFi access (works offline too)
- No special software to install (web-based + mobile app)

Training:
- 30-minute overview session
- 15-minute hands-on walkthrough
- Quick reference card (1 page)
- Support person available for questions
- Total per teacher: ~1 hour

Time commitment:
- Adding new student log: 30 seconds during lesson
- Reviewing student profile: 2 minutes when planning
- No additional "data entry" work - just faster access to existing info
```

---

## Real Pilot Outcomes (8 Weeks)

### Week 1-2: Setup Phase
**Tasks:**
- Admin enables Google APIs (3 hours)
- PTCC deployed to school server (2 hours)
- Teacher laptops configured (1 hour per teacher)
- Mobile apps installed (15 mins per teacher)

**Cost:** ~10 hours admin time, £0

---

### Week 3: Training & Familiarization
**What happens:**
- Each teacher gets 1 hour training
- They start using search feature (instant win - faster than Google manually)
- Mobile logging introduced
- Real data from Google Sheets appears in PTCC

**Teacher reaction:**
"Oh, so it's just... everything I'm already using but faster?"
"Yeah, basically."

---

### Week 4-5: Active Logging Begins
**What happens:**
- Teachers start logging incidents daily
- Mobile app usage increases
- First patterns emerge
- Students get profile views updated real-time

**Real benefit:**
- After 2 weeks, each teacher has 20-30 logged incidents
- Search becomes genuinely useful ("find all incidents for Sarah")
- Mobile logging becomes habit (easy workflow)

---

### Week 6-8: Pattern Recognition
**What happens:**
- System has 200-300 logged incidents across 3-6 teachers
- Patterns start showing
- "Sarah always struggles Monday mornings"
- "Jamie's incidents spike after PE"
- "Marcus improves after one-to-one check-ins"

**Real value:**
- Teachers see patterns they didn't notice before
- Can make informed decisions ("avoid assigning anxiety trigger tasks Monday morning")
- Parent meetings have data to show ("We've noticed X pattern, trying Y strategy")

---

## Honest What-You-Achieve List

### ✅ Definitely Achievable in Pilot
- **Unified search** across Google Workspace (saves 5-10 mins per search)
- **Incident logging** (automatic permanent record vs patchy notes)
- **Student profile view** (see all info in one place)
- **Pattern detection** (simple: "Marcus has 5 incidents, Sarah has 2")
- **Mobile logging** (30-second workflow becomes habit)
- **Data export** (show parents/leadership all tracked incidents)
- **Compliance** (complete audit trail for safeguarding)

### 🟡 Partially Achievable (Basic Versions)
- **Risk flagging** (simple: "5+ incidents in a week = flag", no ML)
- **Trend analysis** (show graphs: incidents over time)
- **Comparative reporting** ("This week vs last week")
- **Scheduled alerts** (daily summary email to teachers)

### ❌ NOT Achievable Without Extra Work
- **Predictive AI** (need ML models + historical data)
- **Automated recommendations** (need training data)
- **Complex analytics** (need data science resources)
- **Integration with ClassCharts** (different API, more setup)

---

## Cost Breakdown for 3-6 Teacher Pilot

| Item | Cost | Notes |
|------|------|-------|
| PTCC System | £0 | Free, open-source |
| Server Hosting | £0 | Uses existing school server |
| Google API Setup | £0 | Free tier, school already has |
| Teacher Laptops | £0 | Already have |
| Mobile Devices | £0 | Teachers already have |
| Admin Time | ~£200 | ~10 hours @ £20/hr for setup |
| **Total** | **~£200** | Just admin time |

**Annual costs after pilot:**
- Maintenance: ~4 hours/year = £80
- Backups: £0 (automated to school server)
- Hosting: £0

---

## Timeline for Getting Started

### Week 1: Planning
- [ ] Get headmaster approval (meeting + pitch)
- [ ] Identify 3-6 participating teachers
- [ ] Confirm Google API access available

### Week 2: Technical Setup
- [ ] Admin enables Google APIs (3 hours)
- [ ] Deploy PTCC to school server (2 hours)
- [ ] Test with sample data (1 hour)

### Week 3: Teacher Onboarding
- [ ] 1-hour training per teacher (6 hours for 6 teachers)
- [ ] Install mobile apps (30 mins per teacher)
- [ ] Test logging workflow

### Week 4-11: Active Pilot
- [ ] Daily usage by teachers
- [ ] Weekly check-ins (15 mins each)
- [ ] Collect feedback
- [ ] Make small improvements

### Week 12: Evaluation
- [ ] Measure: incidents logged, searches performed, time saved
- [ ] Teacher feedback
- [ ] Decision: expand or end pilot

---

## Key Messaging for Getting Approval

### For Head Office
**Problem we're solving:**
- Teachers manually searching multiple systems for student info
- No consistent incident tracking
- Difficulty spotting patterns in student behavior
- Safeguarding records scattered

**Our solution:**
- Unified search across existing Google Workspace
- Automatic incident logging and tracking
- Pattern identification for early intervention
- Complete audit trail for compliance

**Why this pilot:**
- Minimal cost (just admin time)
- Uses existing systems (Google Workspace)
- Data stays on school server (privacy intact)
- 3-6 teachers = manageable scope
- 8 weeks = quick proof of concept

**What we ask:**
- 1-2 hours admin time to set up Google APIs
- 3-6 willing teacher volunteers
- Evaluation meeting at end of pilot

### For Teachers
**What you get:**
- Faster access to student information (5-10 min savings per day)
- Automatic incident tracking (never forget details again)
- Mobile app for quick logging (30-second workflow)
- Complete student profiles in one place
- Data to support parent meetings

**What you have to do:**
- 1-hour training session
- Log incidents on mobile (~1 minute per day extra)
- 15-min weekly check-in with team
- Give feedback on what's working

**What you DON'T have to do:**
- Enter data manually (pulls from Google automatically)
- Learn new complex software (web-based, simple)
- Worry about security (data stays on school server)

---

## Success Metrics for Pilot

### Quantitative (Measure)
- **Incidents logged**: Target 200+ total by week 8
- **Mobile loggings**: Target 50%+ of daily logs via mobile
- **Search usage**: Track searches per week
- **Time saved**: Survey teachers weekly ("How much time saved?")

### Qualitative (Feedback)
- **Ease of use**: "Would you use this regularly?"
- **Value delivered**: "Did this help you understand students better?"
- **Information quality**: "Is the tracked data useful?"
- **Adoption**: "Are you using it daily?"

### Safeguarding
- **Incident tracking**: Complete record for any student
- **Pattern detection**: Any concerning trends identified?
- **Early intervention**: Incidents flagged quickly?

---

## Most Likely Blockers & Solutions

| Blocker | Solution | Time |
|---------|----------|------|
| Admin won't enable Google APIs | Show that it's free, takes 1 hour, uses existing systems | Demo |
| Teachers say "too complicated" | They haven't used it - show 30-second mobile logging | 10 mins |
| "We're already using Google Sheets" | Exactly - we just make it searchable + add mobile logging | 5 mins |
| Concern about data security | Data stays on school server, not cloud - more secure | 5 mins |
| "Do we need new hardware?" | No - uses existing laptops + phones teachers already have | 1 min |
| "Will this take extra time?" | Incident logging takes same time whether digital or paper | 5 mins |

---

## What Winning Looks Like After 8 Weeks

**Teachers are saying:**
- "I actually use this every day"
- "It's so much faster than digging through files"
- "I can finally remember all the details for parent meetings"
- "The pattern about Monday mornings was really helpful"

**Metrics show:**
- 250+ incidents logged
- 100+ searches performed
- Average 3 searches per teacher per week
- 60%+ of logging via mobile app
- Teachers report 5-10 minutes saved per week

**Leadership sees:**
- Complete safeguarding audit trail
- Data-driven insights about student patterns
- Teachers more engaged and informed
- System working well on school infrastructure

**Decision point:**
"This is working. Can we expand to more teachers?"

---

## Post-Pilot Options

### If Successful (Most Likely)
1. Expand to 15-20 teachers
2. Add ClassCharts integration (separate setup)
3. Build out dashboards for leadership
4. Implement simple ML-based alerts

### If Needs Improvement
1. Address teacher feedback
2. Improve mobile UX based on usage patterns
3. Optimize search performance
4. Rerun pilot with adjustments

### If Not Working
1. Honest debrief about why
2. Adjust approach
3. Try different scope or user group
4. Kill gracefully without blame

---

## Bottom Line

**This pilot costs almost nothing** (just admin time).

**It delivers real value immediately:**
- Faster information access
- Automatic incident tracking
- Pattern spotting for early intervention
- Complete safeguarding records

**It uses existing systems** (Google Workspace).

**It's low-risk** (can be turned off if needed).

**It proves the concept** before any significant investment.

---

## Action Items (Next Step)

1. **Schedule 30-min meeting** with headmaster
   - Show this document
   - Pitch as "low-risk pilot with existing systems"
   - Ask for 3-6 teacher volunteers + 1 hour admin time

2. **If approved**: Start technical setup immediately
   - Week 1-2: Admin API configuration
   - Week 3: Teacher training
   - Week 4-11: Active usage
   - Week 12: Evaluation

3. **If rejected**: Key points to address
   - Cost concern? (It's ~£200 for 8 weeks)
   - Data concern? (Stays on school server)
   - Time concern? (Saves teachers time overall)
   - Integration concern? (Uses existing Google Workspace)

---

**This is the realistic, achievable pilot. Not sexy, not revolutionary - just practical, valuable, low-cost. 🎯**