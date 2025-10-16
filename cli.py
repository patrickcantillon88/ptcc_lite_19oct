#!/usr/bin/env python3
"""
PTCC CLI - Command Line Interface
Main entry point for the PTCC system
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.cli import main

if __name__ == "__main__":
    main()