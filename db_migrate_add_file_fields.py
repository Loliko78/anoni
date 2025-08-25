#!/usr/bin/env python3
"""
Database migration to add file_type and file_name columns to Message table
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
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(message)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'file_type' not in columns:
            print("Adding file_type column to Message table...")
            cursor.execute("ALTER TABLE message ADD COLUMN file_type VARCHAR(50)")
            conn.commit()
            print("file_type column added successfully!")
        else:
            print("file_type column already exists.")
            
        if 'file_name' not in columns:
            print("Adding file_name column to Message table...")
            cursor.execute("ALTER TABLE message ADD COLUMN file_name VARCHAR(255)")
            conn.commit()
            print("file_name column added successfully!")
        else:
            print("file_name column already exists.")
            
        print("Migration completed successfully!")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate() 