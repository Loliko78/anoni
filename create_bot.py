#!/usr/bin/env python3
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_bot():
    with app.app_context():
        # Проверяем, существует ли уже бот
        bot = User.query.filter_by(nickname_enc='Harvest').first()
        
        if bot:
            print("Bot Harvest already exists")
            return
        
        # Создаем бота
        bot = User(
            nickname_enc='Harvest',
            password_hash=generate_password_hash('826945214'),
            is_admin=False
        )
        
        db.session.add(bot)
        db.session.commit()
        
        print("Bot Harvest created successfully!")
        print("Login: Harvest")
        print("Password: 826945214")

if __name__ == '__main__':
    create_bot()