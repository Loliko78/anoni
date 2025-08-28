#!/usr/bin/env python3
"""
Миграция для добавления полей онлайн-статуса в таблицу User
"""

import sqlite3
import os
from datetime import datetime, timezone

def migrate_database():
    db_path = 'harvest.db'
    
    if not os.path.exists(db_path):
        print("База данных не найдена!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, существуют ли уже поля
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Добавляем поле last_seen если его нет
        if 'last_seen' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN last_seen DATETIME')
            print("Добавлено поле last_seen")
        else:
            print("Поле last_seen уже существует")
        
        # Добавляем поле is_online если его нет
        if 'is_online' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN is_online BOOLEAN DEFAULT 0')
            print("Добавлено поле is_online")
        else:
            print("Поле is_online уже существует")
        
        # Проверяем таблицу chat
        cursor.execute("PRAGMA table_info(chat)")
        chat_columns = [column[1] for column in cursor.fetchall()]
        
        # Добавляем поле last_activity если его нет
        if 'last_activity' not in chat_columns:
            cursor.execute('ALTER TABLE chat ADD COLUMN last_activity DATETIME')
            print("Добавлено поле last_activity в таблицу chat")
        else:
            print("Поле last_activity уже существует в таблице chat")
        
        # Устанавливаем текущее время для всех пользователей
        current_time = datetime.now(timezone.utc).isoformat()
        cursor.execute('UPDATE user SET last_seen = ? WHERE last_seen IS NULL', (current_time,))
        cursor.execute('UPDATE user SET is_online = 0 WHERE is_online IS NULL')
        
        conn.commit()
        conn.close()
        
        print("Миграция успешно завершена!")
        return True
        
    except Exception as e:
        print(f"Ошибка миграции: {e}")
        return False

if __name__ == '__main__':
    migrate_database()