#!/usr/bin/env python3
"""
Test database connection and schema
"""

from app import app, db
from models import User, Chat, Message

def test_database():
    with app.app_context():
        try:
            # Test basic database connection
            print("Testing database connection...")
            from sqlalchemy import text
            result = db.session.execute(text("SELECT 1")).fetchone()
            print(f"✓ Database connection successful: {result}")
            
            # Test User model
            print("\nTesting User model...")
            users = User.query.limit(1).all()
            print(f"✓ User query successful: {len(users)} users found")
            
            # Test Chat model
            print("\nTesting Chat model...")
            chats = Chat.query.limit(1).all()
            print(f"✓ Chat query successful: {len(chats)} chats found")
            
            # Test Message model
            print("\nTesting Message model...")
            messages = Message.query.limit(1).all()
            print(f"✓ Message query successful: {len(messages)} messages found")
            
            # Test blocked_users field
            print("\nTesting blocked_users field...")
            user = User.query.first()
            if user:
                print(f"✓ User found: {user.nickname_enc}")
                print(f"✓ blocked_users field: {user.blocked_users}")
            else:
                print("⚠ No users found in database")
            
            print("\n🎉 All database tests passed!")
            
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_database() 