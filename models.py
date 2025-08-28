from db import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, LargeBinary, Text
from sqlalchemy.orm import relationship
import datetime

class User(UserMixin, db.Model):
    id = Column(Integer, primary_key=True)
    nickname_enc = Column(String(64), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    banned = Column(Boolean, default=False)
    public_key = Column(LargeBinary, nullable=True)
    avatar = Column(String(128), nullable=True)
    anonymous_mode = Column(Boolean, default=True)
    global_chat_key = Column(String(128), nullable=True)
    global_group_key = Column(String(128), nullable=True)
    blocked_users = Column(Text, nullable=True)  # JSON string of blocked user IDs
    last_seen = Column(DateTime, nullable=True)
    is_online = Column(Boolean, default=False)
    chats1 = relationship('Chat', foreign_keys='Chat.user1_id', backref='user1', lazy=True)
    chats2 = relationship('Chat', foreign_keys='Chat.user2_id', backref='user2', lazy=True)
    support_tickets = relationship('SupportTicket', backref='user', lazy=True)
    
    @property
    def encrypted_nickname(self):
        """Return the encrypted nickname (for template compatibility)"""
        return self.nickname_enc

class Chat(db.Model):
    id = Column(Integer, primary_key=True)
    user1_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    key_enc = Column(LargeBinary, nullable=True)
    session_key = Column(LargeBinary, nullable=True)
    session_expires = Column(DateTime, nullable=True)
    last_read_user1 = Column(DateTime, nullable=True)
    last_read_user2 = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    messages = relationship('Message', backref='chat', lazy=True)

class Group(db.Model):
    id = Column(Integer, primary_key=True)
    name_enc = Column(String(128), nullable=False)
    invite_link_enc = Column(String(128), nullable=False, unique=True)
    creator_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    session_key = Column(LargeBinary, nullable=True)
    session_expires = Column(DateTime, nullable=True)
    avatar = Column(String(128), nullable=True)
    description = Column(String(512), nullable=True)
    messages = relationship('Message', backref='group', lazy=True)
    
    @property
    def name(self):
        """Get group name"""
        return self.name_enc or "Unknown Group"
    
    @property
    def invite_link(self):
        """Get invite link"""
        return self.invite_link_enc or ""
    
    @property
    def members(self):
        """Get group members"""
        return GroupMember.query.filter_by(group_id=self.id).all()

class Message(db.Model):
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chat.id'), nullable=True)
    group_id = Column(Integer, ForeignKey('group.id'), nullable=True)
    sender_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    content_enc = Column(LargeBinary, nullable=False)
    type = Column(String(16), default='text')
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    deleted = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    session_id = Column(String(64), nullable=True)
    file_id = Column(Integer, ForeignKey('file.id'), nullable=True)
    file = relationship('File', backref='messages')
    sender = relationship('User', backref='messages')

class File(db.Model):
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(100), nullable=False)
    uploaded_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

class GroupMember(db.Model):
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('group.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    last_read = Column(DateTime, nullable=True)
    user = relationship('User', backref='group_memberships')

class ReadTracking(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    chat_id = Column(Integer, ForeignKey('chat.id'), nullable=False)
    last_read = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))

class Channel(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256), nullable=True)
    creator_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    avatar = Column(String(128), nullable=True)
    key_enc = Column(LargeBinary, nullable=True)
    deleted = Column(db.Boolean, default=False)
    posts = relationship('ChannelPost', backref='channel', lazy='dynamic')

class ChannelPost(db.Model):
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channel.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    content = Column(String(2048), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    author = relationship('User', backref='channel_posts', lazy='joined')
    comments = relationship('ChannelComment', backref='post', lazy='dynamic', cascade='all, delete-orphan')

class ChannelComment(db.Model):
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('channel_post.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    content = Column(String(1024), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    author = relationship('User', backref='channel_comments', lazy='joined')

class ChannelSubscriber(db.Model):
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channel.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    subscribed_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    user = relationship('User', backref='channel_subscriptions', lazy='joined')

class SupportTicket(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    subject = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    user_nickname = Column(String(64), nullable=False)
    scammer_nickname = Column(String(64), nullable=True)
    evidence_image = Column(String(256), nullable=True)
    status = Column(String(16), default='open')
    admin_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc)) 