#!/usr/bin/env python3
"""
Database migration to add blocked_users column to User table
"""

import sqlite3
import os

def migrate():
    db_path = 'instance/harvest.db'
    
    if not os.path.exists(db_path):
        print("Database not found. Please run the application first to create it.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'blocked_users' not in columns:
            print("Adding blocked_users column to User table...")
            cursor.execute("ALTER TABLE user ADD COLUMN blocked_users TEXT")
            conn.commit()
            print("Migration completed successfully!")
        else:
            print("blocked_users column already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate() 