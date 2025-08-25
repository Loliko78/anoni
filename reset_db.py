#!/usr/bin/env python3
import os
import shutil

def reset_database():
    """Полный сброс базы данных"""
    
    # Удаляем старую базу данных
    db_files = [
        'instance/harvest.db',
        'harvest.db'
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"Removed {db_file}")
    
    # Удаляем папку instance если пуста
    if os.path.exists('instance') and not os.listdir('instance'):
        os.rmdir('instance')
        print("Removed empty instance directory")
    
    print("Database reset complete!")
    print("Run 'python app.py' to create fresh database")

if __name__ == '__main__':
    reset_database()