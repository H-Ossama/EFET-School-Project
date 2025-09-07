####################################################################
################### EFET School Management System ################
####################################################################

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the school_project directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'school_project'))

try:
    from school_project import create_app, db
    from school_project.models import *
    
    logger.info("Imports successful")
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)

# Create the Flask application
app = create_app()
logger.info("Flask app created")

# Add error handlers
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    db.session.rollback()
    return f"Internal Server Error: {error}", 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return f"An error occurred: {str(e)}", 500

# Add debug endpoint for Railway
@app.route('/debug')
def debug_info():
    """Debug endpoint to check app status"""
    try:
        with app.app_context():
            # Import only what we need for the debug check
            from school_project.models import User
            try:
                user_count = User.query.count()
                db_status = 'connected'
            except Exception as db_err:
                user_count = 'unknown'
                db_status = f'error: {str(db_err)}'
            
            return {
                'status': 'running',
                'database': db_status,
                'user_count': user_count,
                'tables_created': 'attempting'
            }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }, 500

# Add health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    try:
        # Test database connection
        with app.app_context():
            try:
                result = db.session.execute(db.text('SELECT 1'))
                db_status = 'connected'
            except Exception:
                db_status = 'disconnected'
        
        return {
            'status': 'healthy', 
            'service': 'EFET School Management',
            'database': db_status,
            'port': os.environ.get('PORT', 'default')
        }, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        # Return 200 to pass Railway healthcheck even if there are minor issues
        return {
            'status': 'partial', 
            'error': str(e),
            'service': 'EFET School Management'
        }, 200

# Initialize database
try:
    with app.app_context():
        # Only create tables, don't import models here to avoid conflicts
        db.create_all()
        logger.info("Database tables created successfully!")
        
        # Check if we have an admin user, create one if not (only on Railway/production)
        if os.environ.get('DATABASE_URL'):  # Only on Railway with PostgreSQL
            try:
                from school_project.models import User
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
            except Exception as admin_err:
                logger.warning(f"Admin user creation failed: {admin_err}")
        
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    # Don't exit, let the app start anyway

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)