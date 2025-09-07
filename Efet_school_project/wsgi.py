#!/usr/bin/env python3
"""
Simple and clean WSGI entry point for Railway deployment
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'school_project'))

try:
    # Import the app from app.py
    from app import app
    logger.info("Successfully imported app from app.py")
    
except Exception as e:
    logger.error(f"Failed to import app: {e}")
    # Create a minimal Flask app for Railway health checks
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return {'status': 'error', 'error': str(e)}, 200
    
    @app.route('/')
    def root():
        return {'status': 'error', 'message': 'App failed to initialize', 'error': str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
