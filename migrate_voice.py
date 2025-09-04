#!/usr/bin/env python3
"""
Миграция для добавления поддержки голосовых сообщений
"""

import sqlite3
import os

def migrate_database():
    """Добавляет поле voice_duration в таблицу message"""
    
    # Путь к базе данных
    db_path = os.path.join('instance', 'harvest.db')
    
    if not os.path.exists(db_path):
        print("База данных не найдена. Создайте её сначала.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, существует ли уже поле voice_duration
        cursor.execute("PRAGMA table_info(message)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'voice_duration' not in columns:
            print("Добавляем поле voice_duration в таблицу message...")
            cursor.execute("ALTER TABLE message ADD COLUMN voice_duration INTEGER")
            conn.commit()
            print("Поле voice_duration успешно добавлено")
        else:
            print("Поле voice_duration уже существует")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Ошибка миграции: {e}")
        return False

if __name__ == '__main__':
    print("Запуск миграции для голосовых сообщений...")
    if migrate_database():
        print("Миграция завершена успешно!")
    else:
        print("Миграция не удалась!")