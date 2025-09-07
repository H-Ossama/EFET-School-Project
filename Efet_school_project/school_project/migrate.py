#!/usr/bin/env python3
"""
Migration script to add status column to user table and create new tables
for admin notifications and email logs.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    db_path = './instance/db.sqlite'
    
    if not os.path.exists(db_path):
        print("Database not found. Creating new database...")
        # Database will be created when the app runs
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if status column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'status' not in columns:
            print("Adding status column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN status TEXT DEFAULT 'pending'")
            
            # Update existing users to have 'approved' status
            cursor.execute("UPDATE user SET status = 'approved' WHERE role != 'visiteur'")
            print("Updated existing users to approved status")
        
        # Create admin_notification table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_notification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                notification_type TEXT DEFAULT 'new_registration',
                message TEXT,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                resolved_by INTEGER,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (resolved_by) REFERENCES user (id)
            )
        """)
        print("Created admin_notification table")
        
        # Create email_log table  
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                subject TEXT,
                message TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'sent',
                FOREIGN KEY (recipient_id) REFERENCES user (id),
                FOREIGN KEY (sender_id) REFERENCES user (id)
            )
        """)
        print("Created email_log table")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()