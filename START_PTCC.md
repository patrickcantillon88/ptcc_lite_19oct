# PTCC Launch Script - Quick Reference 🚀

## One-Command Startup

Open your terminal **outside of Warp** and run:

```bash
cd /Users/cantillonpatrick/Desktop/ptcc_standalone && ./start-ptcc.sh
```

That's it! The script will:

1. **Show splash screen** with PTCC branding
2. **Check system** requirements and directories
3. **Clear ports** (8000, 5174, 8501)
4. **Start Backend API** on port 8000
5. **Start Mobile PWA** on port 5174
6. **Start Streamlit Dashboard** on port 8501
7. **Show status** with colored checkmarks
8. **Open dashboard** automatically in your browser

---

## What You'll See

### Splash Screen
```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     █████╗ ████████╗ ██████╗ ██████╗                   ║
║     ██╔══██╗╚══██╔══╝██╔════╝██╔════╝                   ║
║     ██████╔╝   ██║   ██║     ██║                        ║
║     ██╔═══╝    ██║   ██║     ██║                        ║
║     ██║        ██║   ╚██████╗╚██████╗                   ║
║     ╚═╝        ╚═╝    ╚═════╝ ╚═════╝                   ║
║                                                                ║
║   Personal Teaching Command Center                            ║
║   Privacy-Preserving Safeguarding System                      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

Initializing system...
```

### Status Updates
```
ℹ Checking system requirements...
✓ All directories found

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Clearing ports...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Ports cleared

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Starting Backend API (port 8000)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ℹ Backend PID: 12345
✓ Backend API ready on port 8000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Starting Mobile PWA (port 5174)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ℹ PWA PID: 12346
✓ Mobile PWA ready on port 5174

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Starting Streamlit Dashboard (port 8501)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Backend API       http://localhost:8000
✓ Mobile PWA        http://localhost:5174
✓ Dashboard         http://localhost:8501

Opening Streamlit Dashboard...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Then Streamlit will launch in your default browser on `http://localhost:8501`

---

## System Status

Once running, check the sidebar in Streamlit:

- **🔗 API Status**: Shows ✅ Backend Connected
- **📱 Mobile Interface**: Shows 🚀 Launch button
- Shows mobile PWA URL and other configuration

---

## What's Running

| Component | Port | URL |
|-----------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Mobile PWA | 5174 | http://localhost:5174 |
| Dashboard | 8501 | http://localhost:8501 |

---

## Logs

Logs are saved to `.ptcc_logs/` directory:

```bash
# Backend log
tail -f /Users/cantillonpatrick/Desktop/ptcc_standalone/.ptcc_logs/backend.log

# Mobile PWA log
tail -f /Users/cantillonpatrick/Desktop/ptcc_standalone/.ptcc_logs/pwa.log

# Dashboard log
tail -f /Users/cantillonpatrick/Desktop/ptcc_standalone/.ptcc_logs/dashboard.log
```

---

## Stop Everything

Press `Ctrl+C` in the terminal where you ran the script, or:

```bash
pkill -f "python.*backend"
pkill -f "npm run dev"
pkill -f "vite"
pkill -f "streamlit"
```

---

## Troubleshooting

### Script doesn't exist
```bash
ls -la /Users/cantillonpatrick/Desktop/ptcc_standalone/start-ptcc.sh
```

If file doesn't exist or isn't executable:
```bash
chmod +x /Users/cantillonpatrick/Desktop/ptcc_standalone/start-ptcc.sh
```

### Permission denied
```bash
chmod +x /Users/cantillonpatrick/Desktop/ptcc_standalone/start-ptcc.sh
```

### Services not starting
Check logs:
```bash
tail -50 /Users/cantillonpatrick/Desktop/ptcc_standalone/.ptcc_logs/backend.log
```

### Ports already in use
The script automatically clears ports, but if that fails:
```bash
lsof -i :8000   # Find process on port 8000
kill -9 <PID>   # Replace <PID> with actual process ID
```

---

## Features

✅ **Splash Screen** - Professional PTCC branding  
✅ **Automatic Cleanup** - Clears old processes and ports  
✅ **Status Indicators** - Colored checkmarks for each step  
✅ **Health Checks** - Waits for each service to be ready  
✅ **Auto Browser Open** - Opens dashboard in browser  
✅ **Logging** - All output saved to logs directory  
✅ **Clean Shutdown** - Ctrl+C stops all services gracefully  

---

## Environment Variables

The script automatically sets:

```bash
VITE_NEW_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_BASE_URL=http://localhost:8000
MOBILE_PWA_URL=http://localhost:5174
JWT_SECRET=dev-secret-key-change-in-production
```

To use different values:

```bash
export JWT_SECRET="your-secret-key"
cd /Users/cantillonpatrick/Desktop/ptcc_standalone && ./start-ptcc.sh
```

---

## System Architecture

```
┌─────────────────────────────────────────┐
│  Streamlit Dashboard (Streamlit)        │
│  http://localhost:8501                  │
│  - Teacher interface                    │
│  - 📱 PWA Launcher                      │
│  - System status                        │
└─────────────────────────────────────────┘
         ▲                          │
         │                          │ Launches
         │ API Calls               ▼
         │             ┌──────────────────┐
         │             │ Mobile PWA       │
         │             │ http://localhost:5174
         │             └──────────────────┘
         │                          │
         │                          │
         └──────────────────────────┘ API Calls
                        │
                        ▼
        ┌──────────────────────────┐
        │ Backend API (FastAPI)     │
        │ http://localhost:8000     │
        │ - Safeguarding logic      │
        │ - Student data            │
        │ - Compliance checks       │
        └──────────────────────────┘
```

---

## Quick Access

After startup, access:

1. **Dashboard**: http://localhost:8501 (automatic)
2. **Mobile PWA**: Click "🚀 Launch" in sidebar OR http://localhost:5174
3. **Backend Health**: http://localhost:8000/health (should show `{status: healthy}`)
4. **Logs**: Check `.ptcc_logs/` directory

---

## Help

For more information, see:

- `QUICK_START_COMPLETE_SYSTEM.md` - Complete setup guide
- `SYSTEM_COMPLETE_OVERVIEW.md` - System architecture
- `DASHBOARD_UPDATE_COMPLETE.md` - Dashboard features
- `FRONTEND_BACKEND_INTEGRATION.md` - API integration

---

**Ready?** Run this in your terminal:

```bash
cd /Users/cantillonpatrick/Desktop/ptcc_standalone && ./start-ptcc.sh
```

🚀 **That's it!**
