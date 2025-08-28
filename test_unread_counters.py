#!/usr/bin/env python3
"""
Тест счетчиков непрочитанных сообщений
"""

from app import app
from models import User, Chat, Message, Group, GroupMember
from datetime import datetime, timezone
import requests
import json

def test_unread_counters():
    with app.app_context():
        # Получаем тестовых пользователей
        user1 = User.query.filter_by(nickname_enc='test_user').first()
        user2 = User.query.filter_by(nickname_enc='azazel').first()
        
        if not user1 or not user2:
            print("[ERROR] Тестовые пользователи не найдены")
            return False
        
        print(f"[OK] Найдены пользователи: {user1.nickname_enc}, {user2.nickname_enc}")
        
        # Проверяем существующие чаты
        chats = Chat.query.filter(
            ((Chat.user1_id == user1.id) & (Chat.user2_id == user2.id)) |
            ((Chat.user1_id == user2.id) & (Chat.user2_id == user1.id))
        ).all()
        
        print(f"[OK] Найдено чатов между пользователями: {len(chats)}")
        
        if chats:
            chat = chats[0]
            
            # Подсчитываем непрочитанные сообщения для user1
            if chat.user1_id == user1.id:
                last_read = chat.last_read_user1
            else:
                last_read = chat.last_read_user2
            
            if last_read:
                unread = Message.query.filter(
                    Message.chat_id == chat.id,
                    Message.sender_id != user1.id,
                    Message.timestamp > last_read
                ).count()
            else:
                unread = Message.query.filter(
                    Message.chat_id == chat.id,
                    Message.sender_id != user1.id
                ).count()
            
            print(f"[OK] Непрочитанных сообщений для {user1.nickname_enc}: {unread}")
        
        # Проверяем группы
        groups = Group.query.all()
        print(f"[OK] Всего групп: {len(groups)}")
        
        for group in groups:
            members = GroupMember.query.filter_by(group_id=group.id).count()
            messages = Message.query.filter_by(group_id=group.id).count()
            print(f"[OK] Группа '{group.name}': {members} участников, {messages} сообщений")
        
        print("\n[SUCCESS] Тест счетчиков завершен!")
        return True

if __name__ == '__main__':
    test_unread_counters()