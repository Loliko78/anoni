#lt --port 10000 --subdomain harvestano - запуск сайта через LocalTunnel

from flask import Flask, render_template, redirect, url_for, flash, request, send_file, jsonify, session, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
from forms import RegisterForm, LoginForm
from crypto_utils import generate_aes_key, hash_password, check_password, remove_exif_and_mark, encrypt_file, decrypt_file
from models import User, Chat, Message, File, Group, GroupMember, ReadTracking, Channel, ChannelPost, ChannelSubscriber, ChannelComment
import mimetypes
import uuid
import logging
from db import db
from sqlalchemy import or_, func
from werkzeug.utils import secure_filename
import time
from datetime import datetime, timedelta, UTC
import random
import base64
from flask_cors import CORS

app = Flask(__name__, instance_relative_config=True)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///harvest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')

# Создаем папку uploads если её нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', ping_timeout=60, ping_interval=25)

# Отключаем все логи Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app.logger.disabled = True

# Проверка HTTPS (или Tor)
@app.before_request
def enforce_https():
    # Разрешаем доступ через ngrok и другие туннели
    if (request.host.startswith('localhost') or 
        request.host.startswith('127.0.0.1') or 
        request.host.endswith('.ngrok.io') or
        request.host.endswith('.ngrok-free.app') or
        request.host.endswith('.onion')):
        return None
    # Временно отключаем для тестирования
    return None

# Генерируем безопасный ключ для шифрования ников
NICKNAME_KEY = os.environ.get('NICKNAME_KEY', os.urandom(32))

# Предустановленные ключи для синхронизации (base64) - ровно 32 байта каждый
PRESET_KEYS = [
    "PJPZ+XZf5txh8sg/70l/06k7wJ/HATQoZ1OObCk4Oag=",
    "dQ5mwdYm2IfvNmjT/EYicRVdzL+7rc0lXrPcT8YxlJ4=",
    "1hD/Iwj0Cur6a515t4HwMhRgfyv+lPD1UpogJS+6Pe4=",
    "U2mRdAOB7j2AHkdAjhjdxdeNqAye4rWcSacFKyzS8Ig=",
    "W3PGFQ7WIMfGY2a5fkrr9GFeIoqeR3hG3WKpNy9IDo0=",
    "oUq3ztH9e2ZrsVgPdcu2VnIhZOq4v76o1sjpdRAQIeQ=",
    "+D6OwWf7DLnRQrYrSbYdHwmQQz1TUOnhzh+dvFh+/Jw=",
    "7eC6RVUxjE3I3kIiTF4r/wjRk+L3q0HiAiG6VqDb40g=",
    "oCAL98pSXYdqHSyeWKyH+hn+Nt1IqA9U8uCkibLiBWA=",
    "pYzZ7YElBqfQ/dVDCVN2Zp4kjtvwTI5DtoVRuobCyxc="
]

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        nickname = form.nickname.data.strip()
        password = form.password.data
        password_hash = hash_password(password)
        if User.query.filter_by(nickname_enc=nickname).first():
            flash('Пользователь с таким ником уже существует', 'danger')
            return render_template('register.html', form=form)
        user = User(nickname_enc=nickname, password_hash=password_hash, avatar='avatars/user_1.jpg')
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна! Теперь войдите.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Проверяем защиту от брутфорса
        if not check_bruteforce_protection():
            flash('Слишком много неудачных попыток. Попробуйте через 15 минут.', 'danger')
            return render_template('login.html', form=form)
        
        nickname = form.nickname.data.strip()
        password = form.password.data
        user = User.query.filter_by(nickname_enc=nickname).first()
        
        if user and check_password(user.password_hash, password):
            if user.banned:
                flash('Ваш аккаунт заблокирован', 'danger')
                record_login_attempt(request.remote_addr, False)
                return render_template('login.html', form=form)
            
            login_user(user)
            record_login_attempt(request.remote_addr, True)
            return redirect(url_for('index'))
        
        flash('Неверный ник или пароль', 'danger')
        record_login_attempt(request.remote_addr, False)
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/chats')
@login_required
def index():
    # Получаем все чаты пользователя
    chats = Chat.query.filter(
        (Chat.user1_id == current_user.id) | (Chat.user2_id == current_user.id)
    ).all()
    # Группы, в которых состоит пользователь
    group_memberships = GroupMember.query.filter_by(user_id=current_user.id).all()
    group_list = []
    for gm in group_memberships:
        group = db.session.get(Group, gm.group_id)
        if group:
            try:
                group_name = group.name_enc.decode('utf-8')
                invite_link = group.invite_link_enc.decode('utf-8')
            except Exception:
                group_name = 'Unknown Group'
                invite_link = ''
            group_list.append({
                'group_name': group_name,
                'invite_link': invite_link,
                'group_id': group.id,
                'avatar': group.avatar
            })
    # Для каждого чата получаем собеседника и последнее сообщение
    chats_with_info = []
    for chat in chats:
        other_user = chat.user1 if chat.user1_id != current_user.id else chat.user2
        last_read_entry = ReadTracking.query.filter_by(user_id=current_user.id, chat_id=chat.id).first()
        last_read_time = last_read_entry.last_read if last_read_entry else datetime.min
        unread_count = Message.query.filter(
            Message.chat_id == chat.id,
            Message.timestamp > last_read_time
        ).count()
        # Определяем время последней активности (последнего сообщения)
        last_message = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.desc()).first()
        last_activity = last_message.timestamp if last_message else datetime.min
        chats_with_info.append({
            'chat': chat,
            'other_user_nickname': other_user.nickname_enc,
            'unread_count': unread_count,
            'last_activity': last_activity
        })
    # Сортируем чаты по убыванию активности
    chats_with_info.sort(key=lambda x: x['last_activity'], reverse=True)
    # Каналы, на которые подписан пользователь
    channel_subs = ChannelSubscriber.query.filter_by(user_id=current_user.id).all()
    channel_list = []
    for sub in channel_subs:
        channel = db.session.get(Channel, sub.channel_id)
        if channel and not channel.deleted:  # Проверяем, что канал существует и не удалён
            channel_list.append(channel)
    return render_template('chats.html', chat_list=chats_with_info, group_list=group_list, channel_list=channel_list)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        # Проверяем, не создается ли новый чат
        start_chat = request.form.get('start_chat')
        if start_chat:
            user_id = int(start_chat)
            other_user = db.session.get(User, user_id)
            if other_user and other_user.id != current_user.id and not other_user.banned:
                # Проверяем, есть ли уже чат
                chat = Chat.query.filter(
                    or_(
                        (Chat.user1_id == current_user.id) & (Chat.user2_id == user_id),
                        (Chat.user1_id == user_id) & (Chat.user2_id == current_user.id)
                    )
                ).first()
                
                if not chat:
                    chat = Chat(user1_id=current_user.id, user2_id=user_id)
                    db.session.add(chat)
                    db.session.commit()
                
                return redirect(url_for('chat', chat_id=chat.id))
            else:
                flash('Пользователь не найден', 'danger')
                return redirect(url_for('search'))
        
        nickname = request.form.get('nickname', '').strip()
        if not nickname:
            flash('Введите ник для поиска', 'danger')
            return render_template('search.html', results=[])
        
        # Поиск пользователей
        users = User.query.filter(User.nickname_enc.contains(nickname)).all()
        
        # Поиск каналов
        channels = Channel.query.filter(
            Channel.name.contains(nickname),
            Channel.deleted == False
        ).all()
        
        results = []
        for user in users:
            if user.id != current_user.id and not user.banned:
                # Проверяем, есть ли уже чат с этим пользователем
                chat = Chat.query.filter(
                    or_(
                        (Chat.user1_id == current_user.id) & (Chat.user2_id == user.id),
                        (Chat.user1_id == user.id) & (Chat.user2_id == current_user.id)
                    )
                ).first()
                
                results.append({
                    'type': 'user',
                    'id': user.id,
                    'nickname': user.nickname_enc,
                    'avatar': user.avatar,
                    'chat_id': chat.id if chat else None
                })
        
        for channel in channels:
            # Проверяем, подписан ли пользователь на канал
            is_subscribed = ChannelSubscriber.query.filter_by(
                channel_id=channel.id, 
                user_id=current_user.id
            ).first() is not None
            
            results.append({
                'type': 'channel',
                'id': channel.id,
                'name': channel.name,
                'description': channel.description,
                'avatar': channel.avatar,
                'is_subscribed': is_subscribed
            })
        
        if not results:
            flash('Ничего не найдено', 'info')
        
        return render_template('search.html', results=results)
    
    return render_template('search.html', results=[])

@app.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
@login_required
def chat(chat_id):
    chat = db.session.get(Chat, chat_id)
    if current_user.id not in [chat.user1_id, chat.user2_id]:
        abort(403)

    # Update read tracking
    tracking = ReadTracking.query.filter_by(user_id=current_user.id, chat_id=chat_id).first()
    if tracking:
        tracking.last_read = datetime.now(UTC)
    else:
        tracking = ReadTracking(user_id=current_user.id, chat_id=chat_id, last_read=datetime.now(UTC))
        db.session.add(tracking)
    db.session.commit()

    other_user_id = chat.user2_id if current_user.id == chat.user1_id else chat.user1_id
    other_user = db.session.get(User, other_user_id)

    # E2EE: если ключа нет, генерируем и сохраняем
    if not chat.key_enc:
        key = os.urandom(32)  # 256 бит
        chat.key_enc = base64.b64encode(key)
        db.session.commit()
    # Отправка сообщения
    if request.method == 'POST':
        content_enc = request.form.get('content_enc')
        file = request.files.get('file')
        file_url = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[-1].lower()
            # Поддерживаем все типы файлов
            allowed_extensions = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi', 'mp3', 'wav', 'pdf', 'doc', 'docx', 'txt', 'zip', 'rar', '7z']
            if ext in allowed_extensions:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'chat_{chat_id}_{uuid.uuid4().hex}_{filename}')
                file.save(file_path)
                file_url = url_for('static', filename='uploads/' + os.path.basename(file_path))
        if not content_enc and not file_url:
            return jsonify({'success': False, 'message': 'Missing data'}), 400
        # Сохраняем content_enc и/или file_url
        message_content = content_enc or ''
        if file_url:
            message_content += f' [file:{file_url}]'
        new_message = Message(
            chat_id=chat_id,
            sender_id=current_user.id,
            content_enc=message_content.encode('utf-8')
        )
        db.session.add(new_message)
        db.session.commit()
        # Отправляем сообщение через Socket.IO
        message_data = {
            'id': new_message.id,
            'chat_id': chat_id,
            'sender_id': current_user.id,
            'sender_nickname': current_user.nickname_enc,
            'content': content,
            'timestamp': new_message.timestamp.isoformat(),
            'file_url': file_url
        }
        emit_new_message(f'chat_{chat_id}', message_data)
        return jsonify({'success': True})
    # Получаем сообщения чата
    messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.asc()).all()
    
    # Передаем сообщения как есть, расшифровка будет на клиенте
    messages_data = []
    for message in messages:
        try:
            content = message.content_enc.decode('utf-8') if message.content_enc else ''
            messages_data.append({
                'id': message.id,
                'sender_id': message.sender_id,
                'content': content,
                'timestamp': message.timestamp,
                'deleted': message.deleted
            })
        except Exception as e:
            messages_data.append({
                'id': message.id,
                'sender_id': message.sender_id,
                'content': '[ошибка чтения сообщения]',
                'timestamp': message.timestamp,
                'deleted': message.deleted
            })
    
    # Получаем собеседника
    try:
        nickname = other_user.nickname_enc if other_user else 'Unknown'
    except Exception:
        nickname = 'Unknown'
    
    # Проверяем, есть ли у собеседника публичный ключ
    other_has_key = other_user.public_key is not None if other_user else False
    
    # Кнопка синхронизации показывается всегда в личных чатах
    show_sync_button = True if other_user else False
    
    # E2EE: отдаём ключ в шаблон (base64)
    chat_key_b64 = chat.key_enc.decode('utf-8') if chat.key_enc else ''
    return render_template('chat.html', chat=chat, messages=messages_data, nickname=nickname, chat_key_b64=chat_key_b64, other_has_key=other_has_key, other_user=other_user, show_sync_button=show_sync_button, anonymous_mode=current_user.anonymous_mode)

@app.route('/file/<int:file_id>')
@login_required
def download_file(file_id):
    file_record = File.query.get_or_404(file_id)
    # Проверяем доступ к файлу через сообщение
    if file_record.message.chat_id:
        chat = db.session.get(Chat, file_record.message.chat_id)
        if current_user.id not in [chat.user1_id, chat.user2_id]:
            flash('Нет доступа к этому файлу', 'danger')
            return redirect(url_for('index'))
    elif file_record.message.group_id:
        group = db.session.get(Group, file_record.message.group_id)
        if not GroupMember.query.filter_by(group_id=group.id, user_id=current_user.id).first():
            flash('Нет доступа к этому файлу', 'danger')
            return redirect(url_for('index'))
    
    # Расшифровываем файл
    temp_path = decrypt_file(
        file_record.path_enc.decode('utf-8'), 
        file_record.file_key_enc,
        os.path.join(app.config['UPLOAD_FOLDER'], f'temp_{file_id}')
    )
    
    filename = file_record.filename_enc.decode('utf-8')
    return send_file(temp_path, as_attachment=True, download_name=filename)

@app.route('/file/<int:file_id>/view')
@login_required
def view_file(file_id):
    file_record = File.query.get_or_404(file_id)
    # Проверяем доступ к файлу через сообщение
    if file_record.message.chat_id:
        chat = db.session.get(Chat, file_record.message.chat_id)
        if current_user.id not in [chat.user1_id, chat.user2_id]:
            flash('Нет доступа к этому файлу', 'danger')
            return redirect(url_for('index'))
    elif file_record.message.group_id:
        group = db.session.get(Group, file_record.message.group_id)
        if not GroupMember.query.filter_by(group_id=group.id, user_id=current_user.id).first():
            flash('Нет доступа к этому файлу', 'danger')
            return redirect(url_for('index'))
    
    # Расшифровываем файл
    temp_path = decrypt_file(
        file_record.path_enc.decode('utf-8'), 
        file_record.file_key_enc,
        os.path.join(app.config['UPLOAD_FOLDER'], f'temp_{file_id}')
    )
    
    return send_file(temp_path)

@app.route('/message/delete/<int:msg_id>', methods=['POST'])
@login_required
def delete_message(msg_id):
    msg = Message.query.get_or_404(msg_id)
    if msg.sender_id != current_user.id:
        flash('Можно удалять только свои сообщения', 'danger')
        return redirect(request.referrer or url_for('index'))
    msg.deleted = True
    db.session.commit()
    flash('Сообщение удалено', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/message/edit/<int:msg_id>', methods=['POST'])
@login_required
def edit_message(msg_id):
    msg = Message.query.get_or_404(msg_id)
    if msg.sender_id != current_user.id:
        flash('Можно редактировать только свои сообщения', 'danger')
        return redirect(request.referrer or url_for('index'))
    new_text = request.form.get('edit_text', '').strip()
    if new_text:
        # Имитация формата ciphertext::iv для совместимости с JS (plaintext::emptyiv)
        msg.content_enc = f"{new_text}::plainiv".encode('utf-8')
        db.session.commit()
        flash('Сообщение изменено', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('index'))
    users = User.query.all()
    chats = Chat.query.all()
    groups = Group.query.all()
    return render_template('admin.html', users=users, chats=chats, groups=groups, NICKNAME_KEY=NICKNAME_KEY)

@app.route('/admin/ban/<int:user_id>', methods=['POST'])
@login_required
def admin_ban(user_id):
    if not current_user.is_admin:
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    user.banned = not user.banned
    db.session.commit()
    flash('Статус блокировки изменён', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_chat/<int:chat_id>', methods=['POST'])
@login_required
def admin_delete_chat(chat_id):
    # Только для azazel
    admin_nick = 'azazel'
    try:
        user_nick = other_user.nickname_enc if other_user else ''
    except Exception:
        user_nick = ''
    if not current_user.is_admin or user_nick != admin_nick:
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('index'))
    chat = db.session.get(Chat, chat_id)
    db.session.delete(chat)
    db.session.commit()
    flash('Чат удалён', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/group/create', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        group_name = request.form.get('group_name', '').strip()
        if not group_name:
            flash('Введите название группы', 'danger')
            return render_template('create_group.html')
        # Генерируем invite-link
        invite_link = str(uuid.uuid4())
        name_enc = group_name.encode('utf-8')
        invite_link_enc = invite_link.encode('utf-8')
        group = Group(name_enc=name_enc, invite_link_enc=invite_link_enc, creator_id=current_user.id)
        db.session.add(group)
        db.session.commit()
        # Добавляем создателя в участники
        gm = GroupMember(group_id=group.id, user_id=current_user.id)
        db.session.add(gm)
        db.session.commit()
        flash('Группа создана!', 'success')
        return redirect(url_for('group_chat', invite_link=invite_link))
    return render_template('create_group.html')

@app.route('/group/join/<invite_link>')
@login_required
def join_group(invite_link):
    # Находим группу по invite_link
    groups = Group.query.all()
    found = None
    for group in groups:
        try:
            dec_link = group.invite_link_enc.decode('utf-8')
            if dec_link == invite_link:
                found = group
                break
        except Exception:
            continue
    if not found:
        flash('Группа не найдена', 'danger')
        return redirect(url_for('index'))
    # Добавляем пользователя в участники, если его там нет
    if not GroupMember.query.filter_by(group_id=found.id, user_id=current_user.id).first():
        gm = GroupMember(group_id=found.id, user_id=current_user.id)
        db.session.add(gm)
        db.session.commit()
    return redirect(url_for('group_chat', invite_link=invite_link))

@app.route('/group/<invite_link>', methods=['GET', 'POST'])
@login_required
def group_chat(invite_link):
    found = Group.query.filter_by(invite_link_enc=invite_link.encode('utf-8')).first_or_404()
    # Проверяем, что пользователь участник
    if not GroupMember.query.filter_by(group_id=found.id, user_id=current_user.id).first():
        flash('Вы не участник этой группы', 'danger')
        return redirect(url_for('index'))

    # Обработка смены аватарки и удаления группы (только для создателя)
    if request.method == 'POST' and found.creator_id == current_user.id:
        if 'avatar_choice' in request.form or 'avatar_upload' in request.files:
            avatar_choice = request.form.get('avatar_choice')
            avatar_upload = request.files.get('avatar_upload')
            if avatar_upload and avatar_upload.filename:
                filename = secure_filename(avatar_upload.filename)
                ext = filename.rsplit('.', 1)[-1].lower()
                if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                    avatar_path = f'avatars/group_{found.id}.{ext}'
                    avatar_upload.save(os.path.join(app.static_folder, avatar_path))
                    found.avatar = avatar_path
            elif avatar_choice:
                found.avatar = avatar_choice
            db.session.commit()
            flash('Аватарка группы обновлена', 'success')
            return redirect(url_for('group_chat', invite_link=invite_link))
        if request.form.get('delete_group'):
            # Удаляем все сообщения, участников, саму группу
            Message.query.filter_by(group_id=found.id).delete()
            GroupMember.query.filter_by(group_id=found.id).delete()
            db.session.delete(found)
            db.session.commit()
            flash('Группа удалена', 'success')
            return redirect(url_for('index'))

    # Отправка сообщений аналогично чату (можно вынести в функцию)
    if request.method == 'POST':
        content_enc = request.form.get('content_enc')
        file = request.files.get('file')
        file_url = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[-1].lower()
            # Поддерживаем все типы файлов
            allowed_extensions = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi', 'mp3', 'wav', 'pdf', 'doc', 'docx', 'txt', 'zip', 'rar', '7z']
            if ext in allowed_extensions:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'group_{found.id}_{uuid.uuid4().hex}_{filename}')
                file.save(file_path)
                file_url = url_for('static', filename='uploads/' + os.path.basename(file_path))
        if not content_enc and not file_url:
            return jsonify({'success': False, 'message': 'Missing data'}), 400
        message_content = content_enc or ''
        if file_url:
            message_content += f' [file:{file_url}]'
        new_message = Message(
            group_id=found.id,
            sender_id=current_user.id,
            content_enc=message_content.encode('utf-8')
        )
        db.session.add(new_message)
        db.session.commit()
        # Отправляем сообщение через Socket.IO
        message_data = {
            'id': new_message.id,
            'group_id': found.id,
            'sender_id': current_user.id,
            'sender_name': current_user.nickname_enc,
            'content': content,
            'timestamp': new_message.timestamp.isoformat(),
            'file_url': file_url
        }
        emit_new_message(f'group_{invite_link}', message_data)
        return jsonify({'success': True})
    # Получаем сообщения группы
    messages = Message.query.filter_by(group_id=found.id).order_by(Message.timestamp.asc()).all()
    
    # Передаем сообщения как есть, расшифровка будет на клиенте
    messages_data = []
    for message in messages:
        try:
            content = message.content_enc.decode('utf-8') if message.content_enc else ''
            
            # Получаем информацию об отправителе
            sender = db.session.get(User, message.sender_id)
            sender_nickname = sender.nickname_enc if sender else 'Unknown'
            
            messages_data.append({
                'id': message.id,
                'sender_id': message.sender_id,
                'sender': {'encrypted_nickname': sender_nickname},
                'content': content,
                'timestamp': message.timestamp,
                'deleted': message.deleted
            })
        except Exception as e:
            sender = db.session.get(User, message.sender_id)
            sender_nickname = sender.nickname_enc if sender else 'Unknown'
            messages_data.append({
                'id': message.id,
                'sender_id': message.sender_id,
                'sender': {'encrypted_nickname': sender_nickname},
                'content': '[ошибка чтения сообщения]',
                'timestamp': message.timestamp,
                'deleted': message.deleted
            })
    
    # Получаем название группы
    try:
        group_name = found.name_enc.decode('utf-8')
    except Exception:
        group_name = 'Unknown'
    
    # Проверяем, является ли пользователь создателем группы
    is_creator = (found.creator_id == current_user.id)
    
    # E2EE: отдаём ключ группы в шаблон (base64)
    group_key_b64 = ''
    if found.session_key:
        try:
            # Check if it's already base64
            base64.b64decode(found.session_key, validate=True)
            group_key_b64 = found.session_key.decode('utf-8')
        except (ValueError, TypeError):
            # If not, encode it
            group_key_b64 = base64.b64encode(found.session_key).decode('utf-8')

    return render_template('group_chat.html', group=found, messages=messages_data, group_name=group_name, invite_link=invite_link, is_creator=is_creator, group_key_b64=group_key_b64, anonymous_mode=current_user.anonymous_mode)

@app.route('/admin/delete_group/<int:group_id>', methods=['POST'])
@login_required
def admin_delete_group(group_id):
    # Только для azazel
    admin_nick = 'azazel'
    try:
        user_nick = other_user.nickname_enc if other_user else ''
    except Exception:
        user_nick = ''
    if not current_user.is_admin or user_nick != admin_nick:
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('index'))
    group = db.session.get(Group, group_id)
    db.session.delete(group)
    db.session.commit()
    flash('Группа удалена', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/group/<invite_link>/messages')
@login_required
def get_group_messages(invite_link):
    found = Group.query.filter_by(invite_link_enc=invite_link.encode('utf-8')).first_or_404()
    # Check if user is a member using GroupMember table
    if not GroupMember.query.filter_by(group_id=found.id, user_id=current_user.id).first():
         return jsonify({"error": "Unauthorized"}), 403

    messages = Message.query.filter_by(group_id=found.id).order_by(Message.timestamp.asc()).all()
    return jsonify([{
        'id': msg.id,
        'sender_id': msg.sender_id,
        'content_enc': base64.b64encode(msg.content_enc).decode('utf-8') if msg.content_enc else None,
        'timestamp': msg.timestamp.isoformat(),
        'deleted': msg.deleted
    } for msg in messages])

@app.route('/chat/<int:chat_id>/messages')
@login_required
def get_chat_messages(chat_id):
    chat = db.session.get(Chat, chat_id)
    # Check if user is participant in this chat
    if current_user.id not in [chat.user1_id, chat.user2_id]:
        return jsonify({"error": "Unauthorized"}), 403
    
    messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.asc()).all()
    
    return jsonify([{
        'id': msg.id,
        'sender_id': msg.sender_id,
        'content_enc': base64.b64encode(msg.content_enc).decode('utf-8') if msg.content_enc else None,
        'timestamp': msg.timestamp.isoformat(),
        'deleted': msg.deleted
    } for msg in messages])

@app.route('/group/delete/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    group = db.session.get(Group, group_id)
    # Только если пользователь состоит в группе (или создатель, если нужно)
    gm = GroupMember.query.filter_by(group_id=group.id, user_id=current_user.id).first()
    if not gm:
        flash('Нет доступа к удалению группы', 'danger')
        return redirect(url_for('index'))
    # Удаляем все сообщения, участников, саму группу
    Message.query.filter_by(group_id=group.id).delete()
    GroupMember.query.filter_by(group_id=group.id).delete()
    db.session.delete(group)
    db.session.commit()
    flash('Группа удалена', 'success')
    return redirect(url_for('index'))

@app.before_request
def check_ban():
    from flask_login import current_user, logout_user
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        if getattr(current_user, 'banned', False):
            logout_user()
            flash('Ваш аккаунт заблокирован', 'danger')
            return redirect(url_for('login'))

@app.route('/group/<invite_link>/remove_member/<int:user_id>', methods=['POST'])
@login_required
def remove_group_member(invite_link, user_id):
    # Находим группу по invite_link
    groups = Group.query.all()
    found = None
    for group in groups:
        try:
            dec_link = group.invite_link_enc.decode('utf-8')
            if dec_link == invite_link:
                found = group
                break
        except Exception:
            continue
    if not found:
        flash('Группа не найдена', 'danger')
        return redirect(url_for('index'))
    
    # Проверяем, что пользователь является создателем группы
    if found.creator_id != current_user.id:
        flash('Только создатель группы может удалять участников', 'danger')
        return redirect(url_for('group_chat', invite_link=invite_link))
    
    # Удаляем участника
    member = GroupMember.query.filter_by(group_id=found.id, user_id=user_id).first()
    if member:
        db.session.delete(member)
        db.session.commit()
        flash('Участник удален из группы', 'success')
    else:
        flash('Участник не найден', 'danger')
    
    return redirect(url_for('group_chat', invite_link=invite_link))

@app.route('/group/<invite_link>/copy_link', methods=['POST'])
@login_required
def copy_group_link(invite_link):
    # Находим группу по invite_link
    groups = Group.query.all()
    found = None
    for group in groups:
        try:
            dec_link = group.invite_link_enc.decode('utf-8')
            if dec_link == invite_link:
                found = group
                break
        except Exception:
            continue
    if not found:
        flash('Группа не найдена', 'danger')
        return redirect(url_for('index'))
    
    # Проверяем, что пользователь участник группы
    if not GroupMember.query.filter_by(group_id=found.id, user_id=current_user.id).first():
        flash('Вы не участник этой группы', 'danger')
        return redirect(url_for('index'))
    
    # Формируем полную ссылку для приглашения
    invite_url = request.host_url.rstrip('/') + url_for('join_group', invite_link=invite_link)
    flash(f'Ссылка скопирована: {invite_url}', 'success')
    
    return redirect(url_for('group_chat', invite_link=invite_link))

@app.route('/group/<invite_link>/members')
@login_required
def group_members(invite_link):
    # Находим группу по invite_link
    groups = Group.query.all()
    found = None
    for group in groups:
        try:
            dec_link = group.invite_link_enc.decode('utf-8')
            if dec_link == invite_link:
                found = group
                break
        except Exception:
            continue
    if not found:
        flash('Группа не найдена', 'danger')
        return redirect(url_for('index'))
    
    # Проверяем, что пользователь участник группы
    if not GroupMember.query.filter_by(group_id=found.id, user_id=current_user.id).first():
        flash('Вы не участник этой группы', 'danger')
        return redirect(url_for('index'))
    
    # Получаем список участников
    members = GroupMember.query.filter_by(group_id=found.id).all()
    member_list = []
    for member in members:
        user = db.session.get(User, member.user_id)
        if user:
            member_list.append({
                'id': user.id,
                'nickname': user.nickname_enc,
                'is_creator': found.creator_id == user.id
            })
    
    return render_template('group_members.html', 
                         group=found, 
                         members=member_list, 
                         invite_link=invite_link,
                         is_creator=found.creator_id == current_user.id)

@app.route('/group/<invite_link>/invite_by_nickname', methods=['POST'])
@login_required
def invite_by_nickname(invite_link):
    # Находим группу по invite_link
    groups = Group.query.all()
    found = None
    for group in groups:
        try:
            dec_link = group.invite_link_enc.decode('utf-8')
            if dec_link == invite_link:
                found = group
                break
        except Exception:
            continue
    if not found:
        return jsonify({'success': False, 'message': 'Группа не найдена'})
    
    # Проверяем, что пользователь является создателем группы
    if found.creator_id != current_user.id:
        return jsonify({'success': False, 'message': 'Только создатель группы может приглашать участников'})
    
    # Получаем данные из JSON
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Неверный формат данных'})
    
    nickname = data.get('nickname', '').strip()
    if not nickname:
        return jsonify({'success': False, 'message': 'Введите ник пользователя'})
    
    # Ищем пользователя по нику
    user = User.query.filter_by(nickname_enc=nickname).first()
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь с таким ником не найден'})
    
    # Проверяем, не состоит ли уже пользователь в группе
    existing_member = GroupMember.query.filter_by(group_id=found.id, user_id=user.id).first()
    if existing_member:
        return jsonify({'success': False, 'message': 'Пользователь уже состоит в группе'})
    
    # Добавляем пользователя в группу
    new_member = GroupMember(group_id=found.id, user_id=user.id)
    db.session.add(new_member)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Пользователь {nickname} успешно приглашен в группу!'})

@app.route('/user/<int:user_id>/public_key')
@login_required
def get_user_public_key(user_id):
    """Получить публичный ключ пользователя"""
    user = User.query.get_or_404(user_id)
    if user.public_key:
        return jsonify({
            'user_id': user.id,
            'nickname': user.nickname_enc,
            'public_key': user.public_key.decode('utf-8')
        })
    else:
        return jsonify({'error': 'Public key not found'}), 404

@app.route('/user/update_public_key', methods=['POST'])
@login_required
def update_public_key():
    """Обновить свой публичный ключ"""
    public_key = request.form.get('public_key', '').strip()
    if public_key:
        current_user.public_key = public_key.encode('utf-8')
        db.session.commit()
        flash('Публичный ключ обновлен', 'success')
    else:
        flash('Ключ не может быть пустым', 'danger')
    return redirect(url_for('index'))

@app.route('/chat/<int:chat_id>/sync_keys', methods=['POST'])
@login_required
def sync_chat_keys(chat_id):
    """Синхронизация ключей в чате - установка одинакового ключа обоим пользователям"""
    chat = db.session.get(Chat, chat_id)
    if current_user.id not in [chat.user1_id, chat.user2_id]:
        flash('Нет доступа к этому чату', 'danger')
        return redirect(url_for('index'))
    
    # Выбираем ключ на основе ID чата (чтобы для одного чата всегда был один ключ)
    selected_key = PRESET_KEYS[chat_id % len(PRESET_KEYS)]
    
    print(f"🔑 Синхронизация ключей для чата {chat_id}: выбран ключ {selected_key}")
    
    # Обновляем ключ чата (этот ключ будет использоваться обоими пользователями)
    chat.key_enc = selected_key.encode('utf-8')
    db.session.commit()
    
    # Получаем информацию о собеседнике
    other_id = chat.user2_id if chat.user1_id == current_user.id else chat.user1_id
    other_user = db.session.get(User, other_id)
    
    if not other_user:
        flash('Собеседник не найден', 'danger')
        return redirect(url_for('chat', chat_id=chat_id))
    
    # Возвращаем JSON с ключом для JavaScript
    return jsonify({
        'success': True,
        'message': f'Ключи синхронизированы с пользователем {other_user.nickname_enc}',
        'chat_key': selected_key,
        'other_user_nickname': other_user.nickname_enc
    })

@app.route('/user/generate_key', methods=['POST'])
@login_required
def generate_user_key():
    """Генерация нового публичного ключа пользователя"""
    key = os.urandom(32)  # 256 бит
    current_user.public_key = base64.b64encode(key)
    db.session.commit()
    flash('Новый публичный ключ сгенерирован', 'success')
    return redirect(url_for('index'))

@app.route('/user/generate_key_json', methods=['POST'])
@login_required
def generate_user_key_json():
    """Генерация нового ключа для чата/группы (возвращает JSON)"""
    try:
        # Генерируем случайный ключ
        key = os.urandom(32)  # 256 бит
        key_b64 = base64.b64encode(key).decode('utf-8')
        
        return jsonify({
            'success': True,
            'key': key_b64
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Ошибка генерации ключа: {str(e)}'
        }), 500

@app.route('/notifications/unread_count')
@login_required
def get_unread_count():
    """Получить количество непрочитанных сообщений по чатам"""
    # Получаем все чаты пользователя
    user_chats = Chat.query.filter(
        (Chat.user1_id == current_user.id) | (Chat.user2_id == current_user.id)
    ).all()
    
    # Получаем все группы пользователя
    user_groups = GroupMember.query.filter_by(user_id=current_user.id).all()
    
    chat_unread = {}
    total_unread = 0
    
    # Проверяем личные чаты
    for chat in user_chats:
        # Определяем, какой пользователь мы в этом чате
        is_user1 = chat.user1_id == current_user.id
        last_read_field = 'last_read_user1' if is_user1 else 'last_read_user2'
        last_read_time = getattr(chat, last_read_field)
        
        # Получаем количество непрочитанных сообщений
        if last_read_time:
            # Считаем сообщения после последнего прочтения
            unread_count = Message.query.filter(
                Message.chat_id == chat.id,
                Message.sender_id != current_user.id,
                Message.timestamp > last_read_time
            ).count()
        else:
            # Если никогда не читал, считаем все сообщения от собеседника
            unread_count = Message.query.filter(
                Message.chat_id == chat.id,
                Message.sender_id != current_user.id
            ).count()
        
        if unread_count > 0:
            # Определяем собеседника
            other_id = chat.user2_id if is_user1 else chat.user1_id
            other_user = db.session.get(User, other_id)
            if other_user:
                chat_unread[f'chat_{chat.id}'] = {
                    'nickname': other_user.nickname_enc,
                    'count': unread_count
                }
                total_unread += unread_count
    
    # Проверяем групповые чаты
    for group_member in user_groups:
        group = db.session.get(Group, group_member.group_id)
        if group:
            last_read_time = group_member.last_read
            
            # Получаем количество непрочитанных сообщений
            if last_read_time:
                # Считаем сообщения после последнего прочтения
                unread_count = Message.query.filter(
                    Message.group_id == group.id,
                    Message.sender_id != current_user.id,
                    Message.timestamp > last_read_time
                ).count()
            else:
                # Если никогда не читал, считаем все сообщения в группе
                unread_count = Message.query.filter(
                    Message.group_id == group.id,
                    Message.sender_id != current_user.id
                ).count()
            
            if unread_count > 0:
                chat_unread[f'group_{group.id}'] = {
                    'nickname': group.name_enc.decode('utf-8'),
                    'count': unread_count
                }
                total_unread += unread_count
    
    return jsonify({
        'total_unread': total_unread,
        'chat_unread': chat_unread
    })

@app.route('/chat/<int:chat_id>/mark_read', methods=['POST'])
@login_required
def mark_chat_read(chat_id):
    """Отметить сообщения в чате как прочитанные"""
    chat = db.session.get(Chat, chat_id)
    if current_user.id not in [chat.user1_id, chat.user2_id]:
        return jsonify({'error': 'Нет доступа к этому чату'}), 403
    
    # Определяем, какой пользователь мы в этом чате
    is_user1 = chat.user1_id == current_user.id
    last_read_field = 'last_read_user1' if is_user1 else 'last_read_user2'
    
    # Обновляем время последнего прочтения
    from datetime import datetime
    setattr(chat, last_read_field, datetime.now(UTC))
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/group/<invite_link>/mark_read', methods=['POST'])
@login_required
def mark_group_read(invite_link):
    """Отметить сообщения в группе как прочитанные"""
    # Находим группу по invite_link
    groups = Group.query.all()
    found = None
    for group in groups:
        try:
            dec_link = group.invite_link_enc.decode('utf-8')
            if dec_link == invite_link:
                found = group
                break
        except Exception:
            continue
    
    if not found:
        return jsonify({'error': 'Группа не найдена'}), 404
    
    # Проверяем, что пользователь участник группы
    group_member = GroupMember.query.filter_by(group_id=found.id, user_id=current_user.id).first()
    if not group_member:
        return jsonify({'error': 'Вы не участник этой группы'}), 403
    
    # Обновляем время последнего прочтения
    from datetime import datetime
    group_member.last_read = datetime.now(UTC)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/group/<invite_link>/set_key', methods=['POST'])
@login_required
def set_group_key(invite_link):
    group = Group.query.filter_by(invite_link_enc=invite_link.encode('utf-8')).first_or_404()
    
    # Security check: Only the creator can set the key
    if current_user.id != group.creator_id:
        return jsonify({'success': False, 'message': 'Только создатель может менять ключ'}), 403

    data = request.get_json()
    new_key_b64 = data.get('key')

    if not new_key_b64:
        return jsonify({'success': False, 'message': 'Ключ не предоставлен'}), 400

    # Validate base64
    try:
        # It's already base64, but we need to store it as bytes in the DB
        group.session_key = base64.b64decode(new_key_b64)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Ключ группы обновлен'})
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Неверный формат ключа (не base64)'}), 400

@app.route('/group/<invite_link>/members')
@login_required
def get_group_members(invite_link):
    """Получение списка участников группы"""
    # Находим группу по invite_link
    found = None
    for group in Group.query.all():
        try:
            if group.invite_link_enc.decode('utf-8') == invite_link:
                found = group
                break
        except Exception:
            continue
    
    if not found:
        return jsonify({'error': 'Группа не найдена'}), 404
    
    # Проверяем, что пользователь является участником группы
    if not GroupMember.query.filter_by(group_id=found.id, user_id=current_user.id).first():
        return jsonify({'error': 'Нет доступа к группе'}), 403
    
    # Получаем всех участников группы
    members = []
    group_members = GroupMember.query.filter_by(group_id=found.id).all()
    
    for gm in group_members:
        user = db.session.get(User, gm.user_id)
        if user:
            try:
                nickname = user.nickname_enc
                members.append({
                    'user_id': user.id,
                    'nickname': nickname,
                    'is_creator': user.id == found.creator_id
                })
            except Exception:
                members.append({
                    'user_id': user.id,
                    'nickname': 'Unknown',
                    'is_creator': user.id == found.creator_id
                })
    
    return jsonify({'members': members})

@app.route('/group/<invite_link>/sync_keys', methods=['POST'])
@login_required
def sync_group_keys(invite_link):
    group = Group.query.filter_by(invite_link_enc=invite_link.encode('utf-8')).first_or_404()
    if group.creator_id != current_user.id:
        return jsonify({'success': False, 'message': 'Только создатель группы может синхронизировать ключи'}), 403
    # Генерируем новый ключ
    import base64, os
    new_key = base64.b64encode(os.urandom(32))
    group.session_key = new_key
    db.session.commit()
    return jsonify({'success': True, 'key': new_key.decode('utf-8')})

# WebSocket handlers
@socketio.on('join_chat')
def on_join_chat(data):
    try:
        chat_id = data.get('chat_id')
        user_id = data.get('user_id')
        
        if not chat_id or not user_id:
            print(f'Missing required fields in join_chat: {data}')
            return
            
        room = f'chat_{chat_id}'
        join_room(room)
        print(f'User {user_id} joined chat {chat_id}')
    except Exception as e:
        print(f'Error in join_chat: {e}')

@socketio.on('join_group')
def on_join_group(data):
    try:
        invite_link = data.get('invite_link')
        user_id = data.get('user_id')
        
        if not invite_link or not user_id:
            print(f'Missing required fields in join_group: {data}')
            return
            
        room = f'group_{invite_link}'
        join_room(room)
        print(f'User {user_id} joined group {invite_link}')
    except Exception as e:
        print(f'Error in join_group: {e}')

@socketio.on('leave_chat')
def on_leave_chat(data):
    try:
        chat_id = data.get('chat_id')
        user_id = data.get('user_id')
        
        if not chat_id or not user_id:
            print(f'Missing required fields in leave_chat: {data}')
            return
            
        room = f'chat_{chat_id}'
        leave_room(room)
        print(f'User {user_id} left chat {chat_id}')
    except Exception as e:
        print(f'Error in leave_chat: {e}')

@socketio.on('leave_group')
def on_leave_group(data):
    try:
        invite_link = data.get('invite_link')
        user_id = data.get('user_id')
        
        if not invite_link or not user_id:
            print(f'Missing required fields in leave_group: {data}')
            return
            
        room = f'group_{invite_link}'
        leave_room(room)
        print(f'User {user_id} left group {invite_link}')
    except Exception as e:
        print(f'Error in leave_group: {e}')

@socketio.on('send_message')
def on_send_message(data):
    """Обработка отправки сообщения в личном чате"""
    try:
        content = data.get('content')
        recipient_id = data.get('recipient_id')
        sender_id = data.get('sender_id')
        
        # Проверяем, что отправитель - текущий пользователь
        if sender_id != current_user.id:
            return
        
        # Находим чат между пользователями
        chat = Chat.query.filter(
            or_(
                (Chat.user1_id == sender_id) & (Chat.user2_id == recipient_id),
                (Chat.user1_id == recipient_id) & (Chat.user2_id == sender_id)
            )
        ).first()
        
        if not chat:
            return
        
        # Сохраняем сообщение в базе данных
        new_message = Message(
            chat_id=chat.id,
            sender_id=sender_id,
            content_enc=content.encode('utf-8')
        )
        db.session.add(new_message)
        db.session.commit()
        
        # Отправляем сообщение через Socket.IO
        message_data = {
            'id': new_message.id,
            'chat_id': chat.id,
            'sender_id': sender_id,
            'sender_nickname': current_user.nickname_enc,
            'content': content,
            'timestamp': new_message.timestamp.isoformat(),
            'file_url': None
        }
        
        # Отправляем в комнату чата
        room = f'chat_{chat.id}'
        socketio.emit('new_message', message_data, room=room)
        
    except Exception as e:
        print(f'Error in send_message: {e}')

@socketio.on('send_group_message')
def on_send_group_message(data):
    """Обработка отправки сообщения в группе"""
    try:
        content = data.get('content')
        group_id = data.get('group_id')
        sender_id = data.get('sender_id')
        
        # Проверяем, что отправитель - текущий пользователь
        if sender_id != current_user.id:
            return
        
        # Проверяем, что пользователь является участником группы
        group_member = GroupMember.query.filter_by(group_id=group_id, user_id=sender_id).first()
        if not group_member:
            return
        
        # Получаем группу
        group = db.session.get(Group, group_id)
        if not group:
            return
        
        # Сохраняем сообщение в базе данных
        new_message = Message(
            group_id=group_id,
            sender_id=sender_id,
            content_enc=content.encode('utf-8')
        )
        db.session.add(new_message)
        db.session.commit()
        
        # Получаем информацию об отправителе
        sender = db.session.get(User, sender_id)
        sender_name = sender.nickname_enc if sender else 'Unknown'
        
        # Отправляем сообщение через Socket.IO
        message_data = {
            'id': new_message.id,
            'group_id': group.id,
            'sender_id': current_user.id,
            'sender_name': current_user.nickname_enc,
            'content': content,
            'timestamp': new_message.timestamp.isoformat(),
            'file_url': None
        }
        
        # Отправляем в комнату группы
        room = f'group_{group.invite_link_enc.decode("utf-8")}'
        socketio.emit('new_group_message', message_data, room=room)
        
    except Exception as e:
        print(f'Error in send_group_message: {e}')

def emit_new_message(room, message_data):
    """Отправляем новое сообщение через Socket.IO"""
    socketio.emit('new_message', message_data, room=room)

# Обработчики ошибок
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_code=404,
                         error_title='Страница не найдена',
                         error_message='Запрашиваемая страница не существует или была перемещена.',
                         error_details=str(error) if app.debug else None,
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         request_id=request.headers.get('X-Request-ID', 'N/A')), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html', 
                         error_code=403,
                         error_title='Доступ запрещен',
                         error_message='У вас нет прав для доступа к этой странице.',
                         error_details=str(error) if app.debug else None,
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         request_id=request.headers.get('X-Request-ID', 'N/A')), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', 
                         error_code=500,
                         error_title='Внутренняя ошибка сервера',
                         error_message='Произошла непредвиденная ошибка. Попробуйте обновить страницу или вернуться позже.',
                         error_details=str(error) if app.debug else None,
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         request_id=request.headers.get('X-Request-ID', 'N/A')), 500

@app.errorhandler(400)
def bad_request_error(error):
    return render_template('error.html', 
                         error_code=400,
                         error_title='Неверный запрос',
                         error_message='Запрос содержит ошибки или неверные данные.',
                         error_details=str(error) if app.debug else None,
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         request_id=request.headers.get('X-Request-ID', 'N/A')), 400

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('error.html', 
                         error_code=401,
                         error_title='Не авторизован',
                         error_message='Для доступа к этой странице необходимо войти в систему.',
                         error_details=str(error) if app.debug else None,
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         request_id=request.headers.get('X-Request-ID', 'N/A')), 401

# Универсальный обработчик для всех остальных ошибок
@app.errorhandler(Exception)
def handle_exception(error):
    db.session.rollback()
    return render_template('error.html', 
                         error_code=getattr(error, 'code', 500),
                         error_title='Ошибка приложения',
                         error_message='Произошла непредвиденная ошибка. Попробуйте обновить страницу.',
                         error_details=str(error) if app.debug else None,
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         request_id=request.headers.get('X-Request-ID', 'N/A')), getattr(error, 'code', 500)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Удаление профиля
        if request.form.get('delete_profile'):
            user_id = current_user.id
            logout_user()
            user = User.query.get(user_id)
            db.session.delete(user)
            db.session.commit()
            flash('Профиль удалён', 'success')
            return redirect(url_for('login'))

        # Смена аватарки
        avatar_choice = request.form.get('avatar_choice')
        avatar_upload = request.files.get('avatar_upload')
        if avatar_upload and avatar_upload.filename:
            filename = secure_filename(avatar_upload.filename)
            ext = filename.rsplit('.', 1)[-1].lower()
            if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                avatar_path = f'avatars/user_{current_user.id}.{ext}'
                avatar_upload.save(os.path.join(app.static_folder, avatar_path))
                current_user.avatar = avatar_path
        elif avatar_choice:
            current_user.avatar = avatar_choice

        # Тумблер анонимности
        current_user.anonymous_mode = bool(request.form.get('anonymous_mode'))
        # Глобальные ключи
        current_user.global_chat_key = request.form.get('global_chat_key', '').strip() or None
        current_user.global_group_key = request.form.get('global_group_key', '').strip() or None
        db.session.commit()
        flash('Настройки профиля обновлены', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=current_user)

@app.route('/channels/create', methods=['GET', 'POST'])
@login_required
def create_channel():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not name:
            flash('Введите название канала', 'danger')
            return render_template('create_channel.html')
        channel = Channel(name=name, description=description, creator_id=current_user.id)
        db.session.add(channel)
        db.session.commit()  # Сначала сохраняем канал, чтобы получить channel.id
        db.session.add(ChannelSubscriber(channel_id=channel.id, user_id=current_user.id))
        db.session.commit()
        flash('Канал создан!', 'success')
        return redirect(url_for('view_channel', channel_id=channel.id))
    return render_template('create_channel.html')

@app.route('/channel/<int:channel_id>', methods=['GET', 'POST'])
@login_required
def view_channel(channel_id):
    channel = db.session.get(Channel, channel_id)
    # Смена аватарки (только для создателя)
    if request.method == 'POST' and channel.creator_id == current_user.id:
        avatar_choice = request.form.get('avatar_choice')
        avatar_upload = request.files.get('avatar_upload')
        if avatar_upload and avatar_upload.filename:
            filename = secure_filename(avatar_upload.filename)
            ext = filename.rsplit('.', 1)[-1].lower()
            if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                avatar_path = f'avatars/channel_{channel.id}.{ext}'
                avatar_upload.save(os.path.join(app.static_folder, avatar_path))
                channel.avatar = avatar_path
        elif avatar_choice:
            channel.avatar = avatar_choice
        db.session.commit()
        flash('Аватарка канала обновлена', 'success')
        return redirect(url_for('view_channel', channel_id=channel.id))
    # Получаем посты с комментариями и авторами
    posts = channel.posts.order_by(ChannelPost.timestamp.desc()).all()
    for post in posts:
        post.comments = post.comments.order_by(ChannelComment.timestamp.asc()).all()
        for comment in post.comments:
            comment.author = db.session.get(User, comment.author_id)
    channel.posts = posts
    return render_template('channel.html', channel=channel)

@app.route('/channel/<int:channel_id>/delete', methods=['POST'])
@login_required
def delete_channel(channel_id):
    channel = db.session.get(Channel, channel_id)
    if channel.creator_id != current_user.id:
        flash('Нет прав на удаление канала', 'danger')
        return redirect(url_for('view_channel', channel_id=channel.id))
    # Мягкое удаление - устанавливаем флаг deleted
    channel.deleted = True
    db.session.commit()
    flash('Канал удалён', 'success')
    return redirect(url_for('index'))

@app.route('/channel/<int:channel_id>/post', methods=['POST'])
@login_required
def create_channel_post(channel_id):
    channel = db.session.get(Channel, channel_id)
    if channel.creator_id != current_user.id:
        flash('Только владелец может публиковать посты', 'danger')
        return redirect(url_for('view_channel', channel_id=channel_id))
    content = request.form.get('content', '').strip()
    file = request.files.get('file')
    file_url = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[-1].lower()
        # Поддерживаем все типы файлов
        allowed_extensions = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi', 'mp3', 'wav', 'pdf', 'doc', 'docx', 'txt', 'zip', 'rar', '7z']
        if ext in allowed_extensions:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'channel_{channel_id}_{uuid.uuid4().hex}_{filename}')
            file.save(file_path)
            file_url = url_for('static', filename='uploads/' + os.path.basename(file_path))
    if not content and not file_url:
        flash('Пост не может быть пустым', 'danger')
        return redirect(url_for('view_channel', channel_id=channel_id))
    post_content = content or ''
    if file_url:
        post_content += f' [file:{file_url}]'
    post = ChannelPost(channel_id=channel_id, author_id=current_user.id, content=post_content)
    db.session.add(post)
    db.session.commit()
    flash('Пост опубликован', 'success')
    return redirect(url_for('view_channel', channel_id=channel_id))

@app.route('/channel/<int:channel_id>/subscribe', methods=['POST'])
@login_required
def subscribe_channel(channel_id):
    channel = db.session.get(Channel, channel_id)
    if ChannelSubscriber.query.filter_by(channel_id=channel_id, user_id=current_user.id).first():
        flash('Вы уже подписаны', 'info')
    else:
        db.session.add(ChannelSubscriber(channel_id=channel_id, user_id=current_user.id))
        db.session.commit()
        flash('Вы подписались на канал', 'success')
    return redirect(url_for('view_channel', channel_id=channel_id))

@app.route('/channel/<int:channel_id>/unsubscribe', methods=['POST'])
@login_required
def unsubscribe_channel(channel_id):
    sub = ChannelSubscriber.query.filter_by(channel_id=channel_id, user_id=current_user.id).first()
    if sub:
        db.session.delete(sub)
        db.session.commit()
        flash('Вы отписались от канала', 'success')
    else:
        flash('Вы не были подписаны', 'info')
    return redirect(url_for('view_channel', channel_id=channel_id))

@app.route('/channel/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_channel_comment(post_id):
    post = ChannelPost.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()
    file = request.files.get('file')
    file_url = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[-1].lower()
        # Поддерживаем все типы файлов
        allowed_extensions = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi', 'mp3', 'wav', 'pdf', 'doc', 'docx', 'txt', 'zip', 'rar', '7z']
        if ext in allowed_extensions:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'channel_comment_{post_id}_{uuid.uuid4().hex}_{filename}')
            file.save(file_path)
            file_url = url_for('static', filename='uploads/' + os.path.basename(file_path))
    if not content and not file_url:
        flash('Комментарий не может быть пустым', 'danger')
        return redirect(url_for('view_channel', channel_id=post.channel_id))
    comment_content = content or ''
    if file_url:
        comment_content += f' [file:{file_url}]'
    comment = ChannelComment(post_id=post_id, author_id=current_user.id, content=comment_content)
    db.session.add(comment)
    db.session.commit()
    flash('Комментарий добавлен', 'success')
    return redirect(url_for('view_channel', channel_id=post.channel_id))

@app.route('/channel/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_channel_post(post_id):
    post = ChannelPost.query.get_or_404(post_id)
    channel = db.session.get(Channel, post.channel_id)
    if current_user.id != post.author_id and current_user.id != channel.creator_id:
        flash('Нет прав на удаление поста', 'danger')
        return redirect(url_for('view_channel', channel_id=channel.id))
    db.session.delete(post)
    db.session.commit()
    flash('Пост удалён', 'success')
    return redirect(url_for('view_channel', channel_id=channel.id))

@app.route('/send_message/<int:chat_id>', methods=['POST'])
@login_required
def send_message(chat_id):
    """Отправка сообщения в личный чат"""
    try:
        # Находим чат
        chat = db.session.get(Chat, chat_id)
        if not chat:
            return jsonify({'success': False, 'message': 'Чат не найден'}), 404
        
        # Проверяем, что текущий пользователь является участником чата
        if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
            return jsonify({'success': False, 'message': 'Доступ запрещен'}), 403
        
        # Получаем данные
        content = request.form.get('content_enc', '').strip()
        file = request.files.get('file')
        
        if not content and not file:
            return jsonify({'success': False, 'message': 'Сообщение не может быть пустым'}), 400
        
        # Обрабатываем файл, если он есть
        file_url = None
        if file and file.filename:
            try:
                # Проверяем размер файла (максимум 10MB)
                file.seek(0, 2)  # Перемещаемся в конец файла
                file_size = file.tell()
                file.seek(0)  # Возвращаемся в начало
                
                if file_size > 10 * 1024 * 1024:  # 10MB
                    return jsonify({'success': False, 'message': 'Файл слишком большой (максимум 10MB)'}), 400
                
                # Проверяем расширение файла
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi', 'mp3', 'wav', 'pdf', 'doc', 'docx', 'txt', 'zip', 'rar', '7z'}
                file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                
                if file_ext not in allowed_extensions:
                    return jsonify({'success': False, 'message': f'Недопустимый тип файла. Разрешены: {", ".join(allowed_extensions)}'}), 400
                
                # Сохраняем файл
                filename = secure_filename(file.filename)
                if not filename:
                    return jsonify({'success': False, 'message': 'Недопустимое имя файла'}), 400
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"chat_{chat_id}_{timestamp}_{filename}"
                
                # Создаем папку uploads если её нет
                upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                file_url = f"/static/uploads/{unique_filename}"
                
                # Добавляем информацию о файле к контенту
                if content:
                    content += f" [file:{file_url}]"
                else:
                    content = f"[file:{file_url}]"
            except Exception as file_error:
                print(f'Error saving file: {file_error}')
                return jsonify({'success': False, 'message': 'Ошибка сохранения файла'}), 500
        
        # Сохраняем сообщение в базе данных
        new_message = Message(
            chat_id=chat_id,
            sender_id=current_user.id,
            content_enc=content.encode('utf-8')
        )
        db.session.add(new_message)
        db.session.commit()
        
        # Отправляем сообщение через Socket.IO
        message_data = {
            'id': new_message.id,
            'chat_id': chat_id,
            'sender_id': current_user.id,
            'sender_nickname': current_user.nickname_enc,
            'content': content,
            'timestamp': new_message.timestamp.isoformat(),
            'file_url': file_url
        }
        
        # Отправляем в комнату чата
        room = f'chat_{chat_id}'
        socketio.emit('new_message', message_data, room=room)
        
        return jsonify({'success': True, 'message': 'Сообщение отправлено'})
        
    except Exception as e:
        db.session.rollback()
        print(f'Error in send_message route: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Ошибка отправки сообщения: {str(e)}'}), 500

@app.route('/send_group_message/<invite_link>', methods=['POST'])
@login_required
def send_group_message(invite_link):
    """Отправка сообщения в групповой чат"""
    try:
        # Находим группу
        group = Group.query.filter_by(invite_link_enc=invite_link.encode('utf-8')).first()
        if not group:
            return jsonify({'success': False, 'message': 'Группа не найдена'}), 404
        
        # Проверяем, что пользователь является участником группы
        group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_user.id).first()
        if not group_member:
            return jsonify({'success': False, 'message': 'Вы не являетесь участником группы'}), 403
        
        # Получаем данные
        content = request.form.get('content_enc', '').strip()
        file = request.files.get('file')
        
        if not content and not file:
            return jsonify({'success': False, 'message': 'Сообщение не может быть пустым'}), 400
        
        # Обрабатываем файл, если он есть
        file_url = None
        if file and file.filename:
            try:
                # Проверяем размер файла (максимум 10MB)
                file.seek(0, 2)  # Перемещаемся в конец файла
                file_size = file.tell()
                file.seek(0)  # Возвращаемся в начало
                
                if file_size > 10 * 1024 * 1024:  # 10MB
                    return jsonify({'success': False, 'message': 'Файл слишком большой (максимум 10MB)'}), 400
                
                # Проверяем расширение файла
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi', 'mp3', 'wav', 'pdf', 'doc', 'docx', 'txt', 'zip', 'rar', '7z'}
                file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                
                if file_ext not in allowed_extensions:
                    return jsonify({'success': False, 'message': f'Недопустимый тип файла. Разрешены: {", ".join(allowed_extensions)}'}), 400
                
                # Сохраняем файл
                filename = secure_filename(file.filename)
                if not filename:
                    return jsonify({'success': False, 'message': 'Недопустимое имя файла'}), 400
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"group_{group.id}_{timestamp}_{filename}"
                
                # Создаем папку uploads если её нет
                upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                file_url = f"/static/uploads/{unique_filename}"
                
                # Добавляем информацию о файле к контенту
                if content:
                    content += f" [file:{file_url}]"
                else:
                    content = f"[file:{file_url}]"
            except Exception as file_error:
                print(f'Error saving file: {file_error}')
                return jsonify({'success': False, 'message': 'Ошибка сохранения файла'}), 500
        
        # Сохраняем сообщение в базе данных
        new_message = Message(
            group_id=group.id,
            sender_id=current_user.id,
            content_enc=content.encode('utf-8')
        )
        db.session.add(new_message)
        db.session.commit()
        
        # Отправляем сообщение через Socket.IO
        message_data = {
            'id': new_message.id,
            'group_id': group.id,
            'sender_id': current_user.id,
            'sender_name': current_user.nickname_enc,
            'content': content,
            'timestamp': new_message.timestamp.isoformat(),
            'file_url': file_url
        }
        
        # Отправляем в комнату группы
        room = f'group_{invite_link}'
        socketio.emit('new_group_message', message_data, room=room)
        
        return jsonify({'success': True, 'message': 'Сообщение отправлено'})
        
    except Exception as e:
        db.session.rollback()
        print(f'Error in send_group_message route: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Ошибка отправки сообщения: {str(e)}'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(nickname_enc='azazel').first():
            admin = User(
                nickname_enc='azazel',
                password_hash=hash_password('Log1progress'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
    
    # Получаем порт из переменной окружения или используем 10000 по умолчанию
    port = int(os.environ.get("PORT", 10000))
    try:
        import eventlet
        import eventlet.wsgi
        socketio.run(app, debug=False, host='0.0.0.0', port=port)
    except ImportError:
        socketio.run(app, debug=False, host='0.0.0.0', port=port) 