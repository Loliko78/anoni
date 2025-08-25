#!/usr/bin/env python3
"""
Безопасная инициализация базы данных
"""

from app import app, db
import os

def init_database():
    """Инициализируем базу данных"""
    with app.app_context():
        try:
            # Создаем все таблицы
            db.create_all()
            print("✅ База данных инициализирована")
            
            # Запускаем исправления
            from fix_db import fix_database
            fix_database()
            
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
    return True

if __name__ == '__main__':
    print("🔧 Инициализация базы данных...")
    if init_database():
        print("✅ Готово!")
    else:
        print("❌ Ошибка!")