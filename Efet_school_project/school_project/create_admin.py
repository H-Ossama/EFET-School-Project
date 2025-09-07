#!/usr/bin/env python3
"""
Utility script to create an admin user in the database.
This can be run manually if needed to ensure admin access.
"""

import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Make sure we can import from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def create_admin():
    """Creates or updates an admin user in the database"""
    try:
        from school_project import create_app, db
        from school_project.models import User
        
        app = create_app()
        
        with app.app_context():
            # Check if our admin exists
            admin = User.query.filter_by(email='ossamahattan@gmail.com').first()
            
            if admin:
                # Update existing user to have admin role
                admin.role = 'admin'
                admin.status = 'approved'
                admin.password = generate_password_hash('1324Haddadi@', method='pbkdf2:sha256')
                db.session.commit()
                logger.info(f"Updated existing user {admin.email} to admin role")
            else:
                # Create new admin user
                admin = User(
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
                db.session.add(admin)
                db.session.commit()
                logger.info(f"Created new admin user {admin.email}")
            
            return True
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        return False

if __name__ == "__main__":
    success = create_admin()
    if success:
        print("Admin user created/updated successfully.")
    else:
        print("Failed to create/update admin user. Check logs for details.")
        sys.exit(1)