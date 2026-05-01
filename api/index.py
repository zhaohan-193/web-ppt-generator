import sys
import os
from pathlib import Path

# Add project root to path so backend modules can be found
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Set Vercel env flag
os.environ["VERCEL"] = "1"

from backend.main import app

# Vercel expects the ASGI app to be named 'app' or 'handler'
handler = app
