from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from models import User, Message, Chat
from db import db
from datetime import datetime, timezone

# Отслеживание онлайн пользователей
online_users = set()

def init_socketio_handlers(socketio):
    
    @socketio.on('connect')
    def on_connect():
        if current_user.is_authenticated:
            online_users.add(current_user.id)
            emit('user_online', {'user_id': current_user.id}, broadcast=True)
    
    @socketio.on('disconnect')
    def on_disconnect():
        if current_user.is_authenticated:
            online_users.discard(current_user.id)
            emit('user_offline', {'user_id': current_user.id}, broadcast=True)
    
    @socketio.on('new_message')
    def handle_message(data):
        if not current_user.is_authenticated:
            return
        
        chat_id = data.get('chat_id')
        content = data.get('content', '').strip()
        
        if not content or not chat_id:
            return
        
        # Проверяем доступ к чату
        chat = db.session.get(Chat, chat_id)
        if not chat or (chat.user1_id != current_user.id and chat.user2_id != current_user.id):
            return
        
        # Создаем сообщение
        message = Message(
            chat_id=chat_id,
            sender_id=current_user.id,
            content_enc=content.encode('utf-8'),
            type='text'
        )
        db.session.add(message)
        db.session.commit()
        
        # Определяем получателя
        recipient_id = chat.user2_id if chat.user1_id == current_user.id else chat.user1_id
        
        # Отправляем сообщение
        message_data = {
            'id': message.id,
            'content': content,
            'sender_id': current_user.id,
            'sender_name': current_user.nickname_enc,
            'timestamp': message.timestamp.strftime('%H:%M'),
            'chat_id': chat_id,
            'recipient_id': recipient_id
        }
        
        emit('message_received', message_data, room=f'chat_{chat_id}')
        
        # Уведомление для получателя
        if recipient_id in online_users:
            emit('notification', {
                'title': f'Новое сообщение от {current_user.nickname_enc}',
                'body': content[:50] + ('...' if len(content) > 50 else ''),
                'chat_id': chat_id
            }, room=f'user_{recipient_id}')
    
    @socketio.on('join_chat')
    def on_join_chat(data):
        if current_user.is_authenticated:
            chat_id = data.get('chat_id')
            join_room(f'chat_{chat_id}')
            join_room(f'user_{current_user.id}')
    
    @socketio.on('leave_chat')
    def on_leave_chat(data):
        if current_user.is_authenticated:
            chat_id = data.get('chat_id')
            leave_room(f'chat_{chat_id}')
    
    return online_users