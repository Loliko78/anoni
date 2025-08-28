#!/usr/bin/env python3
"""
Тестовый запуск приложения для проверки работоспособности
"""

from app import app, db
from models import User, Chat, Group, Channel
from werkzeug.security import generate_password_hash

def test_app():
    with app.app_context():
        try:
            # Создаем таблицы
            db.create_all()
            print("[OK] База данных создана")
            
            # Проверяем создание пользователя
            test_user = User.query.filter_by(nickname_enc='test_user').first()
            if not test_user:
                test_user = User(
                    nickname_enc='test_user',
                    password_hash=generate_password_hash('test123')
                )
                db.session.add(test_user)
                db.session.commit()
                print("[OK] Тестовый пользователь создан")
            else:
                print("[OK] Тестовый пользователь уже существует")
            
            # Проверяем количество пользователей
            user_count = User.query.count()
            print(f"[OK] Всего пользователей: {user_count}")
            
            # Проверяем количество чатов
            chat_count = Chat.query.count()
            print(f"[OK] Всего чатов: {chat_count}")
            
            # Проверяем количество групп
            group_count = Group.query.count()
            print(f"[OK] Всего групп: {group_count}")
            
            # Проверяем количество каналов
            channel_count = Channel.query.count()
            print(f"[OK] Всего каналов: {channel_count}")
            
            print("\n[SUCCESS] Приложение готово к работе!")
            print("Запустите: python run_with_cloudflare.py")
            
        except Exception as e:
            print(f"[ERROR] Ошибка: {e}")
            return False
    
    return True

if __name__ == '__main__':
    test_app()