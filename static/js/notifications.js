// Запрос разрешения на уведомления
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

// Показать браузерное уведомление
function showNotification(title, body, chatId) {
    if ('Notification' in window && Notification.permission === 'granted') {
        const notification = new Notification(title, {
            body: body,
            icon: '/static/favicon.ico',
            badge: '/static/favicon.ico',
            tag: `chat_${chatId}`,
            requireInteraction: false
        });
        
        notification.onclick = function() {
            window.focus();
            window.location.href = `/chat/${chatId}`;
            notification.close();
        };
        
        // Автозакрытие через 5 секунд
        setTimeout(() => notification.close(), 5000);
    }
}

// Обновление счетчиков непрочитанных
function updateUnreadCount(chatId, count) {
    const badge = document.querySelector(`[data-chat-id="${chatId}"] .unread-badge`);
    if (badge) {
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Обновление онлайн статуса
function updateOnlineStatus(userId, isOnline) {
    const statusDot = document.querySelector(`[data-user-id="${userId}"] .status-dot`);
    if (statusDot) {
        statusDot.className = `status-dot ${isOnline ? 'online' : 'offline'}`;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    requestNotificationPermission();
    
    // Подключение к SocketIO
    if (typeof socket !== 'undefined') {
        // Обработка уведомлений
        socket.on('notification', function(data) {
            showNotification(data.title, data.body, data.chat_id);
            
            // Обновляем счетчик непрочитанных
            const currentCount = parseInt(document.querySelector(`[data-chat-id="${data.chat_id}"] .unread-badge`)?.textContent || '0');
            updateUnreadCount(data.chat_id, currentCount + 1);
        });
        
        // Обработка онлайн статусов
        socket.on('user_online', function(data) {
            updateOnlineStatus(data.user_id, true);
        });
        
        socket.on('user_offline', function(data) {
            updateOnlineStatus(data.user_id, false);
        });
    }
});