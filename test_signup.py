#!/usr/bin/env python3

import sys
import os

# Add the school_project directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Efet_school_project', 'school_project'))

try:
    # Import from the correct path structure
    from __init__ import create_app, db
    
    print("Creating Flask app...")
    app = create_app()
    
    print("Testing signup functionality...")
    with app.app_context():
        # Test signup endpoint by simulating a POST request
        with app.test_client() as client:
            # First test GET request to signup page
            response = client.get('/signup')
            print(f"GET /signup status code: {response.status_code}")
            
            # Test POST request to signup
            response = client.post('/signup', data={
                'email': 'test@example.com',
                'name': 'Test User',
                'password': 'testpassword123',
                'age': 25,
                'address': 'Test Address',
                'gender': 'Other'
            })
            print(f"POST /signup status code: {response.status_code}")
            
            if response.status_code == 302:  # Redirect means success
                print("SUCCESS: Signup seems to work correctly!")
            else:
                print(f"ERROR: Signup failed with status code {response.status_code}")
                print(f"Response data: {response.get_data(as_text=True)}")
            
except Exception as e:
    print(f"Error testing signup: {e}")
    import traceback
    traceback.print_exc()