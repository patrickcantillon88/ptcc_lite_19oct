"""
PTCC Streamlit Cloud Deployment Entry Point
Simplified version for cloud hosting with embedded backend
"""

import os
import sys
import subprocess
import threading
import time
import streamlit as st

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def start_backend():
    """Start FastAPI backend in background thread"""
    try:
        from backend.main import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="error")
    except Exception as e:
        st.error(f"Backend startup failed: {e}")

def start_pwa():
    """Start PWA build if needed"""
    pwa_path = "frontend/mobile-pwa"
    if os.path.exists(os.path.join(pwa_path, "dist")):
        # Serve built PWA
        os.chdir(pwa_path)
        subprocess.Popen(["python", "-m", "http.server", "5174", "--directory", "dist"])

# Start services in background
if "backend_started" not in st.session_state:
    st.session_state.backend_started = True
    threading.Thread(target=start_backend, daemon=True).start()
    threading.Thread(target=start_pwa, daemon=True).start()
    time.sleep(2)  # Allow services to start

# Import main Streamlit app
sys.path.append("frontend/desktop-web")
from app import main

if __name__ == "__main__":
    main()