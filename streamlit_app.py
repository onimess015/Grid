"""
streamlit_app.py
Streamlit Cloud standard entry point forwarding to app.py
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Execute app.py
from app import *
