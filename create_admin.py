#!/usr/bin/env python3
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Проверяем, существует ли уже админ
        admin = User.query.filter_by(nickname_enc='azazel').first()
        
        if admin:
            print("Admin azazel already exists")
            return
        
        # Создаем админа
        admin = User(
            nickname_enc='azazel',
            password_hash=generate_password_hash('Log1progress'),
            is_admin=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("Admin azazel created successfully!")
        print("Login: azazel")
        print("Password: Log1progress")

if __name__ == '__main__':
    create_admin()