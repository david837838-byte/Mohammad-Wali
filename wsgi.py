# WSGI file for PythonAnywhere
import sys
from pathlib import Path

# Add the project directory to the path
project_dir = str(Path(__file__).parent)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Import and run the app
from app import app
application = app
