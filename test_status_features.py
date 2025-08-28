#!/usr/bin/env python3
"""
Тест новых функций статуса онлайн/офлайн и непрочитанных сообщений
"""

import sqlite3
import os
from datetime import datetime, timezone

def test_status_features():
    """Проверяет, что новые поля добавлены в базу данных"""
    
    # Путь к базе данных
    db_paths = [
        'instance/harvest.db',
        'harvest.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("База данных не найдена!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем структуру таблицы user
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print("Поля в таблице user:")
        for col in columns:
            print(f"  - {col}")
        
        # Проверяем наличие новых полей
        required_fields = ['last_seen', 'is_online']
        missing_fields = []
        
        for field in required_fields:
            if field not in columns:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"\nОтсутствуют поля: {missing_fields}")
            return False
        
        print("\n✅ Все необходимые поля присутствуют!")
        
        # Проверяем количество пользователей
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print(f"Количество пользователей: {user_count}")
        
        # Проверяем статусы пользователей
        cursor.execute("SELECT nickname_enc, is_online, last_seen FROM user LIMIT 5")
        users = cursor.fetchall()
        
        print("\nСтатусы пользователей:")
        for user in users:
            nickname, is_online, last_seen = user
            status = "🟢 Онлайн" if is_online else "🔴 Офлайн"
            print(f"  {nickname}: {status} (последний раз: {last_seen or 'никогда'})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

if __name__ == '__main__':
    print("Тестирование новых функций статуса...")
    test_status_features()