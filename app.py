from flask import Flask, render_template, redirect, url_for, flash, request, send_file, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import json
from simple_forms import RegisterForm, LoginForm
from models import User, Chat, Message, File, Group, GroupMember, ReadTracking, Channel, ChannelPost, ChannelSubscriber, ChannelComment, SupportTicket
import mimetypes
import uuid
import logging
from db import db
from sqlalchemy import or_, func, and_
from werkzeug.utils import secure_filename
import time
from datetime import datetime, timedelta, timezone
import random
import base64
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = 'your-secret-key-here'
# PostgreSQL через ngrok или локальная SQLite
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///harvest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
# app.config['SERVER_NAME'] = 'localhost:5000'
# app.config['APPLICATION_ROOT'] = '/'
# app.config['PREFERRED_URL_SCHEME'] = 'http'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Отслеживание онлайн пользователей
online_users = set()

@socketio.on('connect')
def on_connect():
    if current_user.is_authenticated:
        online_users.add(current_user.id)
        if hasattr(current_user, 'is_online'):
            current_user.is_online = True
        if hasattr(current_user, 'last_seen'):
            current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        socketio.emit('user_online', {'user_id': current_user.id})
        join_room(f'user_{current_user.id}')

@socketio.on('disconnect')
def on_disconnect():
    if current_user.is_authenticated:
        online_users.discard(current_user.id)
        if hasattr(current_user, 'is_online'):
            current_user.is_online = False
        if hasattr(current_user, 'last_seen'):
            current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        socketio.emit('user_offline', {'user_id': current_user.id})
        leave_room(f'user_{current_user.id}')

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
    
    # Отправляем уведомление
    socketio.emit('notification', {
        'title': f'Новое сообщение от {current_user.nickname_enc}',
        'body': content[:50] + ('...' if len(content) > 50 else ''),
        'chat_id': chat_id
    }, room=f'user_{recipient_id}')

# Инициализация базы данных
with app.app_context():
    try:
        db.create_all()
        print("Database initialized")
        
        # Создаем админа если его нет
        admin = User.query.filter_by(nickname_enc='azazel').first()
        if not admin:
            admin = User(
                nickname_enc='azazel',
                password_hash=generate_password_hash('Log1progress'),
                is_admin=True
            )
            db.session.add(admin)
            print("Admin user created")
        
        # Создаем бота если его нет
        bot = User.query.filter_by(nickname_enc='Harvest').first()
        if not bot:
            bot = User(
                nickname_enc='Harvest',
                password_hash=generate_password_hash('826945214')
            )
            db.session.add(bot)
            print("Bot user created")
        
        db.session.commit()
        
        # Автобэкап каждый час
        import threading
        import time
        
        def auto_backup():
            while True:
                time.sleep(3600)  # 1 час
                try:
                    from telegram_backup import backup_database
                    backup_database()
                except Exception as e:
                    print(f"Backup error: {e}")
        
        if os.environ.get('PORT'):  # Только в продакшене
            backup_thread = threading.Thread(target=auto_backup, daemon=True)
            backup_thread.start()
            
    except Exception as e:
        print(f"Warning during DB init: {e}")

# Отключаем все логи Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app.logger.disabled = True

# Проверка HTTPS (или Tor)
@app.before_request
def enforce_https():
    # Временно отключаем для тестирования
    return None

## Удалены устаревшие ключи и настройки сильной анонимности

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def check_bruteforce_protection():
    """Защита от брутфорса - ограничение попыток входа"""
    ip = request.remote_addr
    current_time = time.time()
    
    # Очищаем старые попытки (старше 15 минут)
    if 'login_attempts' not in session:
        session['login_attempts'] = {}
    
    attempts = session['login_attempts']
    attempts = {k: v for k, v in attempts.items() if current_time - v['time'] < 900}
    
    if ip in attempts:
        if attempts[ip]['count'] >= 5:  # Максимум 5 попыток
            if current_time - attempts[ip]['time'] < 900:  # Блокировка на 15 минут
                return False
            else:
                attempts[ip]['count'] = 0
    
    return True

def record_login_attempt(ip, success):
    """Записываем попытку входа"""
    current_time = time.time()
    
    if 'login_attempts' not in session:
        session['login_attempts'] = {}
    
    attempts = session['login_attempts']
    
    if ip not in attempts:
        attempts[ip] = {'count': 0, 'time': current_time}
    
    if not success:
        attempts[ip]['count'] += 1
        attempts[ip]['time'] = current_time
    
    session['login_attempts'] = attempts

@socketio.on('join_chat')
def on_join_chat(data):
    if current_user.is_authenticated:
        chat_id = data.get('chat_id')
        join_room(f'chat_{chat_id}')
        join_room(f'user_{current_user.id}')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if not check_bruteforce_protection():
        flash('Слишком много попыток входа. Попробуйте позже.', 'error')
        return render_template('register.html')
    
    form = RegisterForm(request.form)
    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return render_template('register_minimal.html', form=form)
        
        password_hash = generate_password_hash(password)
        
        if User.query.filter_by(nickname_enc=nickname).first():
            flash('Пользователь с таким ником уже существует', 'danger')
            return render_template('register_minimal.html', form=form)
        
        user = User(nickname_enc=nickname, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register_minimal.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(nickname_enc=nickname).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user.banned:
                flash('Ваш аккаунт заблокирован', 'danger')
                return render_template('login.html')
            
            # Обновляем статус пользователя
            if hasattr(user, 'is_online'):
                user.is_online = True
            if hasattr(user, 'last_seen'):
                user.last_seen = datetime.now(timezone.utc)
            db.session.commit()
            
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Неверный никнейм или пароль', 'danger')
    
    return render_template('login_minimal.html')

@app.route('/logout')
@login_required
def logout():
    # Обновляем статус пользователя
    if hasattr(current_user, 'is_online'):
        current_user.is_online = False
    if hasattr(current_user, 'last_seen'):
        current_user.last_seen = datetime.now(timezone.utc)
    db.session.commit()
    
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/chats')
@login_required
def index():
    try:
        # Получаем все чаты пользователя
        try:
            chats = Chat.query.filter(
                (Chat.user1_id == current_user.id) | (Chat.user2_id == current_user.id)
            ).order_by(Chat.last_activity.desc().nullslast()).all()
        except:
            chats = Chat.query.filter(
                (Chat.user1_id == current_user.id) | (Chat.user2_id == current_user.id)
            ).all()
        
        # Получаем информацию о других пользователях в чатах
        chat_users = {}
        unread_counts = {}
        for chat in chats:
            try:
                if chat.user1_id == current_user.id:
                    other_user = chat.user2
                    last_read = chat.last_read_user1
                else:
                    other_user = chat.user1
                    last_read = chat.last_read_user2
                chat_users[chat.id] = other_user
                
                # Подсчитываем непрочитанные сообщения
                if last_read:
                    unread = Message.query.filter(
                        Message.chat_id == chat.id,
                        Message.sender_id != current_user.id,
                        Message.timestamp > last_read
                    ).count()
                else:
                    unread = Message.query.filter(
                        Message.chat_id == chat.id,
                        Message.sender_id != current_user.id
                    ).count()
                unread_counts[chat.id] = unread
            except Exception as e:
                print(f"Error processing chat {chat.id}: {e}")
                continue
        
        # Получаем группы пользователя
        try:
            group_memberships = GroupMember.query.filter_by(user_id=current_user.id).all()
            groups = []
            group_unread = {}
            for membership in group_memberships:
                group = db.session.get(Group, membership.group_id)
                if group:
                    groups.append(group)
                    # Подсчитываем непрочитанные сообщения в группе
                    if membership.last_read:
                        unread = Message.query.filter(
                            Message.group_id == group.id,
                            Message.sender_id != current_user.id,
                            Message.timestamp > membership.last_read
                        ).count()
                    else:
                        unread = Message.query.filter(
                            Message.group_id == group.id,
                            Message.sender_id != current_user.id
                        ).count()
                    group_unread[group.id] = unread
        except:
            groups = []
            group_unread = {}
        
        # Получаем каналы
        try:
            channels = Channel.query.filter_by(deleted=False).all()
            channel_unread = {}
            for channel in channels:
                # Подсчитываем новые посты в канале (за последние 24 часа)
                day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
                new_posts = ChannelPost.query.filter(
                    ChannelPost.channel_id == channel.id,
                    ChannelPost.timestamp > day_ago
                ).count()
                channel_unread[channel.id] = new_posts
        except:
            channels = []
            channel_unread = {}
        
        return render_template('chats_minimal.html', 
                             chats=chats, 
                             chat_users=chat_users,
                             unread_counts=unread_counts,
                             online_users=online_users,
                             groups=groups,
                             group_unread=group_unread,
                             channels=channels,
                             channel_unread=channel_unread)
    except Exception as e:
        print(f"Error in index: {e}")
        return render_template('chats_minimal.html', 
                             chats=[], 
                             chat_users={},
                             unread_counts={},
                             online_users=set(),
                             groups=[],
                             group_unread={},
                             channels=[],
                             channel_unread={})

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query:
            flash('Введите поисковый запрос', 'error')
            return redirect(url_for('search'))
        
        # Поиск пользователей по никнейму
        users = User.query.filter(
            User.nickname_enc.like(f'%{query}%'),
            User.id != current_user.id,
            User.banned == False
        ).limit(10).all()
        
        # Поиск каналов
        channels = Channel.query.filter(
            Channel.name.like(f'%{query}%'),
            Channel.deleted == False
        ).limit(10).all()
        
        return render_template('search_minimal.html', users=users, channels=channels, query=query)
    
    return render_template('search_minimal.html')

@app.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
@login_required
def chat(chat_id):
    chat = db.session.get(Chat, chat_id)
    if not chat:
        abort(404)
    
    # Проверяем, что пользователь участвует в чате
    if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
        abort(403)

    # Получаем другого пользователя
    if chat.user1_id == current_user.id:
        other_user = chat.user2
    else:
        other_user = chat.user1
    
    # Получаем сообщения
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    
    # Отмечаем сообщения как прочитанные
    if chat.user1_id == current_user.id:
        chat.last_read_user1 = datetime.now(timezone.utc)
    else:
        chat.last_read_user2 = datetime.now(timezone.utc)
    db.session.commit()
    
    # Уведомляем всех пользователей об обновлении счетчиков
    socketio.emit('chat_read', {'chat_id': chat_id})
    
    return render_template('chat_minimal.html', 
                         chat=chat, 
                         other_user=other_user, 
                         messages=messages)

@app.route('/file/<int:file_id>')
@login_required
def download_file(file_id):
    file = db.session.get(File, file_id)
    if not file:
        abort(404)
    
    # Проверяем права доступа
    message = file.message
    if message.chat_id:
        chat = db.session.get(Chat, message.chat_id)
        if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
            abort(403)
    elif message.group_id:
        group_member = GroupMember.query.filter_by(
            group_id=message.group_id, 
            user_id=current_user.id
        ).first()
        if not group_member:
            abort(403)
    else:
        abort(403)
    
    # Расшифровываем имя файла
    filename = file.filename_enc.decode('utf-8')  # Упрощенно для демо
    
    file_path = os.path.join(app.static_folder, file.path_enc.decode('utf-8'))
    
    if not os.path.exists(file_path):
        abort(404)
    
    return send_file(file_path, as_attachment=True, download_name=filename)

@app.route('/file/<int:file_id>/view')
@login_required
def view_file(file_id):
    file = db.session.get(File, file_id)
    if not file:
        abort(404)
    
    # Проверяем права доступа
    message = file.message
    if message.chat_id:
        chat = db.session.get(Chat, message.chat_id)
        if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
            abort(403)
    elif message.group_id:
        group_member = GroupMember.query.filter_by(
            group_id=message.group_id, 
            user_id=current_user.id
        ).first()
        if not group_member:
            abort(403)
    else:
        abort(403)
    
    file_path = os.path.join(app.static_folder, file.path_enc.decode('utf-8'))
    
    if not os.path.exists(file_path):
        abort(404)
    
    return send_file(file_path)

@app.route('/message/delete/<int:msg_id>', methods=['POST'])
@login_required
def delete_message(msg_id):
    message = db.session.get(Message, msg_id)
    if not message:
        abort(404)
    
    # Проверяем права доступа
    if message.sender_id != current_user.id:
        abort(403)
    
    # Полностью удаляем сообщение из базы данных
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/message/edit/<int:msg_id>', methods=['POST'])
@login_required
def edit_message(msg_id):
    message = db.session.get(Message, msg_id)
    if not message:
        abort(404)
    
    # Проверяем права доступа
    if message.sender_id != current_user.id:
        abort(403)
    
    new_content = request.form.get('content', '').strip()
    if not new_content:
        return jsonify({'success': False, 'message': 'Сообщение не может быть пустым'})
    
    message.content_enc = new_content.encode('utf-8')
    message.is_edited = True
    message.edited_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify({'success': True}) 

@app.route('/admin')
@login_required
def admin_panel():
    try:
        if not current_user.is_admin:
            flash('Доступ запрещен', 'error')
            return redirect(url_for('index'))
        
        users = User.query.all()
        tickets = SupportTicket.query.order_by(SupportTicket.created_at.desc()).all()
        return render_template('admin_minimal.html', users=users, tickets=tickets)
    except Exception as e:
        print(f"Error in admin_panel: {e}")
        return render_template('admin_minimal.html', users=[], tickets=[])

@app.route('/admin/promote/<int:user_id>', methods=['POST'])
@login_required
def admin_promote(user_id):
    if not current_user.is_admin or current_user.nickname_enc != 'azazel':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('admin_panel'))
    
    user = db.session.get(User, user_id)
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('admin_panel'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'назначен админом' if user.is_admin else 'снят с админки'
    flash(f'Пользователь {user.nickname_enc} {status}', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/ban/<int:user_id>', methods=['POST'])
@login_required
def admin_ban(user_id):
    if not current_user.is_admin:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('admin_panel'))
    
    user = db.session.get(User, user_id)
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('admin_panel'))
    
    user.banned = not user.banned
    db.session.commit()
    
    status = 'заблокирован' if user.banned else 'разблокирован'
    flash(f'Пользователь {user.nickname_enc} {status}', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_chat/<int:chat_id>', methods=['POST'])
@login_required
def admin_delete_chat(chat_id):
    # Только для azazel
    if not current_user.is_admin or current_user.nickname_enc != 'azazel':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('admin_panel'))
    
    chat = db.session.get(Chat, chat_id)
    if not chat:
        flash('Чат не найден', 'error')
        return redirect(url_for('admin_panel'))
    
    db.session.delete(chat)
    db.session.commit()
    
    flash('Чат удален', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/group/create', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        name = request.form.get('group_name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Название группы не может быть пустым', 'error')
            return render_template('create_group_minimal.html')
        
        # Генерируем уникальную ссылку-приглашение
        invite_link = base64.b64encode(os.urandom(16)).decode('utf-8').replace('/', '_').replace('+', '-')
        
        # Создаем группу
        group = Group(
            name_enc=name,
            invite_link_enc=invite_link,
            creator_id=current_user.id,
            description=description
        )
        db.session.add(group)
        db.session.commit()
        
        # Добавляем создателя как участника
        member = GroupMember(group_id=group.id, user_id=current_user.id)
        db.session.add(member)
        db.session.commit()
        
        flash('Группа создана!', 'success')
        return redirect(url_for('index'))
    
    return render_template('create_group_minimal.html')

@app.route('/group/join/<invite_link>')
@login_required
def join_group(invite_link):
    # Находим группу по invite_link
    group = Group.query.filter_by(invite_link_enc=invite_link).first()
    if not group:
        flash('Группа не найдена', 'error')
        return redirect(url_for('index'))
    
    # Проверяем, не состоит ли уже пользователь в группе
    existing_member = GroupMember.query.filter_by(
        group_id=group.id, 
        user_id=current_user.id
    ).first()
    
    if existing_member:
        flash('Вы уже состоите в этой группе', 'info')
        return redirect(url_for('group_chat', invite_link=invite_link))
    
    # Добавляем пользователя в группу
    member = GroupMember(group_id=group.id, user_id=current_user.id)
    db.session.add(member)
    db.session.commit()
    
    flash('Вы присоединились к группе!', 'success')
    return redirect(url_for('index'))

@app.route('/group/<invite_link>', methods=['GET', 'POST'])
@login_required
def group_chat(invite_link):
    # Находим группу по invite_link
    group = Group.query.filter_by(invite_link_enc=invite_link).first()
    if not group:
        abort(404)
    
    # Проверяем, состоит ли пользователь в группе
    member = GroupMember.query.filter_by(
        group_id=group.id, 
        user_id=current_user.id
    ).first()
    
    if not member:
        flash('Вы не состоите в этой группе', 'error')
        return redirect(url_for('index'))

    # Получаем сообщения группы
    messages = Message.query.filter_by(group_id=group.id).order_by(Message.timestamp).all()
    
    # Получаем участников группы
    members = GroupMember.query.filter_by(group_id=group.id).all()
    member_users = [member.user for member in members]
    
    # Отмечаем сообщения как прочитанные
    member.last_read = datetime.now(timezone.utc)
    db.session.commit()
    
    return render_template('group_chat_minimal.html', 
                         group=group, 
                         messages=messages,
                         members=member_users)

@app.route('/admin/delete_group/<int:group_id>', methods=['POST'])
@login_required
def admin_delete_group(group_id):
    # Только для azazel
    if not current_user.is_admin or current_user.nickname_enc != 'azazel':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('admin_panel'))
    
    group = db.session.get(Group, group_id)
    if not group:
        flash('Группа не найдена', 'error')
        return redirect(url_for('admin_panel'))
    
    db.session.delete(group)
    db.session.commit()
    
    flash('Группа удалена', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/group/<invite_link>/messages')
@login_required
def get_group_messages(invite_link):
    # Находим группу по invite_link
    group = Group.query.filter_by(invite_link_enc=invite_link).first()
    if not group:
        return jsonify({'error': 'Группа не найдена'})
    
    # Проверяем, состоит ли пользователь в группе
    member = GroupMember.query.filter_by(
        group_id=group.id, 
        user_id=current_user.id
    ).first()
    
    if not member:
        return jsonify({'error': 'Доступ запрещен'})
    
    # Получаем сообщения
    messages = Message.query.filter_by(group_id=group.id).order_by(Message.timestamp).all()
    
    # Формируем ответ
    messages_data = []
    for msg in messages:
        sender = db.session.get(User, msg.sender_id)
        messages_data.append({
        'id': msg.id,
            'content': msg.content_enc.decode('utf-8'),
            'sender': sender.nickname_enc,
        'timestamp': msg.timestamp.isoformat(),
            'is_edited': msg.is_edited,
        'deleted': msg.deleted
        })
    
    return jsonify({'messages': messages_data})

@app.route('/chat/<int:chat_id>/messages')
@login_required
def get_chat_messages(chat_id):
    chat = db.session.get(Chat, chat_id)
    if not chat:
        return jsonify({'error': 'Чат не найден'})
    
    # Проверяем, что пользователь участвует в чате
    if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
        return jsonify({'error': 'Доступ запрещен'})
    
    # Получаем сообщения
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    
    # Формируем ответ
    messages_data = []
    for msg in messages:
        sender = db.session.get(User, msg.sender_id)
        messages_data.append({
        'id': msg.id,
            'content': msg.content_enc.decode('utf-8'),
            'sender': sender.nickname_enc,
        'timestamp': msg.timestamp.isoformat(),
            'is_edited': msg.is_edited,
        'deleted': msg.deleted
        })
    
    return jsonify({'messages': messages_data})

@app.route('/group/delete/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    group = db.session.get(Group, group_id)
    if not group:
        flash('Группа не найдена', 'error')
        return redirect(url_for('index'))
    
    # Проверяем, является ли пользователь создателем группы
    if group.creator_id != current_user.id:
        flash('Только создатель группы может её удалить', 'error')
        return redirect(url_for('group_chat', invite_link=group.invite_link_enc.decode('utf-8')))
    
    db.session.delete(group)
    db.session.commit()
    
    flash('Группа удалена', 'success')
    return redirect(url_for('index'))

@app.before_request
def check_ban():
    if current_user.is_authenticated and current_user.banned:
        logout_user()
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('login'))

@app.before_request
def update_last_seen():
    if current_user.is_authenticated:
        if hasattr(current_user, 'last_seen'):
            current_user.last_seen = datetime.now(timezone.utc)
        if hasattr(current_user, 'is_online'):
            current_user.is_online = True
        db.session.commit()
        
        # Обновляем статус других пользователей (офлайн если неактивны > 5 секунд)
        offline_time = datetime.now(timezone.utc) - timedelta(seconds=10)
        try:
            db.session.query(User).filter(
                User.last_seen < offline_time,
                User.is_online == True
            ).update({'is_online': False})
            db.session.commit()
        except:
            pass

@app.route('/group/<invite_link>/remove_member/<int:user_id>', methods=['POST'])
@login_required
def remove_group_member(invite_link, user_id):
    # Находим группу по invite_link
    group = Group.query.filter_by(invite_link_enc=invite_link).first()
    if not group:
        flash('Группа не найдена', 'error')
        return redirect(url_for('index'))
    
    # Проверяем, является ли пользователь создателем группы
    if group.creator_id != current_user.id:
        flash('Только создатель группы может удалять участников', 'error')
        return redirect(url_for('group_chat', invite_link=invite_link))
    
    # Находим участника
    member = GroupMember.query.filter_by(
        group_id=group.id, 
        user_id=user_id
    ).first()
    
    if not member:
        flash('Участник не найден', 'error')
        return redirect(url_for('group_chat', invite_link=invite_link))
    
    # Нельзя удалить создателя группы
    if user_id == group.creator_id:
        flash('Нельзя удалить создателя группы', 'error')
        return redirect(url_for('group_chat', invite_link=invite_link))
    
    db.session.delete(member)
    db.session.commit()
    
    flash('Участник удален из группы', 'success')
    return redirect(url_for('group_chat', invite_link=invite_link))

@app.route('/group/<invite_link>/copy_link', methods=['POST'])
@login_required
def copy_group_link(invite_link):
    # Находим группу по invite_link
    group = Group.query.filter_by(invite_link_enc=invite_link).first()
    if not group:
        return jsonify({'success': False, 'message': 'Группа не найдена'})
    
    # Проверяем, состоит ли пользователь в группе
    member = GroupMember.query.filter_by(
        group_id=group.id, 
        user_id=current_user.id
    ).first()
    
    if not member:
        return jsonify({'success': False, 'message': 'Доступ запрещен'})
    
    # Формируем полную ссылку
    full_link = request.host_url.rstrip('/') + url_for('join_group', invite_link=invite_link)
    
    return jsonify({'success': True, 'link': full_link})

@app.route('/group/<invite_link>/settings', methods=['GET', 'POST'])
@login_required
def group_settings(invite_link):
    group = Group.query.filter_by(invite_link_enc=invite_link).first()
    if not group:
        abort(404)
    
    if group.creator_id != current_user.id:
        flash('Только создатель может изменять настройки группы', 'error')
        return redirect(url_for('group_chat', invite_link=invite_link))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if name:
            group.name_enc = name
        if description:
            group.description = description
            
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                filename = secure_filename(f"group_{group.id}_{uuid.uuid4().hex}_{file.filename}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                group.avatar = f"uploads/{filename}"
        
        db.session.commit()
        flash('Настройки группы обновлены', 'success')
        return redirect(url_for('group_chat', invite_link=invite_link))
    
    members = GroupMember.query.filter_by(group_id=group.id).all()
    return render_template('group_settings_minimal.html', group=group, members=members)

@app.route('/group/<invite_link>/members')
@login_required
def group_members(invite_link):
    # Находим группу по invite_link
    group = Group.query.filter_by(invite_link_enc=invite_link).first()
    if not group:
        flash('Группа не найдена', 'error')
        return redirect(url_for('index'))
    
    # Проверяем, состоит ли пользователь в группе
    member = GroupMember.query.filter_by(
        group_id=group.id, 
        user_id=current_user.id
    ).first()
    
    if not member:
        flash('Вы не состоите в этой группе', 'error')
        return redirect(url_for('index'))
    
    # Получаем участников группы
    members = GroupMember.query.filter_by(group_id=group.id).all()
    member_users = [member.user for member in members]
    
    return render_template('group_members.html', 
                         group=group, 
                         members=member_users)

@app.route('/group/<invite_link>/invite_by_nickname', methods=['POST'])
@login_required
def invite_by_nickname(invite_link):
    # Находим группу по invite_link
    group = Group.query.filter_by(invite_link_enc=invite_link).first()
    if not group:
        flash('Группа не найдена', 'error')
        return redirect(url_for('index'))
    
    # Проверяем, состоит ли пользователь в группе
    member = GroupMember.query.filter_by(
        group_id=group.id, 
        user_id=current_user.id
    ).first()
    
    if not member:
        flash('Вы не состоите в этой группе', 'error')
        return redirect(url_for('index'))
    
    nickname = request.form.get('nickname', '').strip()
    if not nickname:
        flash('Введите никнейм пользователя', 'error')
        return redirect(url_for('group_members', invite_link=invite_link))
    
    # Находим пользователя
    user = User.query.filter_by(nickname_enc=nickname).first()
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('group_members', invite_link=invite_link))
    
    # Проверяем, не состоит ли уже пользователь в группе
    existing_member = GroupMember.query.filter_by(
        group_id=group.id, 
        user_id=user.id
    ).first()
    
    if existing_member:
        flash('Пользователь уже состоит в группе', 'info')
        return redirect(url_for('group_members', invite_link=invite_link))
    
    # Добавляем пользователя в группу
    new_member = GroupMember(group_id=group.id, user_id=user.id)
    db.session.add(new_member)
    db.session.commit()
    
    flash(f'Пользователь {nickname} добавлен в группу', 'success')
    return redirect(url_for('group_members', invite_link=invite_link)) 

## Удалена система публичных ключей

## Удалено обновление публичного ключа

## Удалена синхронизация ключей в чатах

## Удалена генерация пользовательских ключей

## Удалена генерация пользовательских ключей (JSON)

@app.route('/api/user_status/<int:user_id>')
@login_required
def get_user_status(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден'})
    
    return jsonify({
        'user_id': user.id,
        'is_online': getattr(user, 'is_online', False),
        'last_seen': getattr(user, 'last_seen', None).isoformat() if getattr(user, 'last_seen', None) else None
    })

@app.route('/api/push/subscribe', methods=['POST'])
@login_required
def push_subscribe():
    """Подписка на push-уведомления"""
    subscription = request.get_json()
    
    # Сохраняем подписку в базе данных (упрощенно - в поле пользователя)
    if hasattr(current_user, 'push_subscription'):
        current_user.push_subscription = json.dumps(subscription)
    else:
        # Если поля нет, добавляем через raw SQL
        try:
            db.session.execute(
                "UPDATE user SET push_subscription = ? WHERE id = ?",
                (json.dumps(subscription), current_user.id)
            )
        except:
            pass
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except:
        return jsonify({'success': False})

@app.route('/api/unread_counts')
@login_required
def get_unread_counts():
    """Получить актуальные счетчики непрочитанных сообщений"""
    result = {
        'chats': {},
        'groups': {},
        'channels': {}
    }
    
    # Чаты
    chats = Chat.query.filter(
        (Chat.user1_id == current_user.id) | (Chat.user2_id == current_user.id)
    ).all()
    
    for chat in chats:
        if chat.user1_id == current_user.id:
            last_read = chat.last_read_user1
        else:
            last_read = chat.last_read_user2
        
        if last_read:
            unread = Message.query.filter(
                Message.chat_id == chat.id,
                Message.sender_id != current_user.id,
                Message.timestamp > last_read
            ).count()
        else:
            unread = Message.query.filter(
                Message.chat_id == chat.id,
                Message.sender_id != current_user.id
            ).count()
        result['chats'][chat.id] = unread
    
    # Группы
    group_memberships = GroupMember.query.filter_by(user_id=current_user.id).all()
    for membership in group_memberships:
        if membership.last_read:
            unread = Message.query.filter(
                Message.group_id == membership.group_id,
                Message.sender_id != current_user.id,
                Message.timestamp > membership.last_read
            ).count()
        else:
            unread = Message.query.filter(
                Message.group_id == membership.group_id,
                Message.sender_id != current_user.id
            ).count()
        result['groups'][membership.group_id] = unread
    
    # Каналы
    channels = Channel.query.filter_by(deleted=False).all()
    for channel in channels:
        day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
        new_posts = ChannelPost.query.filter(
            ChannelPost.channel_id == channel.id,
            ChannelPost.timestamp > day_ago
        ).count()
        result['channels'][channel.id] = new_posts
    
    return jsonify(result)

@app.route('/notifications/unread_count')
@login_required
def get_unread_count():
    # Подсчитываем непрочитанные сообщения в чатах
    unread_chats = 0
    chats = Chat.query.filter(
        (Chat.user1_id == current_user.id) | (Chat.user2_id == current_user.id)
    ).all()
    
    for chat in chats:
        if chat.user1_id == current_user.id:
            last_read = chat.last_read_user1
        else:
            last_read = chat.last_read_user2
        
        if last_read:
            unread_messages = Message.query.filter(
                Message.chat_id == chat.id,
                Message.timestamp > last_read,
                Message.sender_id != current_user.id
            ).count()
            if unread_messages > 0:
                unread_chats += 1
    
    # Подсчитываем непрочитанные сообщения в группах
    unread_groups = 0
    group_memberships = GroupMember.query.filter_by(user_id=current_user.id).all()
    
    for membership in group_memberships:
        if membership.last_read:
            unread_messages = Message.query.filter(
                Message.group_id == membership.group_id,
                Message.timestamp > membership.last_read,
                    Message.sender_id != current_user.id
                ).count()
            if unread_messages > 0:
                unread_groups += 1
    
    total_unread = unread_chats + unread_groups
    
    return jsonify({'unread_count': total_unread})

@app.route('/chat/<int:chat_id>/mark_read', methods=['POST'])
@login_required
def mark_chat_read(chat_id):
    chat = db.session.get(Chat, chat_id)
    if not chat:
        return jsonify({'success': False, 'message': 'Чат не найден'})
    
    # Проверяем, что пользователь участвует в чате
    if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
        return jsonify({'success': False, 'message': 'Доступ запрещен'})
    
    # Отмечаем как прочитанное
    if chat.user1_id == current_user.id:
        chat.last_read_user1 = datetime.now(timezone.utc)
    else:
        chat.last_read_user2 = datetime.now(timezone.utc)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/group/<invite_link>/mark_read', methods=['POST'])
@login_required
def mark_group_read(invite_link):
    # Находим группу по invite_link
    group = Group.query.filter_by(invite_link_enc=invite_link).first()
    if not group:
        return jsonify({'success': False, 'message': 'Группа не найдена'})
    
    # Проверяем, состоит ли пользователь в группе
    member = GroupMember.query.filter_by(
        group_id=group.id, 
        user_id=current_user.id
    ).first()
    
    if not member:
        return jsonify({'success': False, 'message': 'Доступ запрещен'})
    
    # Отмечаем как прочитанное
    member.last_read = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify({'success': True})

## Удалена установка ключа группы

@app.route('/group/<invite_link>/members')
@login_required
def get_group_members(invite_link):
    # Находим группу по invite_link
    group = Group.query.filter_by(invite_link_enc=invite_link).first()
    if not group:
        return jsonify({'error': 'Группа не найдена'})
    
    # Проверяем, состоит ли пользователь в группе
    member = GroupMember.query.filter_by(
        group_id=group.id, 
        user_id=current_user.id
    ).first()
    
    if not member:
        return jsonify({'error': 'Доступ запрещен'})
    
    # Получаем участников группы
    members = GroupMember.query.filter_by(group_id=group.id).all()
    members_data = []
    
    for member in members:
        user = member.user
        members_data.append({
            'id': user.id,
            'nickname': user.nickname_enc,
            'is_creator': user.id == group.creator_id
        })
    
    return jsonify({'members': members_data})

## Удалена синхронизация ключей в группах

# SocketIO события
@socketio.on('join_chat')
def on_join_chat(data):
    chat_id = data.get('chat_id')
    chat = db.session.get(Chat, chat_id)
    if chat and (chat.user1_id == current_user.id or chat.user2_id == current_user.id):
        join_room(f'chat_{chat_id}')

@socketio.on('join_group')
def on_join_group(data):
    invite_link = data.get('invite_link')
    group = Group.query.filter_by(invite_link_enc=invite_link).first()
    if group:
        member = GroupMember.query.filter_by(group_id=group.id, user_id=current_user.id).first()
        if member:
            join_room(f'group_{invite_link}')

@socketio.on('leave_chat')
def on_leave_chat(data):
    chat_id = data.get('chat_id')
    leave_room(f'chat_{chat_id}')

@socketio.on('leave_group')
def on_leave_group(data):
    invite_link = data.get('invite_link')
    leave_room(f'group_{invite_link}')

@socketio.on('send_message')
def on_send_message(data):
    chat_id = data.get('chat_id')
    content = data.get('content', '').strip()
    file_id = data.get('file_id')
    
    if not content and not file_id:
        return
        
    chat = db.session.get(Chat, chat_id)
    if not chat or (chat.user1_id != current_user.id and chat.user2_id != current_user.id):
        return
        
    # Создаем сообщение
    message = Message(
        chat_id=chat_id,
        sender_id=current_user.id,
        content_enc=content.encode('utf-8') if content else b'',
        file_id=file_id,
        type='file' if file_id else 'text'
    )
    db.session.add(message)
    
    # Обновляем активность чата
    try:
        if hasattr(chat, 'last_activity'):
            chat.last_activity = datetime.now(timezone.utc)
    except:
        pass
    
    db.session.commit()
        
    # Отправляем сообщение в комнату
    message_data = {
        'id': message.id,
        'content': content,
        'sender': current_user.nickname_enc,
        'sender_id': current_user.id,
        'timestamp': message.timestamp.isoformat(),
        'is_edited': False,
        'deleted': False,
        'file_id': file_id
    }
    
    emit('new_message', message_data, room=f'chat_{chat_id}')
    
    # Обновляем счетчики и порядок чатов для всех
    recipient_id = chat.user2_id if chat.user1_id == current_user.id else chat.user1_id
    # Уведомляем получателя о новом сообщении
    emit('update_unread_count', {'chat_id': chat_id, 'type': 'chat'}, room=f'user_{recipient_id}')
    # Уведомляем отправителя об обновлении порядка
    emit('update_unread_count', {'chat_id': chat_id, 'type': 'chat'}, room=f'user_{current_user.id}')
    socketio.emit('chat_activity_update', {'chat_id': chat_id})
    
    # Отправляем push-уведомление
    if content:
        send_push_notification(recipient_id, f'Новое сообщение от {current_user.nickname_enc}', content[:50], f'/chat/{chat_id}')
    else:
        send_push_notification(recipient_id, f'Новое сообщение от {current_user.nickname_enc}', '📄 Файл', f'/chat/{chat_id}')

@socketio.on('send_group_message')
def on_send_group_message(data):
    invite_link = data.get('invite_link')
    content = data.get('content', '').strip()
    file_id = data.get('file_id')
    
    if not content and not file_id:
        return
        
    group = Group.query.filter_by(invite_link_enc=invite_link).first()
    if not group:
        return
        
    member = GroupMember.query.filter_by(group_id=group.id, user_id=current_user.id).first()
    if not member:
        return
        
    # Создаем сообщение
    message = Message(
        group_id=group.id,
        sender_id=current_user.id,
        content_enc=content.encode('utf-8') if content else b'',
        file_id=file_id,
        type='file' if file_id else 'text'
    )
    db.session.add(message)
    db.session.commit()
        
    # Отправляем сообщение в комнату
    message_data = {
        'id': message.id,
        'content': content,
        'sender': current_user.nickname_enc,
        'sender_id': current_user.id,
        'timestamp': message.timestamp.isoformat(),
        'is_edited': False,
        'deleted': False,
        'file_id': file_id
    }
        
    emit('new_group_message', message_data, room=f'group_{invite_link}')
    
    # Обновляем счетчики для всех участников группы
    members = GroupMember.query.filter_by(group_id=group.id).all()
    for member in members:
        if member.user_id != current_user.id:
            emit('update_unread_count', {'group_id': group.id, 'type': 'group'}, room=f'user_{member.user_id}')
            # Отправляем push-уведомление
            if content:
                send_push_notification(member.user_id, f'Новое сообщение в {group.name}', f'{current_user.nickname_enc}: {content[:30]}', f'/group/{invite_link}')
            else:
                send_push_notification(member.user_id, f'Новое сообщение в {group.name}', f'{current_user.nickname_enc}: 📄 Файл', f'/group/{invite_link}')
        
# Звонки
@socketio.on('call_start')
def on_call_start(data):
    if not current_user.is_authenticated:
        return
    
    target_user_id = data.get('target_user_id')
    if not target_user_id:
        return
    
    target_user = db.session.get(User, target_user_id)
    if not target_user:
        return
    
    # Создаем комнату для звонка
    call_room = f'call_{current_user.id}_{target_user_id}'
    
    # Присоединяемся к комнате
    join_room(call_room)
    
    # Отправляем уведомление о звонке
    emit('incoming_call', {
        'caller_id': current_user.id,
        'caller_nickname': current_user.nickname_enc,
        'call_room': call_room
    }, room=f'user_{target_user_id}')

@socketio.on('call_accept')
def on_call_accept(data):
    if not current_user.is_authenticated:
        return
    
    caller_id = data.get('caller_id')
    call_room = data.get('call_room')
    
    if not caller_id or not call_room:
        return
    
    caller = db.session.get(User, caller_id)
    if not caller:
        return
    
    # Присоединяемся к комнате звонка
    join_room(call_room)
    
    # Уведомляем звонящего о принятии
    emit('call_accepted', {
        'accepter_id': current_user.id,
        'accepter_nickname': current_user.nickname_enc
    }, room=call_room)

@socketio.on('call_reject')
def on_call_reject(data):
    if not current_user.is_authenticated:
        return
    
    caller_id = data.get('caller_id')
    call_room = data.get('call_room')
    
    if not caller_id:
        return
    
    caller = db.session.get(User, caller_id)
    if not caller:
        return
    
    # Уведомляем звонящего об отклонении
    emit('call_rejected', {
        'rejecter_id': current_user.id,
        'rejecter_nickname': current_user.nickname_enc
    }, room=f'user_{caller_id}')

@socketio.on('call_end')
def on_call_end(data):
    if not current_user.is_authenticated:
        return
    
    call_room = data.get('call_room')
    other_user_id = data.get('other_user_id')
    
    if call_room:
        # Уведомляем всех в комнате о завершении звонка
        emit('call_ended', {
            'ender_id': current_user.id,
            'ender_nickname': current_user.nickname_enc
        }, room=call_room)
        
        # Покидаем комнату
        leave_room(call_room)
    
    if other_user_id:
        # Также уведомляем конкретного пользователя
        emit('call_ended', {
            'ender_id': current_user.id,
            'ender_nickname': current_user.nickname_enc
        }, room=f'user_{other_user_id}')

@socketio.on('call_message')
def on_call_message(data):
    if not current_user.is_authenticated:
        return
    
    call_room = data.get('call_room')
    message = data.get('message')
    
    if call_room and message:
        # Отправляем сообщение всем в комнате звонка
        emit('call_message', {
            'sender_id': current_user.id,
            'sender_nickname': current_user.nickname_enc,
            'message': message
        }, room=call_room)



def emit_new_message(room, message_data):
    socketio.emit('new_message', message_data, room=room)

# Обработчики ошибок
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message='Страница не найдена'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html', error_code=403, error_message='Доступ запрещен'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error_code=500, error_message='Внутренняя ошибка сервера'), 500

@app.errorhandler(400)
def bad_request_error(error):
    return render_template('error.html', error_code=400, error_message='Неверный запрос'), 400

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('error.html', error_code=401, error_message='Требуется авторизация'), 401

@app.errorhandler(Exception)
def handle_exception(error):
    db.session.rollback()
    import traceback
    print(f"Error: {error}")
    print(traceback.format_exc())
    return f"<h1>Error 500</h1><pre>{error}</pre><pre>{traceback.format_exc()}</pre>", 500

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    try:
        if request.method == 'POST':
            # Обработка загрузки аватара
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and file.filename:
                    try:
                        filename = secure_filename(f"avatar_{current_user.id}_{uuid.uuid4().hex}_{file.filename}")
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        current_user.avatar = f"uploads/{filename}"
                        db.session.commit()
                        flash('Аватар обновлен', 'success')
                    except Exception as e:
                        flash('Ошибка загрузки аватара', 'error')
        
        is_bot = current_user.nickname_enc == 'Harvest'
        return render_template('profile_minimal.html', is_bot=is_bot)
    except Exception as e:
        print(f"Error in profile: {e}")
        is_bot = current_user.nickname_enc == 'Harvest'
        return render_template('profile_minimal.html', is_bot=is_bot)

@app.route('/channels/create', methods=['GET', 'POST'])
@login_required
def create_channel():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Название канала не может быть пустым', 'error')
            return render_template('create_channel_minimal.html')
        
        channel = Channel(
            name=name,
            description=description,
            creator_id=current_user.id
        )
        db.session.add(channel)
        db.session.commit()
        
        flash('Канал создан!', 'success')
        return redirect(url_for('view_channel', channel_id=channel.id))
    
    return render_template('create_channel_minimal.html')

@app.route('/channel/<int:channel_id>', methods=['GET', 'POST'])
@login_required
def view_channel(channel_id):
    channel = db.session.get(Channel, channel_id)
    if not channel or channel.deleted:
        abort(404)
    
    # Получаем посты канала
    posts = channel.posts.order_by(ChannelPost.timestamp.desc()).all()
    
    # Проверяем подписку
    subscription = ChannelSubscriber.query.filter_by(
        channel_id=channel.id, 
        user_id=current_user.id
    ).first()
    
    is_subscribed = subscription is not None
    
    return render_template('channel_minimal.html', 
                         channel=channel, 
                         posts=posts,
                         is_subscribed=is_subscribed)

@app.route('/channel/<int:channel_id>/settings', methods=['GET', 'POST'])
@login_required
def channel_settings(channel_id):
    channel = db.session.get(Channel, channel_id)
    if not channel or channel.deleted:
        abort(404)
    
    if channel.creator_id != current_user.id:
        flash('Только создатель может изменять настройки канала', 'error')
        return redirect(url_for('view_channel', channel_id=channel.id))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if name:
            channel.name = name
        if description:
            channel.description = description
            
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                filename = secure_filename(f"channel_{channel.id}_{uuid.uuid4().hex}_{file.filename}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                channel.avatar = f"uploads/{filename}"
        
        db.session.commit()
        flash('Настройки канала обновлены', 'success')
        return redirect(url_for('view_channel', channel_id=channel.id))
    
    subscribers = ChannelSubscriber.query.filter_by(channel_id=channel.id).all()
    return render_template('channel_settings_minimal.html', channel=channel, subscribers=subscribers)

@app.route('/channel/<int:channel_id>/delete', methods=['POST'])
@login_required
def delete_channel(channel_id):
    channel = db.session.get(Channel, channel_id)
    if not channel:
        flash('Канал не найден', 'error')
        return redirect(url_for('index'))
    
    if channel.creator_id != current_user.id:
        flash('Только создатель канала может его удалить', 'error')
        return redirect(url_for('view_channel', channel_id=channel.id))
    
    channel.deleted = True
    db.session.commit()
    
    flash('Канал удален', 'success')
    return redirect(url_for('index'))

@app.route('/channel/<int:channel_id>/post', methods=['POST'])
@login_required
def create_channel_post(channel_id):
    channel = db.session.get(Channel, channel_id)
    if not channel or channel.deleted:
        flash('Канал не найден', 'error')
        return redirect(url_for('index'))
    
    content = request.form.get('content', '').strip()
    if not content:
        flash('Содержание поста не может быть пустым', 'error')
        return redirect(url_for('view_channel', channel_id=channel.id))
    
    post = ChannelPost(
        channel_id=channel.id,
        author_id=current_user.id,
        content=content
    )
    db.session.add(post)
    db.session.commit()
    
    flash('Пост создан', 'success')
    return redirect(url_for('view_channel', channel_id=channel.id))

@app.route('/channel/<int:channel_id>/subscribe', methods=['POST'])
@login_required
def subscribe_channel(channel_id):
    channel = db.session.get(Channel, channel_id)
    if not channel or channel.deleted:
        flash('Канал не найден', 'error')
        return redirect(url_for('index'))
    
    # Проверяем, не подписан ли уже
    existing_subscription = ChannelSubscriber.query.filter_by(
        channel_id=channel.id, 
        user_id=current_user.id
    ).first()
    
    if existing_subscription:
        flash('Вы уже подписаны на этот канал', 'info')
        return redirect(url_for('view_channel', channel_id=channel.id))
    
    subscription = ChannelSubscriber(
        channel_id=channel.id,
        user_id=current_user.id
    )
    db.session.add(subscription)
    db.session.commit()
    
    flash('Вы подписались на канал', 'success')
    return redirect(url_for('view_channel', channel_id=channel.id))

@app.route('/channel/<int:channel_id>/unsubscribe', methods=['POST'])
@login_required
def unsubscribe_channel(channel_id):
    channel = db.session.get(Channel, channel_id)
    if not channel or channel.deleted:
        flash('Канал не найден', 'error')
        return redirect(url_for('index'))
    
    subscription = ChannelSubscriber.query.filter_by(
        channel_id=channel.id, 
        user_id=current_user.id
    ).first()
    
    if not subscription:
        flash('Вы не подписаны на этот канал', 'info')
        return redirect(url_for('view_channel', channel_id=channel.id))
    
    db.session.delete(subscription)
    db.session.commit()
    
    flash('Вы отписались от канала', 'success')
    return redirect(url_for('view_channel', channel_id=channel.id))

@app.route('/channel/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_channel_comment(post_id):
    post = db.session.get(ChannelPost, post_id)
    if not post:
        flash('Пост не найден', 'error')
        return redirect(url_for('index'))
    
    content = request.form.get('content', '').strip()
    if not content:
        flash('Комментарий не может быть пустым', 'error')
        return redirect(url_for('view_channel', channel_id=post.channel.id))
    
    comment = ChannelComment(
        post_id=post.id,
        author_id=current_user.id,
        content=content
    )
    db.session.add(comment)
    db.session.commit()
    
    flash('Комментарий добавлен', 'success')
    return redirect(url_for('view_channel', channel_id=post.channel.id))

@app.route('/channel/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_channel_post(post_id):
    post = db.session.get(ChannelPost, post_id)
    if not post:
        flash('Пост не найден', 'error')
        return redirect(url_for('index'))
    
    channel_id = post.channel_id
    channel = db.session.get(Channel, channel_id)
    
    if post.author_id != current_user.id and channel.creator_id != current_user.id:
        flash('У вас нет прав для удаления этого поста', 'error')
        return redirect(url_for('view_channel', channel_id=channel_id))
    
    db.session.delete(post)
    db.session.commit()
    flash('Пост удалён', 'success')
    return redirect(url_for('view_channel', channel_id=channel_id))

@app.route('/api/chats')
@login_required
def api_chats():
    # Получаем все чаты пользователя
    chats = Chat.query.filter(
        or_(
            Chat.user1_id == current_user.id,
            Chat.user2_id == current_user.id
        )
    ).all()
    
    chat_list = []
    for chat in chats:
        # Определяем другого пользователя в чате
        other_user = chat.user2 if chat.user1_id == current_user.id else chat.user1
        
        # Получаем последнее сообщение
        last_message = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.desc()).first()
        
        chat_data = {
            'id': chat.id,
            'other_user': {
                'id': other_user.id,
                'nickname_enc': other_user.nickname_enc
            },
            'last_message': last_message.content_enc.decode('utf-8') if last_message and not last_message.deleted else None
        }
        chat_list.append(chat_data)
    
    return jsonify({'chats': chat_list})

@app.route('/api/start_chat', methods=['POST'])
@login_required
def start_chat():
    data = request.get_json()
    target_user_id = data.get('user_id')
    
    if not target_user_id:
        return jsonify({'success': False, 'message': 'ID пользователя не указан'})
    
    target_user = db.session.get(User, target_user_id)
    if not target_user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'})
    
    if target_user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Нельзя создать чат с самим собой'})
    
    # Проверяем, существует ли уже чат между этими пользователями
    existing_chat = Chat.query.filter(
        or_(
            and_(Chat.user1_id == current_user.id, Chat.user2_id == target_user.id),
            and_(Chat.user1_id == target_user.id, Chat.user2_id == current_user.id)
        )
    ).first()
    
    if existing_chat:
        return jsonify({'success': True, 'chat_id': existing_chat.id})
    
    # Создаем новый чат
    new_chat = Chat(
        user1_id=current_user.id,
        user2_id=target_user.id
    )
    db.session.add(new_chat)
    db.session.commit()
    
    return jsonify({'success': True, 'chat_id': new_chat.id})

@app.route('/download_file/<int:file_id>')
@login_required
def download_message_file(file_id):
    file = db.session.get(File, file_id)
    if not file:
        abort(404)
    
    file_path = os.path.join(app.static_folder, file.file_path)
    if not os.path.exists(file_path):
        abort(404)
    
    return send_file(file_path, as_attachment=True, download_name=file.original_name)

@app.route('/upload_file', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Файл не найден'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Файл не выбран'})
    
    if file:
        filename = secure_filename(f"{current_user.id}_{uuid.uuid4().hex}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Создаем запись о файле в базе данных
        file_record = File(
            filename=filename,
            original_name=file.filename,
            file_path=f"uploads/{filename}",
            file_type=file.content_type,
            uploaded_by=current_user.id
        )
        db.session.add(file_record)
    db.session.commit()
    
    return jsonify({
            'success': True, 
            'file_id': file_record.id,
            'file_name': file.filename,
            'file_type': file.content_type
        })
    
    return jsonify({'success': False, 'message': 'Ошибка загрузки файла'})

@app.route('/chat/<int:chat_id>/share_contact', methods=['POST'])
@login_required
def share_contact(chat_id):
    chat = db.session.get(Chat, chat_id)
    if not chat:
        abort(404)
    
    # Проверяем, что пользователь участвует в чате
    if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
        abort(403)
    
    # Получаем другого пользователя в чате
    other_user_id = chat.user2_id if chat.user1_id == current_user.id else chat.user1_id
    other_user = db.session.get(User, other_user_id)
    
    if not other_user:
        abort(404)
    
    # Создаем сообщение с контактом (без публичных ключей)
    contact_info = f"📱 Контакт: {other_user.nickname_enc}"
    
    message = Message(
        chat_id=chat.id,
        sender_id=current_user.id,
        content_enc=contact_info.encode('utf-8')
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Контакт поделен'})

@app.route('/chat/<int:chat_id>/clear_history', methods=['POST'])
@login_required
def clear_chat_history(chat_id):
    chat = db.session.get(Chat, chat_id)
    if not chat:
        abort(404)
    
    # Проверяем, что пользователь участвует в чате
    if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
        abort(403)
    
    # Удаляем все сообщения пользователя в этом чате
    messages = Message.query.filter_by(
        chat_id=chat.id,
        sender_id=current_user.id
    ).all()
    
    for message in messages:
        db.session.delete(message)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'История очищена'})

@app.route('/chat/<int:chat_id>/block_user', methods=['POST'])
@login_required
def block_user(chat_id):
    chat = db.session.get(Chat, chat_id)
    if not chat:
        abort(404)
    
    # Проверяем, что пользователь участвует в чате
    if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
        abort(403)
    
    # Получаем другого пользователя в чате
    other_user_id = chat.user2_id if chat.user1_id == current_user.id else chat.user1_id
    other_user = db.session.get(User, other_user_id)
    
    if not other_user:
        abort(404)
    
    # Добавляем пользователя в список заблокированных
    
    if not current_user.blocked_users:
        current_user.blocked_users = json.dumps([])
    
    blocked_list = json.loads(current_user.blocked_users)
    if other_user_id not in blocked_list:
        blocked_list.append(other_user_id)
        current_user.blocked_users = json.dumps(blocked_list)
        db.session.commit()
    
    return jsonify({'success': True, 'message': 'Пользователь заблокирован'})

@app.route('/admin/ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    if not current_user.is_admin:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    ticket = db.session.get(SupportTicket, ticket_id)
    if not ticket:
        flash('Тикет не найден', 'error')
        return redirect(url_for('admin_panel'))
    
    return render_template('ticket_view_minimal.html', ticket=ticket)

@app.route('/admin/ticket/<int:ticket_id>/status', methods=['POST'])
@login_required
def update_ticket_status(ticket_id):
    if not current_user.is_admin:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    ticket = db.session.get(SupportTicket, ticket_id)
    if not ticket:
        flash('Тикет не найден', 'error')
        return redirect(url_for('admin_panel'))
    
    new_status = request.form.get('status')
    response = request.form.get('response', '').strip()
    
    if new_status in ['open', 'in_progress', 'closed']:
        old_status = ticket.status
        ticket.status = new_status
        if response:
            ticket.admin_response = response
        ticket.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        # Отправляем уведомление пользователю
        status_text = {
            'open': '🟡 Открыт',
            'in_progress': '🔵 В работе',
            'closed': '🟢 Закрыт'
        }
        
        notification_text = f"Обновление тикета #{ticket.id}\n\n"
        notification_text += f"Тема: {ticket.subject}\n"
        notification_text += f"Новый статус: {status_text.get(new_status, new_status)}\n\n"
        
        if response:
            notification_text += f"Ответ администратора:\n{response}"
        
        send_bot_message(ticket.user_id, notification_text)
        
        flash('Статус тикета обновлён', 'success')
    
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

def send_push_notification(user_id, title, body, url=None):
    """Отправляет push-уведомление пользователю"""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return False
        
        # Получаем подписку пользователя
        subscription_data = None
        try:
            result = db.session.execute(
                "SELECT push_subscription FROM user WHERE id = ?",
                (user_id,)
            ).fetchone()
            if result and result[0]:
                subscription_data = json.loads(result[0])
        except:
            return False
        
        if not subscription_data:
            return False
        
        # Отправляем через SocketIO для браузерных уведомлений
        socketio.emit('browser_notification', {
            'title': title,
            'body': body,
            'url': url or '/'
        }, room=f'user_{user_id}')
        
        print(f"[PUSH] Отправка уведомления: {title} -> {user.nickname_enc}")
        return True
        
    except Exception as e:
        print(f"[PUSH ERROR] {e}")
        return False

def send_bot_message(user_id, message_text):
    """Отправляет сообщение от бота пользователю"""
    bot = User.query.filter_by(nickname_enc='Harvest').first()
    if not bot:
        return False
    
    # Проверяем существующий чат или создаем новый
    existing_chat = Chat.query.filter(
        or_(
            and_(Chat.user1_id == bot.id, Chat.user2_id == user_id),
            and_(Chat.user1_id == user_id, Chat.user2_id == bot.id)
        )
    ).first()
    
    if not existing_chat:
        chat = Chat(user1_id=bot.id, user2_id=user_id)
        db.session.add(chat)
        db.session.commit()
    else:
        chat = existing_chat
    
    # Отправляем сообщение
    message = Message(
        chat_id=chat.id,
        sender_id=bot.id,
        content_enc=message_text.encode('utf-8'),
        type='text'
    )
    db.session.add(message)
    db.session.commit()
    return True

@app.route('/bot/broadcast', methods=['POST'])
@login_required
def bot_broadcast():
    if current_user.nickname_enc != 'Harvest':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    message_text = request.form.get('message', '').strip()
    if not message_text:
        flash('Сообщение не может быть пустым', 'error')
        return redirect(url_for('profile'))
    
    # Отправляем сообщение всем пользователям
    users = User.query.filter(User.nickname_enc != 'Harvest', User.banned == False).all()
    
    broadcast_text = f"Объявление Harvest\n\n{message_text}"
    
    sent_count = 0
    for user in users:
        if send_bot_message(user.id, broadcast_text):
            sent_count += 1
    
    flash(f'Сообщение отправлено {sent_count} пользователям', 'success')
    return redirect(url_for('profile'))

@app.route('/create_support_ticket', methods=['POST'])
@login_required
def create_support_ticket():
    subject = request.form.get('subject')
    description = request.form.get('description')
    user_nickname = request.form.get('user_nickname')
    scammer_nickname = request.form.get('scammer_nickname', '')
    
    if not all([subject, description, user_nickname]):
        flash('Заполните все обязательные поля', 'error')
        return redirect(url_for('profile'))
    
    # Обработка изображения доказательства
    evidence_image = None
    if 'evidence_image' in request.files:
        file = request.files['evidence_image']
        if file and file.filename:
            filename = secure_filename(f"evidence_{current_user.id}_{uuid.uuid4().hex}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            evidence_image = f"uploads/{filename}"
    
    # Создаем тикет
    ticket = SupportTicket(
        user_id=current_user.id,
        subject=subject,
        description=description,
        user_nickname=user_nickname,
        scammer_nickname=scammer_nickname,
        evidence_image=evidence_image
    )
    
    db.session.add(ticket)
    db.session.commit()
    
    flash('Тикет поддержки создан', 'success')
    return redirect(url_for('profile'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)