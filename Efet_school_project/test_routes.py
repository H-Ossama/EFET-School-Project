import sys
import os

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)  # Add parent directory for top-level imports
sys.path.insert(0, current_dir)  # Add current directory

# Ensure school_project module is in the Python path
school_project_dir = os.path.join(current_dir, 'school_project')
if os.path.exists(school_project_dir):
    sys.path.insert(0, school_project_dir)
    print(f"Added {school_project_dir} to Python path")

# Import the app
from app import app

# Print all routes
print("Available routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.rule}")