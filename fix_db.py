#!/usr/bin/env python3
"""
Исправление базы данных - добавление недостающих полей
"""

from app import app, db
from models import User
import datetime

def fix_database():
    """Исправляем базу данных"""
    with app.app_context():
        try:
            # Проверяем, есть ли поле created_at
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            if 'created_at' not in columns:
                print("Adding created_at field...")
                db.engine.execute('ALTER TABLE user ADD COLUMN created_at DATETIME')
                
                # Обновляем существующих пользователей
                users = User.query.all()
                for user in users:
                    if not hasattr(user, 'created_at') or user.created_at is None:
                        user.created_at = datetime.datetime.now(datetime.timezone.utc)
                db.session.commit()
                print("Field created_at added")
            else:
                print("Field created_at already exists")
                
            print("Database fixed")
            
        except Exception as e:
            print(f"Error fixing database: {e}")
            return False
    return True

if __name__ == '__main__':
    fix_database()