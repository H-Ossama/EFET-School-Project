#!/usr/bin/env python3

import sys
import os

# Add the school_project directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Efet_school_project', 'school_project'))

from __init__ import create_app, db

print('Creating app...')
app = create_app()

with app.app_context():
    print('Creating database tables...')
    db.create_all()
    print('Database tables created successfully!')
    
    # Test if we can query the User table now
    from models import User
    users = User.query.all()
    print(f'Number of users in database: {len(users)}')
    
    print('Testing signup with proper database...')
    with app.test_client() as client:
        response = client.post('/signup', data={
            'email': 'test2@example.com',
            'name': 'Test User 2',
            'password': 'testpassword123',
            'age': 25,
            'address': 'Test Address',
            'gender': 'Other'
        })
        print(f"POST /signup status code: {response.status_code}")
        
        if response.status_code == 302:
            print("SUCCESS: Signup with database works correctly!")
            # Check if user was actually created
            test_user = User.query.filter_by(email='test2@example.com').first()
            if test_user:
                print(f"User successfully created: {test_user.name} ({test_user.email})")
            else:
                print("WARNING: User not found in database after signup")
        else:
            print(f"ERROR: Signup failed with status code {response.status_code}")