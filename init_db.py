#!/usr/bin/env python3
"""
Initialize database using SQLAlchemy models
"""

import os
import sys
from app import app, db
from models import User, Chat, Message, File, Group, GroupMember, ReadTracking, Channel, ChannelPost, ChannelSubscriber, ChannelComment, SupportTicket

def init_database():
    """Initialize the database with all tables"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully!")
            
            # Check if admin user exists
            admin_user = User.query.filter_by(nickname_enc='azazel').first()
            if not admin_user:
                from werkzeug.security import generate_password_hash
                admin_user = User(
                    nickname_enc='azazel',
                    password_hash=generate_password_hash('Log1progress'),
                    is_admin=True,
                    banned=False
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✓ Admin user 'azazel' created!")
            else:
                print("✓ Admin user already exists")
                
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    init_database() 