#!/usr/bin/env python3
"""
Database Migration Script for Enhanced Messaging System
This script updates the Message table to support priority and read status.
"""

import sqlite3
import os
from datetime import datetime

# Database paths
DB_PATH = 'database.db'
INSTANCE_DB_PATH = 'instance/db.sqlite'

def get_db_connection():
    """Get database connection."""
    # Try different possible database locations
    db_paths = [DB_PATH, INSTANCE_DB_PATH]
    
    for path in db_paths:
        if os.path.exists(path):
            print(f"Found database at: {path}")
            return sqlite3.connect(path), path
    
    # If no database found, create one in the current directory
    print(f"No existing database found. Creating new one at: {DB_PATH}")
    return sqlite3.connect(DB_PATH), DB_PATH

def backup_database(db_path):
    """Create a backup of the current database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")
        return None

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns

def migrate_messages_table():
    """Migrate the messages table to include priority and read status."""
    conn, db_path = get_db_connection()
    cursor = conn.cursor()
    
    print("Starting migration of messages table...")
    
    try:
        # Create backup
        backup_database(db_path)
        
        # Check if the message table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='message'")
        if not cursor.fetchone():
            print("Message table doesn't exist. Creating it...")
            cursor.execute('''
                CREATE TABLE message (
                    id INTEGER PRIMARY KEY,
                    msg_from INTEGER,
                    msg_to INTEGER,
                    content VARCHAR(1000),
                    date_sent DATETIME,
                    priority VARCHAR(20) DEFAULT 'normal',
                    is_read BOOLEAN DEFAULT 0
                )
            ''')
            print("Message table created successfully!")
        else:
            print("Message table exists. Checking for new columns...")
            
            # Check and add priority column
            if not check_column_exists(cursor, 'message', 'priority'):
                print("Adding 'priority' column...")
                cursor.execute("ALTER TABLE message ADD COLUMN priority VARCHAR(20) DEFAULT 'normal'")
                print("Priority column added successfully!")
            else:
                print("Priority column already exists.")
            
            # Check and add is_read column
            if not check_column_exists(cursor, 'message', 'is_read'):
                print("Adding 'is_read' column...")
                cursor.execute("ALTER TABLE message ADD COLUMN is_read BOOLEAN DEFAULT 0")
                print("is_read column added successfully!")
            else:
                print("is_read column already exists.")
            
            # Check if date_sent is DATE and needs to be updated to DATETIME
            cursor.execute("PRAGMA table_info(message)")
            columns_info = cursor.fetchall()
            date_sent_info = next((col for col in columns_info if col[1] == 'date_sent'), None)
            
            if date_sent_info and 'DATE' in str(date_sent_info[2]).upper() and 'DATETIME' not in str(date_sent_info[2]).upper():
                print("Note: date_sent column type should be DATETIME for better precision.")
                print("Consider recreating the table for full compatibility, or update manually if needed.")
        
        # Update existing messages with default values if they don't have them
        cursor.execute("UPDATE message SET priority = 'normal' WHERE priority IS NULL")
        cursor.execute("UPDATE message SET is_read = 0 WHERE is_read IS NULL")
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Show current table structure
        cursor.execute("PRAGMA table_info(message)")
        columns = cursor.fetchall()
        print("\nCurrent message table structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - Default: {col[4] if col[4] else 'None'}")
        
        # Show sample data
        cursor.execute("SELECT COUNT(*) FROM message")
        count = cursor.fetchone()[0]
        print(f"\nTotal messages in database: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, msg_from, msg_to, priority, is_read FROM message LIMIT 5")
            sample_messages = cursor.fetchall()
            print("\nSample messages:")
            for msg in sample_messages:
                print(f"  ID: {msg[0]}, From: {msg[1]}, To: {msg[2]}, Priority: {msg[3]}, Read: {msg[4]}")
    
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

def verify_migration():
    """Verify that the migration was successful."""
    conn, db_path = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check table structure
        cursor.execute("PRAGMA table_info(message)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        required_columns = ['id', 'msg_from', 'msg_to', 'content', 'date_sent', 'priority', 'is_read']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"❌ Migration verification failed. Missing columns: {missing_columns}")
            return False
        else:
            print("✅ Migration verification successful. All required columns present.")
            return True
    
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== EFET School Project - Message Table Migration ===")
    print("This script will update the message table to support enhanced messaging features.")
    print()
    
    try:
        migrate_messages_table()
        print()
        if verify_migration():
            print("🎉 Migration completed successfully!")
            print("\nNew features available:")
            print("  • Message priority (normal, important, urgent)")
            print("  • Read status tracking")
            print("  • Enhanced message display in dashboard")
        else:
            print("⚠️  Migration completed but verification failed.")
    
    except Exception as e:
        print(f"💥 Migration failed: {e}")
        print("Please check the error and try again.")
        exit(1)