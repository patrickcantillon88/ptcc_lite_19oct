#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple backend runner for PTCC system"""

import sys
import os
from pathlib import Path
import argparse

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the backend
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run PTCC Backend Server")
    parser.add_argument("--port", type=int, default=8005, help="Port to run the server on")
    args = parser.parse_args()

    import uvicorn
    from backend.main import app

    print("Starting PTCC Backend Server...")
    print(f"API will be available at: http://localhost:{args.port}")
    print(f"API docs at: http://localhost:{args.port}/docs")
    print(f"Health check at: http://localhost:{args.port}/health")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=args.port,
        reload=False,  # Disable reload to avoid import issues
        log_level="info"
    )