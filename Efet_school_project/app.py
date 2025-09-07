####################################################################
################### EFET School Management System ################
####################################################################

import os
import sys

# Add the school_project directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'school_project'))

from school_project import create_app
from school_project.models import *
from school_project import db

# Create the Flask application
app = create_app()

# Create database tables if they don't exist
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

if __name__ == '__main__':
    # Development server
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))