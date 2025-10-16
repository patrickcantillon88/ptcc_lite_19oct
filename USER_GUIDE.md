# PTCC User Guide for Teachers

## Welcome to PTCC

The Personal Teaching Command Center (PTCC) is your AI-powered assistant for managing student data, generating insights, and optimizing your teaching workflow. This guide will help you get started with all the features available in the system.

## 🚀 Quick Start

### First Time Setup
1. **Start the Backend**: Run `python run_backend.py`
2. **Launch Desktop Interface**: Run `python frontend/desktop-web/run.py`
3. **Access Mobile PWA**: Visit `http://localhost:5173` (when running)

### Daily Workflow
1. **Morning Briefing**: Start your day with the daily briefing
2. **Check AI Insights**: Review AI agent recommendations
3. **Student Management**: Access student profiles and logs
4. **Quick Logging**: Use mobile PWA for in-class observations

## 📋 Daily Briefing

The daily briefing is your command center overview:

### Key Features
- **Schedule Overview**: Today's classes and student counts
- **Student Alerts**: At-risk students requiring attention
- **Duty Assignments**: Your teaching responsibilities
- **AI Insights**: Automated recommendations from AI agents

### Using the Briefing
1. Navigate to "Daily Briefing" in the sidebar
2. Review the date and schedule summary
3. Check student alerts for any at-risk notifications
4. Review duty assignments and communications

## 🤖 AI Teacher Tools

PTCC includes three specialized AI agents to enhance your teaching:

### 🛡️ At-Risk Student Identifier
**Purpose**: Identify students who may need additional support

**How to Use**:
1. Go to "AI Agents" → "At-Risk Student Identifier"
2. Choose analysis type:
   - **Individual Student**: Analyze specific student risk factors
   - **Class Analysis**: Review entire class for at-risk patterns
   - **System Overview**: School-wide risk assessment

**What It Provides**:
- Risk scores (Low/Medium/High/Critical)
- Specific risk factors identified
- Recommended intervention strategies
- Actionable next steps

### 📊 Classroom Behavior Manager
**Purpose**: Optimize classroom dynamics and behavior

**How to Use**:
1. Go to "AI Agents" → "Classroom Behavior Manager"
2. Select your class
3. Choose analysis type (Comprehensive/Insights/Trends)

**What It Provides**:
- Behavior pattern analysis
- Seating arrangement recommendations
- Intervention strategies
- Peer relationship insights

### 🎯 Personalized Learning Path Creator
**Purpose**: Create individualized learning plans

**How to Use**:
1. Go to "AI Agents" → "Personalized Learning Path Creator"
2. Select individual student or class overview
3. Review generated learning objectives

**What It Provides**:
- Learning gap identification
- Strength-based recommendations
- Specific learning objectives
- Progress monitoring plans

## 👥 Student Management

### Viewing Student Information
1. Navigate to "Students" in the sidebar
2. Use filters to find specific students:
   - Class code (7A, 7B, 8A, etc.)
   - Year group (7-11)
   - Campus (JC)
   - Support level (0-3)

### Student Profile Details
Each student profile includes:
- **Basic Information**: Name, class, year group, campus
- **Support Level**: Visual indicator (🟢 Low, 🟡 Medium, 🟠 High, 🔴 Critical)
- **Support Notes**: Additional context and requirements
- **Recent Logs**: Behavior and observation history
- **Assessment History**: Academic performance trends

### Adding Quick Logs
Use the mobile PWA for rapid in-class logging:
1. Open mobile PWA on tablet/phone
2. Select student from quick search
3. Choose log type (Positive/Negative/Neutral)
4. Add category and notes
5. Submit instantly

## 🔍 Search Functionality

### Smart Search Features
- **Natural Language**: Search using everyday language
- **Multi-Source**: Searches across all student data and documents
- **Relevance Ranking**: Most relevant results appear first

### Search Examples
```
"anxious students in year 7"
"behavior issues last week"
"assessment results for Nguyen"
"support plans for high needs"
```

### Advanced Search
- Use quotes for exact phrases
- Combine multiple terms for specific results
- Filter by date ranges and categories

## 📁 Data Import

### Supported File Types
- **Excel/CSV**: Student lists, assessment data, timetables
- **PDF**: Reports, meeting notes, policies
- **Word Documents**: Communications, IEPs, reports

### Import Process
1. Go to "Import" in the sidebar
2. Choose single file or directory import
3. Select file type or use auto-detection
4. Choose whether to index for search
5. Click "Import" and monitor progress

## 📱 Mobile PWA Usage

### Setup
1. Start the mobile PWA: `npm run dev`
2. Access via `http://localhost:5173`
3. Install as PWA on mobile devices for offline capability

### Key Features
- **Quick Student Search**: Rapid access to student profiles
- **In-Lesson Logging**: Add behavior observations instantly
- **Camera Integration**: Photo documentation capabilities
- **Offline Mode**: Continue working without internet
- **Push Notifications**: Reminders and alerts

### Best Practices
- Keep device charged for offline logging
- Sync data when back online
- Use camera for visual behavior documentation
- Regular data synchronization

## ⚙️ Settings and Configuration

### System Settings
- **Search Results**: Adjust number of results displayed
- **Notifications**: Configure alerts and reminders
- **Backup Settings**: Automatic data backups
- **Privacy Options**: Data export and security settings

### Customization
- **School Information**: Update campus and house details
- **Timetable**: Configure period structures
- **File Paths**: Set default locations for data imports

## 🔒 Privacy and Security

### Data Protection
- **Local Storage**: All data remains on your device
- **No Cloud Uploads**: Complete privacy for student information
- **Encrypted Database**: SQLite with built-in encryption
- **Access Control**: Configurable user permissions

### Best Practices
- Regular data backups
- Secure device storage
- Private network usage
- Regular system updates

## 🆘 Troubleshooting

### Common Issues

**Backend Won't Start**
```
Error: Port 8005 already in use
Solution: Kill existing process or change port in config
```

**Frontend Can't Connect**
```
Error: Cannot connect to backend
Solution: Ensure backend is running on correct port
```

**Search Not Working**
```
Issue: No results returned
Solution: Check if documents are indexed, rebuild search index
```

**Mobile PWA Not Loading**
```
Issue: Blank screen or errors
Solution: Clear browser cache, restart development server
```

### Getting Help
1. Check system logs in `logs/ptcc.log`
2. Review API documentation at `/docs`
3. Test individual components with integration scripts
4. Contact system administrator for advanced issues

## 📈 Advanced Features

### Custom Reporting
- Export student data in multiple formats
- Generate custom reports and analytics
- Schedule automated report generation

### Integration Options
- API access for third-party tools
- Data export for external analysis
- Custom script integration

### Performance Optimization
- Database query optimization
- Search index maintenance
- System resource monitoring

## 🎯 Pro Tips

1. **Morning Routine**: Always start with the daily briefing
2. **Mobile First**: Use PWA for in-class observations
3. **Regular Backups**: Enable automatic backups for data safety
4. **AI Integration**: Leverage AI agents for proactive insights
5. **Search Power**: Use natural language search for quick information retrieval

## 📞 Support

For technical support or feature requests:
- Check the troubleshooting section first
- Review system logs for error details
- Contact your system administrator
- Refer to API documentation for advanced usage

---

**Version**: PTCC 1.0.0 with BIS HCMC Dataset
**Last Updated**: October 2025
**System Status**: Production Ready ✅