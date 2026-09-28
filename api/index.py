"""
api/index.py
Vercel serverless handler for FastAPI.
Exposes the main FastAPI `app` instance.
"""
import sys
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from server import app  # noqa: E402

# Vercel looks for `app` in this file
