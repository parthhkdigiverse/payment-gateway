import sys
import os

# Resolve paths to root and backend directories
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_dir = os.path.join(root_dir, 'backend')

# Add both paths to the python path so absolute imports resolve correctly on Vercel
sys.path.append(root_dir)
sys.path.append(backend_dir)

# Import FastAPI app from backend.main
from backend.main import app
