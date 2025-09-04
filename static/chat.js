// Глобальные переменные
let currentChatId = null;
let currentCallRoom = null;
let isInCall = false;
let callPartner = null;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    initializeSocketIO();
    loadChatList();
});

// Инициализация чата
function initializeChat() {
    // Получаем ID чата из URL
    const pathParts = window.location.pathname.split('/');
    currentChatId = pathParts[pathParts.length - 1];
    
    // Инициализируем форму отправки сообщений
    const messageForm = document.getElementById('messageForm');
    const messageInput = document.getElementById('messageInput');
    
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage();
        });
    }
    
    if (messageInput) {
        messageInput.addEventListener('input', function() {
            autoResizeTextarea(this);
        });
        
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Инициализируем загрузку файлов
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
    
    // Инициализируем панель стикеров
    initializeStickers();
    
    // Загружаем сообщения
    loadMessages();
    
    // Автоскролл к последнему сообщению
    scrollToBottom();
}

// Инициализация Socket.IO
function initializeSocketIO() {
    if (typeof io !== 'undefined') {
        const socket = io();
        
        // Подключение к чату
        socket.emit('join_chat', { chat_id: currentChatId });
        
        // Получение нового сообщения
        socket.on('new_message', function(data) {
            if (data.chat_id == currentChatId) {
                addMessage(data);
                scrollToBottom();
                showNotification('Новое сообщение', 'success');
            }
        });
        
        // Получение голосового сообщения
        socket.on('voice_message_received', function(data) {
            if (data.chat_id == currentChatId) {
                addVoiceMessage(data);
                showNotification('Голосовое сообщение', 'success');
            }
        });
        
        // Входящий звонок
        socket.on('incoming_call', function(data) {
            showIncomingCallModal(data);
        });
        
        // Звонок принят
        socket.on('call_accepted', function(data) {
            handleCallAccepted(data);
        });
        
        // Звонок отклонен
        socket.on('call_rejected', function(data) {
            handleCallRejected(data);
        });
        
        // Звонок завершен
        socket.on('call_ended', function(data) {
            handleCallEnded(data);
        });
        
        // Сообщение во время звонка
        socket.on('call_message', function(data) {
            addCallMessage(data);
        });
    }
}

// Загрузка списка чатов
function loadChatList() {
    fetch('/api/chats')
        .then(response => response.json())
        .then(data => {
            const chatList = document.getElementById('chatList');
            if (chatList && data.chats) {
                chatList.innerHTML = '';
                data.chats.forEach(chat => {
                    const chatItem = createChatItem(chat);
                    chatList.appendChild(chatItem);
                });
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки чатов:', error);
        });
}

// Создание элемента чата
function createChatItem(chat) {
    const div = document.createElement('div');
    div.className = 'chat-item';
    div.onclick = () => window.location.href = `/chat/${chat.id}`;
    
    div.innerHTML = `
        <div class="chat-avatar">
            <div class="default-avatar">
                <span>${chat.other_user.nickname_enc[0].toUpperCase()}</span>
            </div>
        </div>
        <div class="chat-info">
            <div class="chat-name">${chat.other_user.nickname_enc}</div>
            <div class="chat-preview">${chat.last_message || 'Нет сообщений'}</div>
        </div>
    `;
    
    return div;
}

// Загрузка сообщений
function loadMessages() {
    if (!currentChatId) return;
    
    fetch(`/chat/${currentChatId}/messages`)
        .then(response => response.json())
        .then(data => {
            const messagesContainer = document.getElementById('chatMessages');
            if (messagesContainer && data.messages) {
                messagesContainer.innerHTML = '';
                data.messages.forEach(message => {
                    addMessage(message, false);
                });
                scrollToBottom();
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки сообщений:', error);
        });
}

// Отправка сообщения
function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const content = messageInput.value.trim();
    
    if (!content) return;
    
    if (typeof io !== 'undefined') {
        const socket = io();
        socket.emit('send_message', {
            chat_id: currentChatId,
            content: content
        });
    }
    
    messageInput.value = '';
    autoResizeTextarea(messageInput);
}

// Отправка стикера
function sendSticker(emoji) {
    if (typeof io !== 'undefined') {
        const socket = io();
        socket.emit('send_message', {
            chat_id: currentChatId,
            content: emoji,
            is_sticker: true
        });
    }
    
    toggleStickers();
}

// Добавление сообщения в чат
function addMessage(messageData, animate = true) {
    const messagesContainer = document.getElementById('chatMessages');
    if (!messagesContainer) return;
    
    // Проверяем тип сообщения
    if (messageData.type === 'voice') {
        addVoiceMessage(messageData, animate);
        return;
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${messageData.sender_id == currentUserId ? 'sent' : 'received'}`;
    messageDiv.dataset.messageId = messageData.id;
    
    if (animate) {
        messageDiv.style.animation = 'messageSlideIn 0.3s ease';
    }
    
    const isOwnMessage = messageData.sender_id == currentUserId;
    
    let messageHTML = '';
    
    if (!isOwnMessage) {
        messageHTML += `
            <div class="message-avatar">
                <div class="mini-avatar">
                    <span>${messageData.sender_nickname ? messageData.sender_nickname[0].toUpperCase() : 'U'}</span>
                </div>
            </div>
        `;
    }
    
    messageHTML += `
        <div class="message-content">
    `;
    
    if (messageData.file_id) {
        messageHTML += `
            <div class="message-file">
                <div class="file-preview">
                    ${messageData.file_type && messageData.file_type.startsWith('image/') 
                        ? `<img src="/file/${messageData.file_id}" alt="Изображение" class="file-image">`
                        : '<div class="file-icon">📎</div>'
                    }
                </div>
                <div class="file-info">
                    <div class="file-name">${messageData.file_name || 'Файл'}</div>
                    <a href="/file/${messageData.file_id}" class="file-download" download>Скачать</a>
                </div>
            </div>
        `;
    }
    
    if (messageData.content) {
        messageHTML += `
            <div class="message-text">
                ${messageData.content}
                ${messageData.is_edited ? '<span class="edited-mark">(ред.)</span>' : ''}
            </div>
        `;
    }
    
    messageHTML += `
            <div class="message-time">${formatTime(messageData.timestamp)}</div>
        </div>
    `;
    
    if (isOwnMessage) {
        messageHTML += `
            <div class="message-actions">
                <button class="btn btn-edit" onclick="editMessage(${messageData.id})" title="Редактировать">✏️</button>
                <button class="btn btn-delete" onclick="deleteMessage(${messageData.id})" title="Удалить">🗑️</button>
            </div>
        `;
    }
    
    messageDiv.innerHTML = messageHTML;
    messagesContainer.appendChild(messageDiv);
}

// Удаление сообщения
function deleteMessage(messageId) {
    if (!confirm('Удалить это сообщение?')) return;
    
    fetch(`/message/delete/${messageId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
            if (messageElement) {
                messageElement.remove();
                showNotification('Сообщение удалено', 'success');
            }
        }
    })
    .catch(error => {
        console.error('Ошибка удаления сообщения:', error);
        showNotification('Ошибка удаления сообщения', 'error');
    });
}

// Редактирование сообщения
function editMessage(messageId) {
    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
    if (!messageElement) return;
    
    const messageText = messageElement.querySelector('.message-text');
    const currentText = messageText.textContent.replace('(ред.)', '').trim();
    
    const newText = prompt('Редактировать сообщение:', currentText);
    if (newText === null || newText.trim() === '') return;
    
    fetch(`/message/edit/${messageId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: newText.trim() })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            messageText.innerHTML = `${newText.trim()} <span class="edited-mark">(ред.)</span>`;
            showNotification('Сообщение отредактировано', 'success');
        }
    })
    .catch(error => {
        console.error('Ошибка редактирования сообщения:', error);
        showNotification('Ошибка редактирования сообщения', 'error');
    });
}

// Обработка загрузки файла
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/upload_file', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Отправляем сообщение с файлом
            if (typeof io !== 'undefined') {
                const socket = io();
                socket.emit('send_message', {
                    chat_id: currentChatId,
                    file_id: data.file_id,
                    file_name: data.file_name,
                    file_type: data.file_type
                });
            }
            showNotification('Файл загружен', 'success');
        } else {
            showNotification('Ошибка загрузки файла', 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка загрузки файла:', error);
        showNotification('Ошибка загрузки файла', 'error');
    });
    
    // Очищаем input
    event.target.value = '';
}

// Инициализация стикеров
function initializeStickers() {
    const stickerButtons = document.querySelectorAll('.sticker');
    stickerButtons.forEach(button => {
        button.addEventListener('click', function() {
            const emoji = this.textContent;
            sendSticker(emoji);
        });
    });
}

// Переключение панели стикеров
function toggleStickers() {
    const stickersPanel = document.getElementById('stickersPanel');
    if (stickersPanel) {
        stickersPanel.style.display = stickersPanel.style.display === 'none' ? 'block' : 'none';
    }
}

// Автоматическое изменение размера textarea
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
}

// Прокрутка к последнему сообщению
function scrollToBottom() {
    const messagesContainer = document.getElementById('chatMessages');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Форматирование времени
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ru-RU', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// Переключение боковой панели
function toggleSidebar() {
    const sidebar = document.querySelector('.chat-sidebar');
    if (sidebar) {
        sidebar.classList.toggle('show');
    }
}

// Переключение меню чата
function toggleChatMenu() {
    const dropdown = document.getElementById('chatMenuDropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

// Закрытие всех выпадающих меню при клике вне их
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('chatMenuDropdown');
    if (dropdown && !dropdown.contains(event.target) && !event.target.matches('.btn-menu')) {
        dropdown.classList.remove('show');
    }
    
    const stickersPanel = document.getElementById('stickersPanel');
    if (stickersPanel && !stickersPanel.contains(event.target) && !event.target.matches('.btn-sticker')) {
        stickersPanel.style.display = 'none';
    }
});

// Функции меню чата
function syncKeys() {
    if (!currentChatId) return;
    
    fetch(`/chat/${currentChatId}/sync_keys`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Ключи синхронизированы', 'success');
        } else {
            showNotification('Ошибка синхронизации ключей', 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка синхронизации ключей:', error);
        showNotification('Ошибка синхронизации ключей', 'error');
    });
    
    toggleChatMenu();
}

function shareContact() {
    if (!currentChatId) return;
    
    fetch(`/chat/${currentChatId}/share_contact`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Контакт поделен', 'success');
        } else {
            showNotification('Ошибка при делении контакта', 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка при делении контакта:', error);
        showNotification('Ошибка при делении контакта', 'error');
    });
    
    toggleChatMenu();
}

function clearHistory() {
    if (!currentChatId || !confirm('Очистить всю историю чата?')) return;
    
    fetch(`/chat/${currentChatId}/clear_history`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const messagesContainer = document.getElementById('chatMessages');
            if (messagesContainer) {
                messagesContainer.innerHTML = '';
            }
            showNotification('История очищена', 'success');
        } else {
            showNotification('Ошибка очистки истории', 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка очистки истории:', error);
        showNotification('Ошибка очистки истории', 'error');
    });
    
    toggleChatMenu();
}

function blockUser() {
    if (!currentChatId || !confirm('Заблокировать этого пользователя?')) return;
    
    fetch(`/chat/${currentChatId}/block_user`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Пользователь заблокирован', 'success');
            setTimeout(() => {
                window.location.href = '/chats';
            }, 1000);
        } else {
            showNotification('Ошибка блокировки пользователя', 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка блокировки пользователя:', error);
        showNotification('Ошибка блокировки пользователя', 'error');
    });
    
    toggleChatMenu();
}

// Функции звонков
function startCall() {
    if (!currentChatId) return;
    
    // Получаем ID другого пользователя из URL или данных чата
    const pathParts = window.location.pathname.split('/');
    const chatId = pathParts[pathParts.length - 1];
    
    // Здесь нужно получить ID другого пользователя из данных чата
    // Пока используем заглушку
    const targetUserId = getOtherUserIdFromChat(chatId);
    
    if (targetUserId && typeof io !== 'undefined') {
        const socket = io();
        socket.emit('call_start', {
            target_user_id: targetUserId
        });
        
        showNotification('Звонок начат...', 'info');
    }
}

function acceptCall() {
    const modal = document.getElementById('incomingCallModal');
    const callerId = modal.dataset.callerId;
    const callRoom = modal.dataset.callRoom;
    
    if (typeof io !== 'undefined') {
        const socket = io();
        socket.emit('call_accept', {
            caller_id: callerId,
            call_room: callRoom
        });
        
        isInCall = true;
        currentCallRoom = callRoom;
        callPartner = callerId;
        
        showCallInterface();
    }
    
    hideIncomingCallModal();
}

function rejectCall() {
    const modal = document.getElementById('incomingCallModal');
    const callerId = modal.dataset.callerId;
    const callRoom = modal.dataset.callRoom;
    
    if (typeof io !== 'undefined') {
        const socket = io();
        socket.emit('call_reject', {
            caller_id: callerId,
            call_room: callRoom
        });
    }
    
    hideIncomingCallModal();
}

function endCall() {
    if (typeof io !== 'undefined') {
        const socket = io();
        socket.emit('call_end', {
            call_room: currentCallRoom,
            other_user_id: callPartner
        });
    }
    
    isInCall = false;
    currentCallRoom = null;
    callPartner = null;
    hideCallInterface();
}

function sendCallMessage() {
    const callMessageInput = document.getElementById('callMessageInput');
    const message = callMessageInput.value.trim();
    
    if (!message || !currentCallRoom) return;
    
    if (typeof io !== 'undefined') {
        const socket = io();
        socket.emit('call_message', {
            call_room: currentCallRoom,
            message: message
        });
        
        addCallMessage({
            sender_id: currentUserId,
            sender_nickname: currentUserNickname,
            message: message
        });
    }
    
    callMessageInput.value = '';
}

// Обработчики событий звонков
function handleCallAccepted(data) {
    isInCall = true;
    callPartner = data.accepter_id;
    showCallInterface();
    showNotification('Звонок принят', 'success');
}

function handleCallRejected(data) {
    showNotification('Звонок отклонен', 'warning');
}

function handleCallEnded(data) {
    isInCall = false;
    currentCallRoom = null;
    callPartner = null;
    hideCallInterface();
    showNotification('Звонок завершен', 'info');
}

function addCallMessage(data) {
    const callMessagesContainer = document.getElementById('callMessages');
    if (!callMessagesContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `call-message ${data.sender_id == currentUserId ? 'own' : 'other'}`;
    messageDiv.innerHTML = `
        <span class="call-message-sender">${data.sender_nickname}:</span>
        <span class="call-message-text">${data.message}</span>
    `;
    
    callMessagesContainer.appendChild(messageDiv);
    callMessagesContainer.scrollTop = callMessagesContainer.scrollHeight;
}

// Показ модального окна входящего звонка
function showIncomingCallModal(data) {
    const modal = document.getElementById('incomingCallModal');
    const callerName = document.getElementById('callerName');
    
    if (modal && callerName) {
        modal.dataset.callerId = data.caller_id;
        modal.dataset.callRoom = data.call_room;
        callerName.textContent = `${data.caller_nickname} звонит вам`;
        modal.classList.add('show');
    }
}

function hideIncomingCallModal() {
    const modal = document.getElementById('incomingCallModal');
    if (modal) {
        modal.classList.remove('show');
    }
}

// Показ интерфейса звонка
function showCallInterface() {
    const callInterface = document.getElementById('callInterface');
    if (callInterface) {
        callInterface.style.display = 'flex';
    }
}

function hideCallInterface() {
    const callInterface = document.getElementById('callInterface');
    if (callInterface) {
        callInterface.style.display = 'none';
    }
}

// Уведомления
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Автоматическое удаление через 3 секунды
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Вспомогательные функции
function getOtherUserIdFromChat(chatId) {
    // Здесь должна быть логика получения ID другого пользователя
    // Пока возвращаем заглушку
    return null;
}

// Получение текущего пользователя из данных страницы
const currentUserId = document.body.dataset.userId;
const currentUserNickname = document.body.dataset.userNickname; 