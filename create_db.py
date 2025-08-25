#!/usr/bin/env python3
"""
Создание базовой базы данных
"""

import sqlite3
import os

def create_database():
    db_path = 'instance/harvest.db'
    
    # Создаем папку instance если её нет
    os.makedirs('instance', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Создаем таблицу пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname_enc VARCHAR(128) UNIQUE NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                banned BOOLEAN DEFAULT 0,
                avatar VARCHAR(256),
                public_key VARCHAR(512),
                anonymous_mode BOOLEAN DEFAULT 0,
                global_chat_key VARCHAR(128),
                global_group_key VARCHAR(128),
                harvest_tokens REAL DEFAULT 0.0
            )
        """)
        print("✓ Создана таблица user")
        
        # Создаем таблицу чатов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user1_id) REFERENCES user (id),
                FOREIGN KEY (user2_id) REFERENCES user (id)
            )
        """)
        print("✓ Создана таблица chat")
        
        # Создаем таблицу сообщений
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chat (id),
                FOREIGN KEY (sender_id) REFERENCES user (id)
            )
        """)
        print("✓ Создана таблица message")
        
        # Создаем таблицу групп
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `group` (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(128) NOT NULL,
                creator_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (creator_id) REFERENCES user (id)
            )
        """)
        print("✓ Создана таблица group")
        
        # Создаем таблицу участников групп
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_member (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES `group` (id),
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """)
        print("✓ Создана таблица group_member")
        
        # Создаем таблицу каналов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(128) NOT NULL,
                description TEXT,
                creator_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (creator_id) REFERENCES user (id)
            )
        """)
        print("✓ Создана таблица channel")
        
        # Создаем таблицу постов каналов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channel_post (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                title VARCHAR(128) NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (channel_id) REFERENCES channel (id),
                FOREIGN KEY (author_id) REFERENCES user (id)
            )
        """)
        print("✓ Создана таблица channel_post")
        
        # Создаем таблицу подписчиков каналов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channel_subscriber (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (channel_id) REFERENCES channel (id),
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """)
        print("✓ Создана таблица channel_subscriber")
        
        # Создаем таблицу комментариев к постам
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channel_comment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES channel_post (id),
                FOREIGN KEY (author_id) REFERENCES user (id)
            )
        """)
        print("✓ Создана таблица channel_comment")
        
        # Создаем таблицу отслеживания прочтения
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS read_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER,
                group_id INTEGER,
                channel_id INTEGER,
                last_read_message_id INTEGER,
                last_read_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (chat_id) REFERENCES chat (id),
                FOREIGN KEY (group_id) REFERENCES `group` (id),
                FOREIGN KEY (channel_id) REFERENCES channel (id)
            )
        """)
        print("✓ Создана таблица read_tracking")
        
        # Создаем таблицу файлов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename VARCHAR(256) NOT NULL,
                original_filename VARCHAR(256) NOT NULL,
                file_path VARCHAR(512) NOT NULL,
                file_size INTEGER,
                mime_type VARCHAR(128),
                uploaded_by INTEGER NOT NULL,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uploaded_by) REFERENCES user (id)
            )
        """)
        print("✓ Создана таблица file")
        
        # Создаем таблицу объявлений маркетплейса
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_listing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER NOT NULL,
                title VARCHAR(128) NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL,
                category VARCHAR(64) NOT NULL,
                status VARCHAR(16) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_path VARCHAR(256),
                FOREIGN KEY (seller_id) REFERENCES user (id)
            )
        """)
        print("✓ Создана таблица market_listing")
        
        # Создаем таблицу покупок
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_purchase (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL,
                buyer_id INTEGER NOT NULL,
                seller_id INTEGER NOT NULL,
                price REAL NOT NULL,
                status VARCHAR(16) DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                buyer_confirmed BOOLEAN DEFAULT 0,
                seller_confirmed BOOLEAN DEFAULT 0,
                completed_at DATETIME,
                FOREIGN KEY (listing_id) REFERENCES market_listing (id),
                FOREIGN KEY (buyer_id) REFERENCES user (id),
                FOREIGN KEY (seller_id) REFERENCES user (id)
            )
        """)
        print("✓ Создана таблица market_purchase")
        
        # Создаем таблицу транзакций токенов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS token_transaction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                transaction_type VARCHAR(32) NOT NULL,
                amount REAL NOT NULL,
                balance_before REAL NOT NULL,
                balance_after REAL NOT NULL,
                description VARCHAR(256),
                related_purchase_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (related_purchase_id) REFERENCES market_purchase (id)
            )
        """)
        print("✓ Создана таблица token_transaction")
        
        # Создаем таблицу обращений в поддержку
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS support_ticket (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject VARCHAR(128) NOT NULL,
                description TEXT NOT NULL,
                user_nickname VARCHAR(64) NOT NULL,
                scammer_nickname VARCHAR(64),
                evidence_image VARCHAR(256),
                status VARCHAR(16) DEFAULT 'open',
                admin_response TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """)
        print("✓ Создана таблица support_ticket")
        
        # Создаем индексы
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_nickname ON user(nickname_enc)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_users ON chat(user1_id, user2_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_chat ON message(chat_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_sender ON message(sender_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_group_member_group ON group_member(group_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_group_member_user ON group_member(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_channel_post_channel ON channel_post(channel_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_channel_subscriber_channel ON channel_subscriber(channel_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_channel_subscriber_user ON channel_subscriber(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_channel_comment_post ON channel_comment(post_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_read_tracking_user ON read_tracking(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_listing_seller ON market_listing(seller_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_listing_status ON market_listing(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_listing_category ON market_listing(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_purchase_buyer ON market_purchase(buyer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_purchase_seller ON market_purchase(seller_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_transaction_user ON token_transaction(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_support_ticket_user ON support_ticket(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_support_ticket_status ON support_ticket(status)")
        print("✓ Созданы индексы")
        
        conn.commit()
        print("\n🎉 База данных успешно создана!")
        print("📁 Путь: instance/harvest.db")
        
    except Exception as e:
        print(f"❌ Ошибка при создании базы данных: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_database() 