#!/usr/bin/env python3
import sqlite3
import os

def migrate_database():
    db_path = 'instance/harvest.db'
    
    if not os.path.exists(db_path):
        print("Database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if file_id column exists in message table
        cursor.execute("PRAGMA table_info(message)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'file_id' not in columns:
            print("Adding file_id column to message table...")
            cursor.execute("ALTER TABLE message ADD COLUMN file_id INTEGER")
            conn.commit()
            print("file_id column added")
        else:
            print("file_id column already exists")
            
        # Recreate file table with new structure
        cursor.execute("PRAGMA table_info(file)")
        file_columns = [column[1] for column in cursor.fetchall()]
        
        if 'filename' not in file_columns:
            print("Recreating file table...")
            cursor.execute("DROP TABLE IF EXISTS file")
            cursor.execute("""
                CREATE TABLE file (
                    id INTEGER PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    original_name VARCHAR(255) NOT NULL,
                    file_path VARCHAR(512) NOT NULL,
                    file_type VARCHAR(100) NOT NULL,
                    uploaded_by INTEGER NOT NULL,
                    created_at DATETIME,
                    FOREIGN KEY(uploaded_by) REFERENCES user(id)
                )
            """)
            conn.commit()
            print("file table recreated")
        else:
            print("file table already has correct structure")
            
        # Check if description column exists in group table
        cursor.execute("PRAGMA table_info('group')")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'description' not in columns:
            print("Adding description column to group table...")
            cursor.execute("ALTER TABLE 'group' ADD COLUMN description TEXT")
            conn.commit()
            print("description column added")
        else:
            print("description column already exists")
            
        # Check if avatar column exists in channel table
        cursor.execute("PRAGMA table_info(channel)")
        channel_columns = [column[1] for column in cursor.fetchall()]
        
        if 'avatar' not in channel_columns:
            print("Adding avatar column to channel table...")
            cursor.execute("ALTER TABLE channel ADD COLUMN avatar VARCHAR(128)")
            conn.commit()
            print("avatar column added to channel")
        else:
            print("avatar column already exists in channel")
            
        print("Migration completed!")
        
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()