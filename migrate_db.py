#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

def migrate_database():
    db_path = 'instance/harvest.db'
    
    if not os.path.exists(db_path):
        print("Database not found, will be created on first run")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if created_at column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'created_at' not in columns:
            print("Adding created_at column...")
            cursor.execute("ALTER TABLE user ADD COLUMN created_at DATETIME")
            
            # Update existing users with current timestamp
            now = datetime.now().isoformat()
            cursor.execute("UPDATE user SET created_at = ? WHERE created_at IS NULL", (now,))
            
            conn.commit()
            print("Migration completed!")
        else:
            print("Column created_at already exists")
            
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()