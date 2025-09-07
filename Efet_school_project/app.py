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

# Add health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    try:
        # Test database connection
        with app.app_context():
            result = db.session.execute(db.text('SELECT 1'))
        return {'status': 'healthy', 'service': 'EFET School Management'}, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {'status': 'unhealthy', 'error': str(e)}, 500

# Initialize database
try:
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully!")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    # Don't exit, let the app start anyway

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)