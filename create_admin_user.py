#!/usr/bin/env python3
"""
Utility script to ensure admin users exist in the database.
Can be run manually to create or update the admin users.
"""

import os
import sys
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("admin_creator")

# Get the absolute path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.join(current_dir, 'Efet_school_project')

# Add paths to Python path
sys.path.insert(0, current_dir)
sys.path.insert(0, app_path)

def create_admin_users():
    """Create or update admin users in the database"""
    try:
        # Import app and db, handling potential import paths
        try:
            sys.path.insert(0, os.path.join(app_path, 'school_project'))
            from Efet_school_project.app import app, db
            from Efet_school_project.school_project.models import User
        except ImportError:
            os.chdir(app_path)
            from app import app, db
            from school_project.models import User
        
        with app.app_context():
            # Create or update custom admin
            custom_admin = User.query.filter_by(email='ossamahattan@gmail.com').first()
            if custom_admin:
                # Update existing user
                custom_admin.role = 'admin'
                custom_admin.status = 'approved'
                custom_admin.password = generate_password_hash('1324Haddadi@', method='pbkdf2:sha256')
                db.session.commit()
                logger.info("Updated existing admin user with email: ossamahattan@gmail.com")
            else:
                # Create new admin user
                custom_admin = User(
                    email='ossamahattan@gmail.com',
                    name='Ossama Hattan',
                    password=generate_password_hash('1324Haddadi@', method='pbkdf2:sha256'),
                    role='admin',
                    status='approved',
                    age=30,
                    address='EFET School',
                    registration='ADMIN001',
                    gender='Male',
                    register_date=datetime.now().date()
                )
                db.session.add(custom_admin)
                db.session.commit()
                logger.info("Created new admin user with email: ossamahattan@gmail.com")
            
            # Create or update default admin
            default_admin = User.query.filter_by(email='admin@efet.edu').first()
            if not default_admin:
                default_admin = User(
                    email='admin@efet.edu',
                    name='Administrator',
                    password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                    role='admin',
                    status='approved',
                    age=30,
                    address='EFET School',
                    registration='ADMIN001',
                    gender='Other',
                    register_date=datetime.now().date()
                )
                db.session.add(default_admin)
                db.session.commit()
                logger.info("Created backup admin user with email: admin@efet.edu")
            
            return True
    except Exception as e:
        logger.error(f"Error creating admin users: {e}")
        return False

if __name__ == "__main__":
    print("Creating admin users...")
    if create_admin_users():
        print("Admin users created/updated successfully!")
    else:
        print("Failed to create admin users. Check logs for details.")
        sys.exit(1)