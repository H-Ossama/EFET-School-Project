#!/usr/bin/env python3
"""
Test script to create a visitor user and admin notification
"""

import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_test_visitor():
    db_path = './instance/db.sqlite'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create a test visitor user
        email = 'visitor@test.com'
        name = 'Test Visitor'
        password = generate_password_hash('password123', method='pbkdf2:sha256')
        
        # Check if user already exists
        cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
        if cursor.fetchone():
            print(f"User {email} already exists")
            return
        
        # Insert new visitor user
        cursor.execute("""
            INSERT INTO user (email, name, password, role, status) 
            VALUES (?, ?, ?, 'visiteur', 'pending')
        """, (email, name, password))
        
        user_id = cursor.lastrowid
        
        # Create admin notification for this user
        message = f"Nouvel utilisateur {name} ({email}) s'est inscrit et attend l'approbation."
        cursor.execute("""
            INSERT INTO admin_notification (user_id, notification_type, message, is_read) 
            VALUES (?, 'new_registration', ?, 0)
        """, (user_id, message))
        
        conn.commit()
        print(f"Created test visitor user: {email} (password: password123)")
        print(f"Created admin notification for user ID: {user_id}")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_visitor()