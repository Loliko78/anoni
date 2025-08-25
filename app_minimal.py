#!/usr/bin/env python3
"""
Минимальная версия Flask приложения без SQLAlchemy
для обхода проблем с eventlet и Python 3.13
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import sqlite3
import os
import datetime
import uuid
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Константы
NICKNAME_KEY = "your-secret-key-here"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
DB_PATH = 'instance/harvest.db'

# Создаем Flask приложение
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Создаем папку для загрузок
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    """Получение соединения с базой данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encrypt_nickname(nickname):
    """Шифрование никнейма"""
    key = hashlib.sha256(NICKNAME_KEY.encode()).digest()
    cipher = Cipher(algorithms.AES(key), modes.GCM(), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(nickname.encode()) + encryptor.finalize()
    return base64.b64encode(encryptor.tag + ciphertext).decode()

def decrypt_nickname(encrypted_nickname):
    """Расшифровка никнейма"""
    try:
        key = hashlib.sha256(NICKNAME_KEY.encode()).digest()
        data = base64.b64decode(encrypted_nickname.encode())
        tag = data[:16]
        ciphertext = data[16:]
        cipher = Cipher(algorithms.AES(key), modes.GCM(tag), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode()
    except:
        return encrypted_nickname

# Простая система сессий
sessions = {}

def get_current_user():
    """Получение текущего пользователя из сессии"""
    session_id = request.cookies.get('session_id')
    if session_id and session_id in sessions:
        user_id = sessions[session_id]
        conn = get_db()
        user = conn.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        return user
    return None

def login_required(f):
    """Декоратор для проверки авторизации"""
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('Необходима авторизация', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Маршруты
@app.route('/')
@login_required
def index():
    """Главная страница с чатами"""
    user = get_current_user()
    
    if user['banned']:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('login'))
    
    conn = get_db()
    
    # Получаем чаты пользователя
    chats = conn.execute('''
        SELECT c.*, u1.nickname_enc as user1_nickname, u2.nickname_enc as user2_nickname
        FROM chat c
        JOIN user u1 ON c.user1_id = u1.id
        JOIN user u2 ON c.user2_id = u2.id
        WHERE c.user1_id = ? OR c.user2_id = ?
    ''', (user['id'], user['id'])).fetchall()
    
    # Получаем последние сообщения для каждого чата
    chat_list = []
    for chat in chats:
        last_message = conn.execute('''
            SELECT * FROM message 
            WHERE chat_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (chat['id'],)).fetchone()
        
        # Определяем собеседника
        if chat['user1_id'] == user['id']:
            other_nickname = decrypt_nickname(chat['user2_nickname'])
        else:
            other_nickname = decrypt_nickname(chat['user1_nickname'])
        
        chat_list.append({
            'chat': chat,
            'other_nickname': other_nickname,
            'last_message': last_message
        })
    
    conn.close()
    
    return render_template('chats.html', chats=chat_list, NICKNAME_KEY=NICKNAME_KEY)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация пользователя"""
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        
        conn = get_db()
        
        # Проверяем, что никнейм не занят
        existing_user = conn.execute(
            'SELECT id FROM user WHERE nickname_enc = ?', 
            (encrypt_nickname(nickname),)
        ).fetchone()
        
        if existing_user:
            flash('Позывной уже занят', 'danger')
            conn.close()
            return render_template('register.html')
        
        # Создаем нового пользователя
        conn.execute('''
            INSERT INTO user (nickname_enc, password_hash, harvest_tokens)
            VALUES (?, ?, 0.0)
        ''', (encrypt_nickname(nickname), generate_password_hash(password)))
        
        conn.commit()
        conn.close()
        
        flash('Регистрация успешна! Теперь войдите в систему', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Вход в систему"""
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        
        conn = get_db()
        
        # Ищем пользователя
        user = conn.execute(
            'SELECT * FROM user WHERE nickname_enc = ?', 
            (encrypt_nickname(nickname),)
        ).fetchone()
        
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            if user['banned']:
                flash('Ваш аккаунт заблокирован', 'danger')
                return render_template('login.html')
            
            # Создаем сессию
            session_id = str(uuid.uuid4())
            sessions[session_id] = user['id']
            
            response = redirect(url_for('index'))
            response.set_cookie('session_id', session_id)
            return response
        else:
            flash('Неверный позывной или пароль', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Выход из системы"""
    session_id = request.cookies.get('session_id')
    if session_id in sessions:
        del sessions[session_id]
    
    response = redirect(url_for('login'))
    response.delete_cookie('session_id')
    return response

@app.route('/profile')
@login_required
def profile():
    """Профиль пользователя"""
    user = get_current_user()
    
    if user['banned']:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user, NICKNAME_KEY=NICKNAME_KEY)

@app.route('/marketplace')
@login_required
def marketplace():
    """Страница маркетплейса"""
    user = get_current_user()
    
    if user['banned']:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('login'))
    
    conn = get_db()
    
    # Получаем активные объявления
    listings = conn.execute('''
        SELECT ml.*, u.nickname_enc as seller_nickname
        FROM market_listing ml
        JOIN user u ON ml.seller_id = u.id
        WHERE ml.status = 'active'
        ORDER BY ml.created_at DESC
    ''').fetchall()
    
    # Получаем объявления пользователя
    my_listings = conn.execute('''
        SELECT * FROM market_listing 
        WHERE seller_id = ? 
        ORDER BY created_at DESC
    ''', (user['id'],)).fetchall()
    
    # Получаем покупки пользователя
    my_purchases = conn.execute('''
        SELECT mp.*, ml.title as listing_title
        FROM market_purchase mp
        JOIN market_listing ml ON mp.listing_id = ml.id
        WHERE mp.buyer_id = ?
        ORDER BY mp.created_at DESC
    ''', (user['id'],)).fetchall()
    
    # Получаем продажи пользователя
    my_sales = conn.execute('''
        SELECT mp.*, ml.title as listing_title
        FROM market_purchase mp
        JOIN market_listing ml ON mp.listing_id = ml.id
        WHERE mp.seller_id = ?
        ORDER BY mp.created_at DESC
    ''', (user['id'],)).fetchall()
    
    conn.close()
    
    return render_template('marketplace.html', 
                         listings=listings, 
                         my_listings=my_listings,
                         my_purchases=my_purchases,
                         my_sales=my_sales)

@app.route('/search')
@login_required
def search():
    """Поиск пользователей"""
    user = get_current_user()
    
    if user['banned']:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('login'))
    
    query = request.args.get('q', '')
    users = []
    
    if query:
        conn = get_db()
        all_users = conn.execute('SELECT * FROM user WHERE id != ?', (user['id'],)).fetchall()
        conn.close()
        
        for user_row in all_users:
            try:
                decrypted_nickname = decrypt_nickname(user_row['nickname_enc'])
                if query.lower() in decrypted_nickname.lower():
                    users.append(user_row)
            except:
                continue
    
    return render_template('search.html', users=users, query=query, NICKNAME_KEY=NICKNAME_KEY)

@app.route('/start_chat/<int:user_id>')
@login_required
def start_chat(user_id):
    """Начать чат с пользователем"""
    user = get_current_user()
    
    if user['banned']:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('login'))
    
    if user_id == user['id']:
        flash('Нельзя начать чат с самим собой', 'danger')
        return redirect(url_for('search'))
    
    conn = get_db()
    
    # Проверяем, существует ли уже чат
    existing_chat = conn.execute('''
        SELECT id FROM chat 
        WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)
    ''', (user['id'], user_id, user_id, user['id'])).fetchone()
    
    if existing_chat:
        conn.close()
        return redirect(url_for('chat', chat_id=existing_chat['id']))
    
    # Создаем новый чат
    conn.execute('INSERT INTO chat (user1_id, user2_id) VALUES (?, ?)', (user['id'], user_id))
    conn.commit()
    
    # Получаем ID нового чата
    new_chat = conn.execute('SELECT id FROM chat WHERE user1_id = ? AND user2_id = ?', (user['id'], user_id)).fetchone()
    conn.close()
    
    return redirect(url_for('chat', chat_id=new_chat['id']))

@app.route('/chat/<int:chat_id>')
@login_required
def chat(chat_id):
    """Страница чата"""
    user = get_current_user()
    
    if user['banned']:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('login'))
    
    conn = get_db()
    
    # Проверяем, что пользователь участвует в чате
    chat = conn.execute('''
        SELECT * FROM chat 
        WHERE id = ? AND (user1_id = ? OR user2_id = ?)
    ''', (chat_id, user['id'], user['id'])).fetchone()
    
    if not chat:
        conn.close()
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('index'))
    
    # Определяем собеседника
    if chat['user1_id'] == user['id']:
        other_user = conn.execute('SELECT * FROM user WHERE id = ?', (chat['user2_id'],)).fetchone()
    else:
        other_user = conn.execute('SELECT * FROM user WHERE id = ?', (chat['user1_id'],)).fetchone()
    
    # Получаем сообщения
    messages = conn.execute('''
        SELECT m.*, u.nickname_enc as sender_nickname
        FROM message m
        JOIN user u ON m.sender_id = u.id
        WHERE m.chat_id = ?
        ORDER BY m.timestamp
    ''', (chat_id,)).fetchall()
    
    conn.close()
    
    return render_template('chat.html', 
                         chat=chat, 
                         other_user=other_user, 
                         messages=messages, 
                         NICKNAME_KEY=NICKNAME_KEY)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """Отправка сообщения"""
    user = get_current_user()
    
    if user['banned']:
        return jsonify({'error': 'Аккаунт заблокирован'}), 403
    
    chat_id = request.form.get('chat_id')
    message_text = request.form.get('message')
    
    if not chat_id or not message_text:
        return jsonify({'error': 'Неверные данные'}), 400
    
    conn = get_db()
    
    # Проверяем, что пользователь участвует в чате
    chat = conn.execute('''
        SELECT id FROM chat 
        WHERE id = ? AND (user1_id = ? OR user2_id = ?)
    ''', (chat_id, user['id'], user['id'])).fetchone()
    
    if not chat:
        conn.close()
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    # Создаем сообщение
    conn.execute('''
        INSERT INTO message (chat_id, sender_id, content)
        VALUES (?, ?, ?)
    ''', (chat_id, user['id'], message_text))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# Статические файлы
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Сервис загруженных файлов"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print("🚀 Запуск минимального Flask приложения...")
    print("📱 Локальный доступ: http://0.0.0.0:5000")
    print("💡 WebSocket функции отключены")
    print("💡 Нажмите Ctrl+C для остановки")
    
    app.run(host='0.0.0.0', port=5000, debug=False) 