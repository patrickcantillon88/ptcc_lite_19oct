# PTCC Portable Demo Setup

## Overview
This creates a self-contained demo that runs on any laptop for meetings, presentations, or stakeholder reviews.

## Quick Demo Setup (5 minutes)

### Prerequisites
- macOS or Windows laptop
- Python 3.11+ installed
- Chrome/Firefox browser

### Setup Commands
```bash
# Clone or copy project folder
cd ptcc_standalone

# Install dependencies (one time only)
pip install -r requirements.txt
cd frontend/mobile-pwa && npm install
cd ../desktop-web && pip install -r requirements.txt
cd ../..

# Load demo data (one time only)
python -m backend.scripts.import_sample

# Start demo (every time)
./start-ptcc-fast.sh
```

### Demo URLs
- **Streamlit Dashboard**: http://localhost:8501
- **Mobile PWA**: http://localhost:5174  
- **Backend API**: http://localhost:8001/docs

## Demo Script (15-minute walkthrough)

### Part 1: System Overview (3 minutes)
1. **Start at Streamlit Dashboard** (localhost:8501)
   - Show unified interface
   - Demonstrate document upload
   - Point out "📱 Mobile PWA" link in sidebar

2. **Navigate to Mobile PWA** (click sidebar link)
   - Show two-tab interface: Logger and Agents
   - Demonstrate desktop-responsive design

### Part 2: Student Data Management (5 minutes)
1. **Student Search** (Agents tab)
   - Search for specific student names
   - Show class filtering (3A, 4B, 5C, 6A)
   - Demonstrate instant results vs "15-30 minute current process"

2. **Student Profiles** (select any student)
   - Show complete student information
   - Point out support levels (0-4)
   - Highlight behavioral history integration

### Part 3: AI Agent Analysis (4 minutes)
1. **Agent Cards** (after selecting student)
   - Show three agent types: Period Briefing, CCA Engagement, Accommodation Compliance
   - Demonstrate expandable details
   - Point out priority color coding (green/yellow/orange/red)

2. **Recommended Actions** (expand any card)
   - Show structured recommendations
   - Highlight reasoning section
   - Explain teacher remains in control

### Part 4: Quick Logging (3 minutes)
1. **Logger Tab** (switch from Agents)
   - Show student selection
   - Demonstrate category buttons (positive/negative/neutral)
   - Show offline capability and sync status

2. **Integration** (return to Streamlit)
   - Show how data flows between interfaces
   - Demonstrate search across all data sources

## Key Talking Points During Demo

### Privacy & Security
- "All data stays on this laptop - nothing goes to the cloud"
- "Student data never leaves the school network"
- "You control the data, not a vendor"

### Speed & Efficiency
- "Find any student information in 5 seconds vs 15-30 minutes currently"
- "Three interfaces, one system, no separate logins"
- "Works offline during lessons"

### Teacher Control
- "AI provides recommendations, teachers make decisions"
- "Built by a teacher who understands real classroom needs"
- "System adapts to your workflow, not the other way around"

## Common Questions & Answers

**Q: "What happens if the internet goes down?"**
A: System works completely offline. Mobile PWA caches data and syncs when reconnected.

**Q: "How do we get our real data in?"**
A: Document upload system handles PDFs, Word docs, Excel files. Drag and drop interface.

**Q: "Is this another database we have to maintain?"**  
A: No new data entry. System makes existing data useful by connecting scattered information.

**Q: "What about multi-user access?"**
A: Architecture ready - needs 1-2 days development for teacher login and role-based access.

**Q: "How much does this cost?"**
A: Open source, no licensing. Just development time and server hardware.

## Technical Setup for IT Review

### System Requirements
- Python 3.11+ environment  
- 4GB RAM minimum (8GB recommended)
- SQLite database (included)
- Modern browser (Chrome/Firefox/Safari)

### Network Requirements
- No external internet required for operation
- Internal network for multi-user deployment
- Standard web ports (8001, 8501, 5174)

### Security Architecture
- Local SQLite database
- CORS-protected APIs
- No cloud dependencies
- Complete audit logging

### Scalability Testing
- Currently: 160 students running smoothly
- Tested: 5+ concurrent users
- Capacity: 1000+ students without modification

## Demo Data Details

### Synthetic Dataset
- 160 realistic student profiles
- 4 classes: 3A, 4B, 5C, 6A  
- 2 campuses: A and B
- Support levels 0-4 with realistic distribution
- Behavioral logs with timestamps
- Assessment data across subjects

### No Real Student Data
- All names generated algorithmically
- No connection to actual students
- Safe for external demonstration
- Respects privacy while showing capabilities

## Troubleshooting

### Services Won't Start
```bash
# Kill any running processes
pkill -f "python.*backend"
pkill -f "npm run dev"
pkill -f "streamlit"

# Restart
./start-ptcc-fast.sh
```

### Database Issues
```bash
# Reset to clean state
rm -f data/school.db backend/data/school.db
python -m backend.scripts.import_sample
cp data/school.db backend/data/school.db
```

### Port Conflicts
Edit `start-ptcc-fast.sh` lines 14-16 to change ports if needed.

## Post-Demo Follow-up

### If Interested
1. **Technical Assessment** (1 week)
   - Review codebase and development needs
   - Estimate deployment requirements
   - Plan pilot with real data

2. **Pilot Preparation** (2-3 weeks development)
   - Multi-user authentication
   - Real data import tools
   - Performance optimization

3. **Stakeholder Demo** (custom setup)
   - Run demo on school network
   - Use anonymized real data
   - Include multiple teachers

### If Not Interested
- System remains useful for personal teaching
- No organizational obligations
- Continue independent development

## Contact for Demo
- **In-person**: Bring laptop, 15-30 minutes needed
- **Remote**: Screen share with system running locally  
- **Asynchronous**: Provide access credentials for self-guided exploration

**The system works now. This demo proves it.**