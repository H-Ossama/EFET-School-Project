#!/usr/bin/env python3
"""
Script to reset admin password for easy access
"""

import sqlite3
from werkzeug.security import generate_password_hash

def reset_admin_password():
    db_path = './instance/db.sqlite'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Reset password for anass@gmail.com to 'admin123'
        new_password = 'admin123'
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        
        cursor.execute("""
            UPDATE user 
            SET password = ? 
            WHERE email = 'anass@gmail.com' AND role = 'admin'
        """, (hashed_password,))
        
        # Also reset password for admin@efet.ma to 'admin123'
        cursor.execute("""
            UPDATE user 
            SET password = ? 
            WHERE email = 'admin@efet.ma' AND role = 'admin'
        """, (hashed_password,))
        
        conn.commit()
        
        print("✅ Admin passwords reset successfully!")
        print()
        print("🔑 Admin Login Credentials:")
        print("=" * 40)
        print("Account 1:")
        print(f"  Email: anass@gmail.com")
        print(f"  Password: {new_password}")
        print()
        print("Account 2:")
        print(f"  Email: admin@efet.ma")
        print(f"  Password: {new_password}")
        print("=" * 40)
        print()
        print("🌐 Access the application at: http://127.0.0.1:5000")
        print("📋 Use these credentials to login and access admin features")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reset_admin_password()