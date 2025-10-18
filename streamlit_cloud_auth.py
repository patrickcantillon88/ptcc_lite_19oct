"""
PTCC Cloud Deployment with Authentication
Simple login system for demo/testing access
"""

import os
import sys
import threading
import time
import streamlit as st
import hashlib

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append('frontend/desktop-web')

# Demo credentials from environment
DEMO_USERNAME = os.getenv('DEMO_USERNAME', 'demo')
DEMO_PASSWORD = os.getenv('DEMO_PASSWORD', 'ptcc2024')

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(username, password):
    """Verify login credentials"""
    return username == DEMO_USERNAME and password == DEMO_PASSWORD

def login_form():
    """Display login form"""
    st.title("🏫 PTCC Demo Access")
    st.markdown("---")
    
    with st.form("login_form"):
        st.markdown("### Demo Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if check_credentials(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials")
                st.info("Use demo credentials provided by administrator")

def start_backend():
    """Start FastAPI backend in background"""
    try:
        from backend.main import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="error")
    except Exception as e:
        st.error(f"Backend startup failed: {e}")

def main():
    """Main application with authentication"""
    st.set_page_config(
        page_title="PTCC Demo",
        page_icon="🏫",
        layout="wide"
    )
    
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    # Check authentication
    if not st.session_state.authenticated:
        login_form()
        return
    
    # Start backend services once authenticated
    if "services_started" not in st.session_state:
        st.session_state.services_started = True
        threading.Thread(target=start_backend, daemon=True).start()
        time.sleep(2)
    
    # Logout button in sidebar
    with st.sidebar:
        st.markdown(f"**Logged in as:** {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
        
        st.markdown("---")
        st.markdown("### Quick Links")
        st.markdown("- [Mobile PWA](http://localhost:5174) (if running locally)")
        st.markdown("- [API Docs](http://localhost:8001/docs) (if running locally)")
    
    # Import and run main app
    try:
        from app import main as app_main
        app_main()
    except ImportError:
        st.error("Main application not found. Please check deployment.")
        st.info("This may be a deployment configuration issue.")

if __name__ == "__main__":
    main()