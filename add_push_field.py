#!/usr/bin/env python3
import sqlite3
import os

def add_push_field():
    db_path = 'instance/harvest.db'
    
    if not os.path.exists(db_path):
        print("База данных не найдена!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('ALTER TABLE user ADD COLUMN push_subscription TEXT')
            print("Добавлено поле push_subscription")
        except sqlite3.OperationalError:
            print("Поле push_subscription уже существует")
        
        conn.commit()
        conn.close()
        
        print("База данных обновлена для push-уведомлений!")
        return True
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

if __name__ == '__main__':
    add_push_field()