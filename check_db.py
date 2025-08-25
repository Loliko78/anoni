#!/usr/bin/env python3
import os
import sqlite3
from pathlib import Path

def check_and_create_db():
    """Check if database exists and create it if needed"""
    db_path = Path("instance/harvest.db")
    
    # Create instance directory if it doesn't exist
    db_path.parent.mkdir(exist_ok=True)
    
    if not db_path.exists():
        print("Database not found. Creating new database...")
        # Create empty database file
        conn = sqlite3.connect(db_path)
        conn.close()
        print("Database file created.")
    else:
        print("Database exists.")

if __name__ == "__main__":
    check_and_create_db() 