#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime, timezone

def fix_database():
    db_path = 'instance/harvest.db'
    
    if not os.path.exists(db_path):
        print("База данных не найдена!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Добавляем поля в таблицу user
        try:
            cursor.execute('ALTER TABLE user ADD COLUMN last_seen DATETIME')
            print("Добавлено поле last_seen")
        except sqlite3.OperationalError:
            print("Поле last_seen уже существует")
        
        try:
            cursor.execute('ALTER TABLE user ADD COLUMN is_online BOOLEAN DEFAULT 0')
            print("Добавлено поле is_online")
        except sqlite3.OperationalError:
            print("Поле is_online уже существует")
        
        # Добавляем поле в таблицу chat
        try:
            cursor.execute('ALTER TABLE chat ADD COLUMN last_activity DATETIME')
            print("Добавлено поле last_activity")
        except sqlite3.OperationalError:
            print("Поле last_activity уже существует")
        
        # Устанавливаем значения по умолчанию
        current_time = datetime.now(timezone.utc).isoformat()
        cursor.execute('UPDATE user SET last_seen = ? WHERE last_seen IS NULL', (current_time,))
        cursor.execute('UPDATE user SET is_online = 0 WHERE is_online IS NULL')
        cursor.execute('UPDATE chat SET last_activity = ? WHERE last_activity IS NULL', (current_time,))
        
        conn.commit()
        conn.close()
        
        print("База данных успешно обновлена!")
        return True
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

if __name__ == '__main__':
    fix_database()