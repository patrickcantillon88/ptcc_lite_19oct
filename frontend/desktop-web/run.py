#!/usr/bin/env python3
"""
Run script for PTCC Desktop Web Frontend
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Run the Streamlit frontend"""
    # Change to the frontend directory
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)
    
    # Run Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8502",
        "--server.address", "0.0.0.0",
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false"
    ])

if __name__ == "__main__":
    main()