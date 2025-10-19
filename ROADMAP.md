# PTCC - Product Roadmap
**Date: October 19, 2024**

## Status: BIFURCATED DEVELOPMENT

As of October 19, 2024, PTCC development splits into two distinct paths:

### Path 1: PTCC Full (Frozen Archive)
- **Status:** Frozen, archived, reference-only
- **Purpose:** Proof-of-concept, commercial template, learning artifact
- **No new development** unless unfreezing decision is made

### Path 2: PTCC Lite (Active Development)
- **Status:** Launching for real-world testing
- **Purpose:** Practical tool for specialist teachers
- **See: ptcc_lite_19oct repository for active roadmap**

---

## PTCC Full - Future Potential (If Unfrozen)

### Phase 1: Foundation Stabilization (Months 3-4)

**Goals:**
- Real data integration (replace all mock data)
- API access to school systems (SIMS, ClassCharts, Google Classroom)
- Proven user feedback from PTCC Lite

**Work:**
- SIMS API integration layer
- Google Classroom sync
- ClassCharts behavioral data import
- Replace mock data with real school data
- Load testing with real dataset volumes

**Success Criteria:**
- Zero mock data in production
- Sync reliability >99%
- <500ms API response time under load

---

### Phase 2: Simplified Agent Framework (Months 4-6)

**Goals:**
- Simplify multi-agent orchestration based on PTCC Lite learnings
- Focus on 1-2 proven use cases instead of 5+

**Work:**
- Remove unused agent types
- Keep only: at-risk detection, behavior pattern analysis
- Simplify agent communication (no complex orchestration)
- Add human-in-the-loop validation (teacher approval before action)

**Success Criteria:**
- <3 agents active
- <2 seconds per agent analysis
- User survey: "Helpful" vs. "Confusing" ratio >2:1

---

### Phase 3: Multi-User & Scalability (Months 6-9)

**Goals:**
- Support multiple teachers in same school
- Multi-school deployment capability

**Work:**
- User management & authentication (currently designed, not deployed)
- Role-based access control (teacher vs. admin vs. leadership)
- Data isolation (each teacher's data stays private)
- School-level configuration & customization
- Performance optimization for 100+ teachers

**Success Criteria:**
- 3+ schools using PTCC Full
- <1 second response time across all endpoints
- Zero data leakage between users

---

### Phase 4: Advanced Intelligence (Months 9-12)

**Goals:**
- Predictive insights (not just reactive analysis)
- Personalized intervention recommendations

**Work:**
- Predictive modeling for student risk (long-term)
- Personalized learning path generation
- Automated intervention suggestions
- Teacher performance analytics (controversial, optional)

**Success Criteria:**
- Predictive model accuracy >75%
- Teachers act on 40%+ of recommendations
- Measurable student outcome improvement

---

### Phase 5: Ecosystem Integration (Months 12+)

**Goals:**
- Connect to parent communication platforms
- Integrate with LMS (Google Classroom, ClassCharts, Tapestry)
- Third-party app marketplace

**Work:**
- Guardian communication APIs (email parents from PTCC)
- LMS event webhooks (automated data sync)
- Plugin system for third-party apps
- Mobile app (iOS/Android native)

**Success Criteria:**
- 5+ external integrations working
- Mobile app download >1000
- API third-parties building on top

---

## PTCC Lite - Active Roadmap

### Version 1 (October 19 - October 25)

**Must-Have:**
- Photo roster with student names + ability data
- Quick incident logging (one-tap capture)
- Weekly pattern summary
- Pre-lesson briefing

**Nice-to-Have:**
- RAG search over LS docs
- House points tracking
- Mobile-friendly UI

**Success:** Teacher using it in every lesson

---

### Version 2 (October 26 - November 8)

**Based on V1 Feedback:**
- Adjust UI/UX based on usage patterns
- Add most-requested feature from teacher feedback
- Improve pattern recognition
- Mobile app or PWA

**Success:** Usage frequency increasing, teacher reports reduced cognitive load

---

### Version 3+ (November+)

**TBD Based on:** Real usage data from PTCC Lite

---

## Decision Framework: When to Unfreeze PTCC Full

**Unfreeze when:**
1. ✅ PTCC Lite has been used daily for 4+ weeks
2. ✅ Real feedback shows specific need for advanced features (not hypothetical)
3. ✅ Have API access to school systems (or realistic path to it)
4. ✅ Have budget/time for 3+ month development cycle
5. ✅ Have 3+ teachers willing to test enterprise version

**Don't unfreeze if:**
- ❌ PTCC Lite is solving the problem well (no need)
- ❌ No new constraints have changed (PTCC Lite remains better fit)
- ❌ Competing priorities demand attention
- ❌ Unclear market demand (just because it's possible, not because it's needed)

---

## Commercial Vision (For PTCC Full, If Launched)

### Target Customer: Multi-School Networks

**Size:** 5-20 schools, 30-100 teachers

**Problem Solved:**
- Unified view across multiple campuses (not just within one school)
- Consistent behavior/safeguarding management across schools
- Central analytics for school leadership
- Evidence-based decisions for teacher support

**Pricing Model (Hypothetical):**
- Per-school: $500-2,000/month
- Per-teacher: $50-100/month
- Per-region (entire network): Custom pricing

**Sales Pitch:**
"PTCC Full is what's possible when you unify fragmented education data. PTCC Lite is what works today with your existing constraints. Start with Lite, scale to Full when ready."

---

## Known Challenges & Mitigation

### Challenge 1: API Access Barriers
**Problem:** Can't access SIMS, Google Classroom, ClassCharts APIs

**Mitigation:**
- Start with available data sources (PDFs, CSVs, manual input)
- Advocate for API access with school leadership
- Build import/export for common formats
- Partner with education software companies for data sharing

### Challenge 2: Data Quality
**Problem:** School systems have inconsistent, incomplete, or conflicting data

**Mitigation:**
- Data validation & cleaning layers
- User override capability (teacher sees flagged inconsistency, corrects it)
- Data lineage tracking (know where each data point came from)
- Manual audit trails for sensitive decisions

### Challenge 3: Privacy & Safeguarding
**Problem:** Managing sensitive student data, compliance with regulations

**Mitigation:**
- Local-first architecture (data stays on school network)
- Encryption at rest and in transit
- Access controls (who can see what)
- Audit logs (every access is tracked)
- GDPR-compliant data deletion

### Challenge 4: Adoption & Change Management
**Problem:** Teachers already overwhelmed, resistant to new tools

**Mitigation:**
- Start with solving ONE problem (incident logging, not everything)
- Minimal friction UI (one-tap, not multi-step)
- Regular feedback loops (iterate based on teacher input)
- Training & support (not just software, but adoption help)

### Challenge 5: Scalability
**Problem:** Works for one teacher, unclear if it scales to 100+ teachers

**Mitigation:**
- Early load testing (don't wait for production failure)
- Horizontal scaling architecture (add servers as needed)
- Efficient data queries (indexed, cached, optimized)
- Monitor performance from day one

---

## Experimental Features (Low Priority)

### If You Have Extra Time:

**1. AI-Powered Writing Assistant**
- Help teacher write reports faster
- Templates + AI completion
- Student quote auto-capture
- Status: Nice-to-have, not core

**2. Parent Communication Portal**
- Send updates to parents directly from PTCC
- Privacy-preserving (only share relevant info)
- Status: Future integration, not core

**3. Behavior Analytics Dashboard**
- Heat maps of behavior hotspots (time, location, student combo)
- Predictive behavior alerts
- Status: Research phase, not production

**4. LLM-Powered Student Summaries**
- Auto-generate student reports from incident logs
- Extract key patterns and recommendations
- Status: Future, once data is clean

**5. Peer Benchmarking**
- "How does my class compare to other classes?"
- Anonymized, aggregated, privacy-safe
- Status: Research phase, not core

---

## Success Metrics

### For PTCC Lite:
- Teacher uses it 5+ times per day
- Reduces time spent finding student information by 50%
- Reduces cognitive load (teacher reports)
- Weekly usage pattern stable (not novelty effect)

### For PTCC Full (If Unfrozen):
- 3+ schools actively using it
- API integration reliability >99%
- Average teacher reduces prep time by 30%
- School leadership makes 20% better decisions (measurable outcome)
- Net Promoter Score (NPS) >60

---

## Contingency Plans

### If PTCC Lite Fails:
1. Review why it failed (too complex? doesn't solve real problem? wrong audience?)
2. Return to brain dump and validate problem statement
3. Either pivot or abandon project

### If API Access Never Materializes:
1. PTCC Lite becomes permanent version
2. Optimize for accessible data sources only
3. Build integrations creatively (webhook listeners, SFTP imports, etc.)

### If Teacher Adoption Stalls:
1. Gather qualitative feedback (why not using it?)
2. Iterate on UI/UX
3. May need different approach (paper-based hybrid? different tool entirely?)

### If Multiple Teachers Want to Use It:
1. Multi-user architecture becomes essential (currently single-user local)
2. Accelerate Phase 3 (scalability work)
3. May need cloud deployment instead of local

---

## Long-Term Vision (Year 2+)

**Ideal Outcome:**
PTCC becomes the "operating system for specialist teachers"—the single place where:
- Fragmented data gets unified
- Patterns become visible
- Decisions get easier
- Teaching gets better

Not through AI magic, but through **practical data architecture** + **interface design** + **institutional memory**.

**The Real Win:**
A teacher says: "I don't know how I taught before PTCC. I'm less stressed, my students are better grouped, I catch problems before they escalate."

That's what PTCC Full was designed for. PTCC Lite is the realistic path to getting there.

---

*Roadmap by: Patrick Cantillon | Date: October 19, 2024*
*Next Review: December 1, 2024 (after real-world testing with PTCC Lite)*
