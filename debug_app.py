#!/usr/bin/env python3
"""
Debug version of the app with detailed logging
"""

import logging
import traceback
from flask import Flask, render_template, redirect, url_for, flash, request, send_file, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, timedelta, timezone
import sqlite3
from models import User, Chat, Message, File, Group, GroupMember, ReadTracking, Channel, ChannelPost, ChannelSubscriber, ChannelComment, SupportTicket
from db import db

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/harvest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Flask configuration for URL building
app.config['SERVER_NAME'] = 'localhost:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        logger.debug(f"Loading user with ID: {user_id}")
        user = User.query.get(int(user_id))
        logger.debug(f"User loaded: {user}")
        return user
    except Exception as e:
        logger.error(f"Error loading user {user_id}: {e}")
        logger.error(traceback.format_exc())
        return None

@app.before_request
def check_ban():
    try:
        logger.debug(f"Before request: {request.endpoint}")
        if current_user.is_authenticated and current_user.banned:
            logger.warning(f"Banned user {current_user.id} attempted to access {request.endpoint}")
            logout_user()
            flash('Ваш аккаунт заблокирован', 'danger')
            return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"Error in check_ban: {e}")
        logger.error(traceback.format_exc())

@app.route('/')
def index():
    try:
        logger.debug("Accessing index route")
        if current_user.is_authenticated:
            logger.debug(f"User {current_user.id} is authenticated, redirecting to chats")
            return redirect(url_for('chats'))
        else:
            logger.debug("User not authenticated, showing login page")
            return render_template('login.html')
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        logger.error(traceback.format_exc())
        return "Internal Server Error", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        logger.debug("Accessing login route")
        if request.method == 'POST':
            logger.debug("Processing login POST request")
            username = request.form.get('username')
            password = request.form.get('password')
            logger.debug(f"Login attempt for username: {username}")
            
            user = User.query.filter_by(nickname_enc=username).first()
            if user and check_password_hash(user.password_hash, password):
                logger.debug(f"Login successful for user {user.id}")
                login_user(user)
                return redirect(url_for('chats'))
            else:
                logger.warning(f"Login failed for username: {username}")
                flash('Неверное имя пользователя или пароль', 'error')
        
        logger.debug("Rendering login template")
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Error in login route: {e}")
        logger.error(traceback.format_exc())
        return "Internal Server Error", 500

@app.route('/logout')
@login_required
def logout():
    try:
        logger.debug(f"Logout for user {current_user.id}")
        logout_user()
        return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"Error in logout route: {e}")
        logger.error(traceback.format_exc())
        return "Internal Server Error", 500

@app.route('/chats')
@login_required
def chats():
    try:
        logger.debug(f"Accessing chats route for user {current_user.id}")
        user_chats = Chat.query.filter(
            (Chat.user1_id == current_user.id) | (Chat.user2_id == current_user.id)
        ).all()
        
        user_groups = Group.query.join(GroupMember).filter(GroupMember.user_id == current_user.id).all()
        
        logger.debug(f"Found {len(user_chats)} chats and {len(user_groups)} groups")
        return render_template('chats.html', chats=user_chats, groups=user_groups)
    except Exception as e:
        logger.error(f"Error in chats route: {e}")
        logger.error(traceback.format_exc())
        return "Internal Server Error", 500

@app.route('/search')
def search():
    try:
        logger.debug("Accessing search route")
        query = request.args.get('q', '')
        results = []
        
        if query:
            logger.debug(f"Searching for: {query}")
            # Add search logic here
            pass
        
        return render_template('search.html', results=results, query=query)
    except Exception as e:
        logger.error(f"Error in search route: {e}")
        logger.error(traceback.format_exc())
        return "Internal Server Error", 500

@app.route('/profile')
@login_required
def profile():
    try:
        logger.debug(f"Accessing profile route for user {current_user.id}")
        return render_template('profile.html')
    except Exception as e:
        logger.error(f"Error in profile route: {e}")
        logger.error(traceback.format_exc())
        return "Internal Server Error", 500

@app.route('/admin')
@login_required
def admin():
    try:
        logger.debug(f"Accessing admin route for user {current_user.id}")
        if not current_user.is_admin:
            logger.warning(f"Non-admin user {current_user.id} attempted to access admin")
            abort(403)
        
        users = User.query.all()
        return render_template('admin.html', users=users)
    except Exception as e:
        logger.error(f"Error in admin route: {e}")
        logger.error(traceback.format_exc())
        return "Internal Server Error", 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 error: {error}")
    return render_template('error.html', error_code=404, error_message="Страница не найдена"), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    logger.error(traceback.format_exc())
    db.session.rollback()
    return render_template('error.html', error_code=500, error_message="Внутренняя ошибка сервера"), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    logger.error(traceback.format_exc())
    return render_template('error.html', error_code=500, error_message="Неожиданная ошибка"), 500

if __name__ == '__main__':
    logger.info("Starting debug Flask application...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 