#!/usr/bin/env python3
"""
Упрощенная версия Flask приложения без SocketIO
для обхода проблем с eventlet и Python 3.13
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import sqlite3
import datetime
import uuid
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import json

# Импортируем модели
from models import User, Chat, Message, File, Group, GroupMember, ReadTracking, Channel, ChannelPost, ChannelSubscriber, ChannelComment, MarketListing, MarketPurchase, TokenTransaction, SupportTicket

# Импортируем базу данных
from db import db

# Константы
NICKNAME_KEY = "your-secret-key-here"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

# Создаем Flask приложение
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/harvest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализируем базу данных
db.init_app(app)

# Инициализируем Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Создаем папку для загрузок
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

# Маршруты
@app.route('/')
@login_required
def index():
    """Главная страница с чатами"""
    if current_user.banned:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('login'))
    
    # Получаем чаты пользователя
    chats = Chat.query.filter(
        (Chat.user1_id == current_user.id) | (Chat.user2_id == current_user.id)
    ).all()
    
    # Получаем информацию о собеседниках
    chat_list = []
    for chat in chats:
        if chat.user1_id == current_user.id:
            other_user = chat.user2
        else:
            other_user = chat.user1
        
        # Получаем последнее сообщение
        last_message = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.desc()).first()
        
        chat_list.append({
            'chat': chat,
            'other_user': other_user,
            'last_message': last_message
        })
    
    return render_template('chats.html', chats=chat_list, NICKNAME_KEY=NICKNAME_KEY)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация пользователя"""
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        
        # Проверяем, что никнейм не занят
        existing_user = User.query.filter_by(nickname_enc=encrypt_nickname(nickname)).first()
        if existing_user:
            flash('Позывной уже занят', 'danger')
            return render_template('register.html')
        
        # Создаем нового пользователя
        user = User(
            nickname_enc=encrypt_nickname(nickname),
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь войдите в систему', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Вход в систему"""
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        
        # Ищем пользователя
        user = User.query.filter_by(nickname_enc=encrypt_nickname(nickname)).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user.banned:
                flash('Ваш аккаунт заблокирован', 'danger')
                return render_template('login.html')
            
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Неверный позывной или пароль', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/chat/<int:chat_id>')
@login_required
def chat(chat_id):
    """Страница чата"""
    if current_user.banned:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('login'))
    
    chat = Chat.query.get_or_404(chat_id)
    
    # Проверяем, что пользователь участвует в чате
    if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('index'))
    
    # Определяем собеседника
    if chat.user1_id == current_user.id:
        other_user = chat.user2
    else:
        other_user = chat.user1
    
    # Получаем сообщения
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    
    return render_template('chat.html', chat=chat, other_user=other_user, messages=messages, NICKNAME_KEY=NICKNAME_KEY)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """Отправка сообщения"""
    if current_user.banned:
        return jsonify({'error': 'Аккаунт заблокирован'}), 403
    
    chat_id = request.form.get('chat_id')
    message_text = request.form.get('message')
    
    if not chat_id or not message_text:
        return jsonify({'error': 'Неверные данные'}), 400
    
    chat = Chat.query.get(chat_id)
    if not chat or (chat.user1_id != current_user.id and chat.user2_id != current_user.id):
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    # Создаем сообщение
    message = Message(
        chat_id=chat_id,
        sender_id=current_user.id,
        content=message_text
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'success': True, 'message_id': message.id})

@app.route('/profile')
@login_required
def profile():
    """Профиль пользователя"""
    if current_user.banned:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=current_user, NICKNAME_KEY=NICKNAME_KEY)

@app.route('/search')
@login_required
def search():
    """Поиск пользователей"""
    if current_user.banned:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('login'))
    
    query = request.args.get('q', '')
    users = []
    
    if query:
        # Ищем пользователей по никнейму
        all_users = User.query.filter(User.id != current_user.id).all()
        for user in all_users:
            try:
                decrypted_nickname = decrypt_nickname(user.nickname_enc)
                if query.lower() in decrypted_nickname.lower():
                    users.append(user)
            except:
                continue
    
    return render_template('search.html', users=users, query=query, NICKNAME_KEY=NICKNAME_KEY)

@app.route('/start_chat/<int:user_id>')
@login_required
def start_chat(user_id):
    """Начать чат с пользователем"""
    if current_user.banned:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('login'))
    
    other_user = User.query.get_or_404(user_id)
    
    if other_user.id == current_user.id:
        flash('Нельзя начать чат с самим собой', 'danger')
        return redirect(url_for('search'))
    
    # Проверяем, существует ли уже чат
    existing_chat = Chat.query.filter(
        ((Chat.user1_id == current_user.id) & (Chat.user2_id == other_user.id)) |
        ((Chat.user1_id == other_user.id) & (Chat.user2_id == current_user.id))
    ).first()
    
    if existing_chat:
        return redirect(url_for('chat', chat_id=existing_chat.id))
    
    # Создаем новый чат
    chat = Chat(user1_id=current_user.id, user2_id=other_user.id)
    db.session.add(chat)
    db.session.commit()
    
    return redirect(url_for('chat', chat_id=chat.id))

# Маршруты для маркетплейса
@app.route('/marketplace')
@login_required
def marketplace():
    """Страница маркетплейса"""
    if current_user.banned:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('login'))
    
    # Получаем активные объявления
    listings = MarketListing.query.filter_by(status='active').order_by(MarketListing.created_at.desc()).all()
    
    # Получаем объявления пользователя
    my_listings = MarketListing.query.filter_by(seller_id=current_user.id).order_by(MarketListing.created_at.desc()).all()
    
    # Получаем покупки пользователя
    my_purchases = MarketPurchase.query.filter_by(buyer_id=current_user.id).order_by(MarketPurchase.created_at.desc()).all()
    
    # Получаем продажи пользователя
    my_sales = MarketPurchase.query.filter_by(seller_id=current_user.id).order_by(MarketPurchase.created_at.desc()).all()
    
    return render_template('marketplace.html', 
                         listings=listings, 
                         my_listings=my_listings,
                         my_purchases=my_purchases,
                         my_sales=my_sales)

@app.route('/marketplace/create_listing', methods=['POST'])
@login_required
def create_listing():
    """Создание нового объявления"""
    if current_user.banned:
        return jsonify({'error': 'Аккаунт заблокирован'}), 403
    
    title = request.form.get('title')
    description = request.form.get('description')
    price = request.form.get('price')
    category = request.form.get('category')
    
    if not all([title, description, price, category]):
        return jsonify({'error': 'Заполните все поля'}), 400
    
    try:
        price = float(price)
        if price <= 0:
            return jsonify({'error': 'Цена должна быть больше 0'}), 400
    except ValueError:
        return jsonify({'error': 'Неверная цена'}), 400
    
    # Обработка изображения
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"listing_{current_user.id}_{uuid.uuid4().hex}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = filename
    
    # Создаем объявление
    listing = MarketListing(
        seller_id=current_user.id,
        title=title,
        description=description,
        price=price,
        category=category,
        image_path=image_path
    )
    
    db.session.add(listing)
    db.session.commit()
    
    return jsonify({'success': True, 'listing_id': listing.id})

@app.route('/marketplace/buy/<int:listing_id>', methods=['POST'])
@login_required
def buy_listing(listing_id):
    """Покупка товара"""
    if current_user.banned:
        return jsonify({'error': 'Аккаунт заблокирован'}), 403
    
    listing = MarketListing.query.get_or_404(listing_id)
    
    if listing.seller_id == current_user.id:
        return jsonify({'error': 'Нельзя купить свой товар'}), 400
    
    if listing.status != 'active':
        return jsonify({'error': 'Товар недоступен'}), 400
    
    if current_user.harvest_tokens < listing.price:
        return jsonify({'error': 'Недостаточно токенов'}), 400
    
    # Создаем покупку
    purchase = MarketPurchase(
        listing_id=listing.id,
        buyer_id=current_user.id,
        seller_id=listing.seller_id,
        price=listing.price
    )
    
    db.session.add(purchase)
    db.session.commit()
    
    # Создаем или находим чат с продавцом
    existing_chat = Chat.query.filter(
        ((Chat.user1_id == current_user.id) & (Chat.user2_id == listing.seller_id)) |
        ((Chat.user1_id == listing.seller_id) & (Chat.user2_id == current_user.id))
    ).first()
    
    if not existing_chat:
        chat = Chat(user1_id=current_user.id, user2_id=listing.seller_id)
        db.session.add(chat)
        db.session.commit()
        chat_id = chat.id
    else:
        chat_id = existing_chat.id
    
    # Отправляем сообщение о покупке
    message = Message(
        chat_id=chat_id,
        sender_id=current_user.id,
        content=f"Покупаю товар: {listing.title} за {listing.price} HRVST"
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'success': True, 'chat_id': chat_id})

@app.route('/marketplace/confirm/<int:purchase_id>/<role>', methods=['POST'])
@login_required
def confirm_purchase(purchase_id, role):
    """Подтверждение покупки"""
    if current_user.banned:
        return jsonify({'error': 'Аккаунт заблокирован'}), 403
    
    purchase = MarketPurchase.query.get_or_404(purchase_id)
    
    if role == 'buyer' and purchase.buyer_id != current_user.id:
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    if role == 'seller' and purchase.seller_id != current_user.id:
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    if role == 'buyer':
        purchase.buyer_confirmed = True
    elif role == 'seller':
        purchase.seller_confirmed = True
    
    # Если оба подтвердили, завершаем сделку
    if purchase.buyer_confirmed and purchase.seller_confirmed:
        purchase.status = 'completed'
        purchase.completed_at = datetime.datetime.utcnow()
        
        # Переводим токены
        buyer = User.query.get(purchase.buyer_id)
        seller = User.query.get(purchase.seller_id)
        
        buyer.harvest_tokens -= purchase.price
        seller.harvest_tokens += purchase.price
        
        # Создаем записи транзакций
        buyer_transaction = TokenTransaction(
            user_id=buyer.id,
            transaction_type='market_purchase',
            amount=-purchase.price,
            balance_before=buyer.harvest_tokens + purchase.price,
            balance_after=buyer.harvest_tokens,
            description=f"Покупка: {purchase.listing.title}",
            related_purchase_id=purchase.id
        )
        
        seller_transaction = TokenTransaction(
            user_id=seller.id,
            transaction_type='market_sale',
            amount=purchase.price,
            balance_before=seller.harvest_tokens - purchase.price,
            balance_after=seller.harvest_tokens,
            description=f"Продажа: {purchase.listing.title}",
            related_purchase_id=purchase.id
        )
        
        db.session.add(buyer_transaction)
        db.session.add(seller_transaction)
        
        # Обновляем статус объявления
        purchase.listing.status = 'sold'
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/create_support_ticket', methods=['POST'])
@login_required
def create_support_ticket():
    """Создание обращения в поддержку"""
    if current_user.banned:
        return jsonify({'error': 'Аккаунт заблокирован'}), 403
    
    subject = request.form.get('subject')
    description = request.form.get('description')
    user_nickname = request.form.get('user_nickname')
    scammer_nickname = request.form.get('scammer_nickname')
    
    if not all([subject, description, user_nickname]):
        return jsonify({'error': 'Заполните обязательные поля'}), 400
    
    # Обработка изображения
    evidence_image = None
    if 'evidence_image' in request.files:
        file = request.files['evidence_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"support_{current_user.id}_{uuid.uuid4().hex}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            evidence_image = filename
    
    # Создаем обращение
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
    
    return jsonify({'success': True, 'ticket_id': ticket.id})

# Маршруты для управления токенами
@app.route('/buy_tokens', methods=['POST'])
@login_required
def buy_tokens():
    """Покупка токенов"""
    if current_user.banned:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('profile'))
    
    amount = request.form.get('amount')
    comment = request.form.get('comment')
    
    if not amount:
        flash('Укажите количество токенов', 'danger')
        return redirect(url_for('profile'))
    
    try:
        amount = int(amount)
        if amount <= 0:
            flash('Количество должно быть больше 0', 'danger')
            return redirect(url_for('profile'))
    except ValueError:
        flash('Неверное количество токенов', 'danger')
        return redirect(url_for('profile'))
    
    # Обработка скриншота оплаты
    payment_proof = None
    if 'payment_proof' in request.files:
        file = request.files['payment_proof']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"payment_{current_user.id}_{uuid.uuid4().hex}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            payment_proof = filename
    
    # Создаем заявку на покупку (пока без автоматического начисления)
    flash(f'Заявка на покупку {amount} токенов отправлена. Ожидайте подтверждения от администратора.', 'success')
    
    return redirect(url_for('profile'))

@app.route('/withdraw_tokens', methods=['POST'])
@login_required
def withdraw_tokens():
    """Вывод токенов"""
    if current_user.banned:
        flash('Ваш аккаунт заблокирован', 'danger')
        return redirect(url_for('profile'))
    
    amount = request.form.get('amount')
    yoomoney_wallet = request.form.get('yoomoney_wallet')
    comment = request.form.get('comment')
    
    if not all([amount, yoomoney_wallet]):
        flash('Заполните все обязательные поля', 'danger')
        return redirect(url_for('profile'))
    
    try:
        amount = float(amount)
        if amount <= 0:
            flash('Количество должно быть больше 0', 'danger')
            return redirect(url_for('profile'))
        if amount > current_user.harvest_tokens:
            flash('Недостаточно токенов', 'danger')
            return redirect(url_for('profile'))
    except ValueError:
        flash('Неверное количество токенов', 'danger')
        return redirect(url_for('profile'))
    
    # Создаем заявку на вывод (пока без автоматического списания)
    flash(f'Заявка на вывод {amount} токенов отправлена. Ожидайте подтверждения от администратора.', 'success')
    
    return redirect(url_for('profile'))

# Админ панель
@app.route('/admin')
@login_required
def admin_panel():
    """Админ панель"""
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    chats = Chat.query.all()
    groups = Group.query.all()
    support_tickets = SupportTicket.query.order_by(SupportTicket.created_at.desc()).all()
    
    return render_template('admin.html', 
                         users=users, 
                         chats=chats, 
                         groups=groups, 
                         support_tickets=support_tickets, 
                         NICKNAME_KEY=NICKNAME_KEY)

@app.route('/admin/update_tokens', methods=['POST'])
@login_required
def admin_update_tokens():
    """Обновление токенов пользователя администратором"""
    if not current_user.is_admin:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('index'))
    
    user_id = request.form.get('user_id')
    action = request.form.get('action')
    amount = request.form.get('amount')
    reason = request.form.get('reason')
    
    if not all([user_id, action, amount, reason]):
        flash('Заполните все поля', 'danger')
        return redirect(url_for('admin_panel'))
    
    try:
        user_id = int(user_id)
        amount = float(amount)
    except ValueError:
        flash('Неверные данные', 'danger')
        return redirect(url_for('admin_panel'))
    
    user = User.query.get(user_id)
    if not user:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('admin_panel'))
    
    balance_before = user.harvest_tokens
    
    if action == 'add':
        user.harvest_tokens += amount
    elif action == 'subtract':
        user.harvest_tokens -= amount
        if user.harvest_tokens < 0:
            user.harvest_tokens = 0
    elif action == 'set':
        user.harvest_tokens = amount
    else:
        flash('Неверное действие', 'danger')
        return redirect(url_for('admin_panel'))
    
    # Создаем запись транзакции
    transaction = TokenTransaction(
        user_id=user.id,
        transaction_type='admin_' + action,
        amount=amount if action != 'set' else (user.harvest_tokens - balance_before),
        balance_before=balance_before,
        balance_after=user.harvest_tokens,
        description=f"Админ: {reason}"
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    flash(f'Баланс пользователя {decrypt_nickname(user.nickname_enc)} обновлен', 'success')
    return redirect(url_for('admin_panel'))

# Статические файлы
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Сервис загруженных файлов"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    print("🚀 Запуск упрощенного Flask приложения...")
    print("📱 Локальный доступ: http://0.0.0.0:5000")
    print("💡 WebSocket функции отключены из-за проблем совместимости")
    print("💡 Нажмите Ctrl+C для остановки")
    
    app.run(host='0.0.0.0', port=5000, debug=False) 