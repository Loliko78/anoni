#!/usr/bin/env python3
"""
Скрипт для миграции данных из SQLite в PostgreSQL
Используйте этот скрипт для переноса данных с локальной SQLite базы на PostgreSQL на Render
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app import app, db
from models import User, Chat, Message, File, Group, GroupMember, ReadTracking, Channel, ChannelPost, ChannelSubscriber, ChannelComment

def migrate_data():
    """Мигрирует данные из SQLite в PostgreSQL"""
    
    # Проверяем наличие переменной окружения DATABASE_URL
    if not os.environ.get('DATABASE_URL'):
        print("Ошибка: DATABASE_URL не установлена")
        print("Убедитесь, что вы запускаете этот скрипт на Render или установите DATABASE_URL")
        return False
    
    # Создаем подключение к PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    postgres_engine = create_engine(database_url)
    
    # Проверяем подключение к PostgreSQL
    try:
        with postgres_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Подключение к PostgreSQL успешно")
    except Exception as e:
        print(f"✗ Ошибка подключения к PostgreSQL: {e}")
        return False
    
    # Создаем таблицы в PostgreSQL
    with app.app_context():
        db.create_all()
        print("✓ Таблицы созданы в PostgreSQL")
    
    # Подключаемся к локальной SQLite базе
    sqlite_path = os.path.join(app.instance_path, 'harvest.db')
    if not os.path.exists(sqlite_path):
        print(f"✗ SQLite база данных не найдена: {sqlite_path}")
        return False
    
    sqlite_engine = create_engine(f'sqlite:///{sqlite_path}')
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SQLiteSession()
    
    # PostgreSQL сессия
    PostgresSession = sessionmaker(bind=postgres_engine)
    postgres_session = PostgresSession()
    
    try:
        # Мигрируем пользователей
        print("Миграция пользователей...")
        users = sqlite_session.query(User).all()
        for user in users:
            # Проверяем, не существует ли уже пользователь
            existing_user = postgres_session.query(User).filter_by(id=user.id).first()
            if not existing_user:
                new_user = User(
                    id=user.id,
                    nickname_enc=user.nickname_enc,
                    password_hash=user.password_hash,
                    avatar=user.avatar,
                    is_admin=user.is_admin,
                    banned=user.banned,
                    public_key_enc=user.public_key_enc
                )
                postgres_session.add(new_user)
        postgres_session.commit()
        print(f"✓ Мигрировано {len(users)} пользователей")
        
        # Мигрируем чаты
        print("Миграция чатов...")
        chats = sqlite_session.query(Chat).all()
        for chat in chats:
            existing_chat = postgres_session.query(Chat).filter_by(id=chat.id).first()
            if not existing_chat:
                new_chat = Chat(
                    id=chat.id,
                    user1_id=chat.user1_id,
                    user2_id=chat.user2_id,
                    key_enc=chat.key_enc
                )
                postgres_session.add(new_chat)
        postgres_session.commit()
        print(f"✓ Мигрировано {len(chats)} чатов")
        
        # Мигрируем сообщения
        print("Миграция сообщений...")
        messages = sqlite_session.query(Message).all()
        for message in messages:
            existing_message = postgres_session.query(Message).filter_by(id=message.id).first()
            if not existing_message:
                new_message = Message(
                    id=message.id,
                    chat_id=message.chat_id,
                    sender_id=message.sender_id,
                    content_enc=message.content_enc,
                    timestamp=message.timestamp,
                    is_edited=message.is_edited
                )
                postgres_session.add(new_message)
        postgres_session.commit()
        print(f"✓ Мигрировано {len(messages)} сообщений")
        
        # Мигрируем файлы
        print("Миграция файлов...")
        files = sqlite_session.query(File).all()
        for file in files:
            existing_file = postgres_session.query(File).filter_by(id=file.id).first()
            if not existing_file:
                new_file = File(
                    id=file.id,
                    message_id=file.message_id,
                    filename_enc=file.filename_enc,
                    filepath=file.filepath,
                    filesize=file.filesize,
                    mime_type=file.mime_type
                )
                postgres_session.add(new_file)
        postgres_session.commit()
        print(f"✓ Мигрировано {len(files)} файлов")
        
        # Мигрируем группы
        print("Миграция групп...")
        groups = sqlite_session.query(Group).all()
        for group in groups:
            existing_group = postgres_session.query(Group).filter_by(id=group.id).first()
            if not existing_group:
                new_group = Group(
                    id=group.id,
                    name_enc=group.name_enc,
                    invite_link_enc=group.invite_link_enc,
                    creator_id=group.creator_id,
                    avatar=group.avatar,
                    key_enc=group.key_enc
                )
                postgres_session.add(new_group)
        postgres_session.commit()
        print(f"✓ Мигрировано {len(groups)} групп")
        
        # Мигрируем участников групп
        print("Миграция участников групп...")
        group_members = sqlite_session.query(GroupMember).all()
        for member in group_members:
            existing_member = postgres_session.query(GroupMember).filter_by(
                group_id=member.group_id, 
                user_id=member.user_id
            ).first()
            if not existing_member:
                new_member = GroupMember(
                    group_id=member.group_id,
                    user_id=member.user_id
                )
                postgres_session.add(new_member)
        postgres_session.commit()
        print(f"✓ Мигрировано {len(group_members)} участников групп")
        
        # Мигрируем отслеживание прочтения
        print("Миграция отслеживания прочтения...")
        read_tracking = sqlite_session.query(ReadTracking).all()
        for tracking in read_tracking:
            existing_tracking = postgres_session.query(ReadTracking).filter_by(
                user_id=tracking.user_id,
                chat_id=tracking.chat_id
            ).first()
            if not existing_tracking:
                new_tracking = ReadTracking(
                    user_id=tracking.user_id,
                    chat_id=tracking.chat_id,
                    last_read=tracking.last_read
                )
                postgres_session.add(new_tracking)
        postgres_session.commit()
        print(f"✓ Мигрировано {len(read_tracking)} записей отслеживания прочтения")
        
        # Мигрируем каналы
        print("Миграция каналов...")
        channels = sqlite_session.query(Channel).all()
        for channel in channels:
            existing_channel = postgres_session.query(Channel).filter_by(id=channel.id).first()
            if not existing_channel:
                new_channel = Channel(
                    id=channel.id,
                    name=channel.name,
                    description=channel.description,
                    creator_id=channel.creator_id,
                    avatar=channel.avatar
                )
                postgres_session.add(new_channel)
        postgres_session.commit()
        print(f"✓ Мигрировано {len(channels)} каналов")
        
        # Мигрируем посты каналов
        print("Миграция постов каналов...")
        channel_posts = sqlite_session.query(ChannelPost).all()
        for post in channel_posts:
            existing_post = postgres_session.query(ChannelPost).filter_by(id=post.id).first()
            if not existing_post:
                new_post = ChannelPost(
                    id=post.id,
                    channel_id=post.channel_id,
                    author_id=post.author_id,
                    content=post.content,
                    timestamp=post.timestamp
                )
                postgres_session.add(new_post)
        postgres_session.commit()
        print(f"✓ Мигрировано {len(channel_posts)} постов каналов")
        
        # Мигрируем подписчиков каналов
        print("Миграция подписчиков каналов...")
        subscribers = sqlite_session.query(ChannelSubscriber).all()
        for subscriber in subscribers:
            existing_subscriber = postgres_session.query(ChannelSubscriber).filter_by(
                channel_id=subscriber.channel_id,
                user_id=subscriber.user_id
            ).first()
            if not existing_subscriber:
                new_subscriber = ChannelSubscriber(
                    channel_id=subscriber.channel_id,
                    user_id=subscriber.user_id,
                    subscribed_at=subscriber.subscribed_at
                )
                postgres_session.add(new_subscriber)
        postgres_session.commit()
        print(f"✓ Мигрировано {len(subscribers)} подписчиков каналов")
        
        # Мигрируем комментарии каналов
        print("Миграция комментариев каналов...")
        comments = sqlite_session.query(ChannelComment).all()
        for comment in comments:
            existing_comment = postgres_session.query(ChannelComment).filter_by(id=comment.id).first()
            if not existing_comment:
                new_comment = ChannelComment(
                    id=comment.id,
                    post_id=comment.post_id,
                    author_id=comment.author_id,
                    content=comment.content,
                    timestamp=comment.timestamp
                )
                postgres_session.add(new_comment)
        postgres_session.commit()
        print(f"✓ Мигрировано {len(comments)} комментариев каналов")
        
        print("\n🎉 Миграция завершена успешно!")
        print("Теперь ваше приложение будет использовать PostgreSQL на Render")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка во время миграции: {e}")
        postgres_session.rollback()
        return False
    finally:
        sqlite_session.close()
        postgres_session.close()

if __name__ == '__main__':
    print("🚀 Запуск миграции данных из SQLite в PostgreSQL...")
    print("Убедитесь, что:")
    print("1. У вас есть локальная SQLite база данных")
    print("2. Установлена переменная окружения DATABASE_URL")
    print("3. PostgreSQL база данных доступна\n")
    
    success = migrate_data()
    if success:
        print("\n✅ Миграция завершена успешно!")
        sys.exit(0)
    else:
        print("\n❌ Миграция не удалась!")
        sys.exit(1) 