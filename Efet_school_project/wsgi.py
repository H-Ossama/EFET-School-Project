#!/usr/bin/env python3
"""
Railway Startup Script for EFET School Management System
This script handles all the startup logic for Railway deployment
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_python_path():
    """Add necessary directories to Python path"""
    current_dir = Path(__file__).parent
    school_project_dir = current_dir / 'school_project'
    
    # Add paths
    if str(school_project_dir) not in sys.path:
        sys.path.insert(0, str(school_project_dir))
        logger.info(f"Added {school_project_dir} to Python path")

def create_application():
    """Create and configure the Flask application"""
    try:
        setup_python_path()
        
        # Import after path setup
        from school_project import create_app, db
        from school_project.models import User, Payment, Grade, Major, Message, Absence, Subject, AdminNotification, EmailLog
        
        logger.info("Successfully imported modules")
        
        # Create Flask app
        app = create_app()
        logger.info("Flask application created")
        
        # Add health check endpoint
        @app.route('/health')
        def health_check():
            """Health check endpoint for Railway"""
            return {
                'status': 'healthy', 
                'service': 'EFET School Management System',
                'version': '1.0.0'
            }, 200
        
        # Initialize database
        with app.app_context():
            try:
                db.create_all()
                logger.info("Database tables created/verified successfully")
                
                # Create admin user if doesn't exist
                admin = User.query.filter_by(role='admin').first()
                if not admin:
                    from werkzeug.security import generate_password_hash
                    from datetime import datetime
                    
                    admin_user = User(
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
                    db.session.add(admin_user)
                    db.session.commit()
                    logger.info("Default admin user created")
                else:
                    logger.info("Admin user already exists")
                    
            except Exception as e:
                logger.error(f"Database initialization error: {e}")
                # Don't fail the app startup for database issues
        
        return app
        
    except Exception as e:
        logger.error(f"Application creation failed: {e}")
        raise

# Create the application instance
app = create_application()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting development server on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)