// Push уведомления для веб-приложения
class PushNotifications {
    constructor() {
        this.registration = null;
        this.init();
        this.setupSocketListener();
    }

    async init() {
        console.log('[PUSH] Инициализация системы уведомлений');
        
        // Проверяем поддержку уведомлений
        if (!('Notification' in window)) {
            console.log('[PUSH] Браузер не поддерживает уведомления');
            return;
        }
        
        console.log('[PUSH] Текущее разрешение:', Notification.permission);
        
        // Запрашиваем разрешение на уведомления
        await this.requestPermission();
        
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            try {
                this.registration = await navigator.serviceWorker.register('/static/js/sw.js');
                console.log('[PUSH] Service Worker зарегистрирован');
            } catch (error) {
                console.error('[PUSH] Ошибка регистрации Service Worker:', error);
            }
        }
    }

    async requestPermission() {
        if (Notification.permission === 'granted') {
            console.log('[PUSH] Разрешение уже предоставлено');
            return true;
        }
        
        if (Notification.permission === 'denied') {
            console.log('[PUSH] Разрешение отклонено пользователем');
            return false;
        }
        
        if (Notification.permission === 'default') {
            console.log('[PUSH] Запрашиваем разрешение...');
            try {
                const permission = await Notification.requestPermission();
                console.log('[PUSH] Получено разрешение:', permission);
                return permission === 'granted';
            } catch (error) {
                console.error('[PUSH] Ошибка запроса разрешения:', error);
                return false;
            }
        }
        
        return false;
    }

    setupSocketListener() {
        // Слушаем уведомления через SocketIO
        if (typeof socket !== 'undefined') {
            socket.on('browser_notification', (data) => {
                console.log('[PUSH] Получено уведомление через SocketIO:', data);
                this.showNotification(data.title, data.body, data.url);
            });
        } else {
            console.log('[PUSH] SocketIO не найден, ждем...');
            // Пробуем подключиться позже
            setTimeout(() => {
                if (typeof socket !== 'undefined') {
                    socket.on('browser_notification', (data) => {
                        console.log('[PUSH] Получено уведомление через SocketIO (отложенное):', data);
                        this.showNotification(data.title, data.body, data.url);
                    });
                }
            }, 2000);
        }
    }

    showNotification(title, body, url) {
        console.log('[PUSH] Попытка показать уведомление:', { title, body, url });
        
        if (Notification.permission !== 'granted') {
            console.log('[PUSH] Нет разрешения на уведомления');
            return;
        }
        
        try {
            const notification = new Notification(title, {
                body: body,
                icon: '/static/favicon.ico',
                badge: '/static/favicon.ico',
                tag: 'harvest-message-' + Date.now(),
                requireInteraction: false,
                silent: false,
                timestamp: Date.now()
            });
            
            console.log('[PUSH] Уведомление создано:', notification);

            notification.onclick = function() {
                console.log('[PUSH] Клик по уведомлению');
                window.focus();
                if (url && url !== '/') {
                    window.location.href = url;
                }
                notification.close();
            };
            
            notification.onshow = function() {
                console.log('[PUSH] Уведомление показано');
            };
            
            notification.onerror = function(error) {
                console.error('[PUSH] Ошибка уведомления:', error);
            };

            // Автоматически закрываем через 8 секунд
            setTimeout(() => {
                notification.close();
                console.log('[PUSH] Уведомление автоматически закрыто');
            }, 8000);
            
        } catch (error) {
            console.error('[PUSH] Ошибка создания уведомления:', error);
        }
    }
    


    async subscribe() {
        const hasPermission = await this.requestPermission();
        if (!hasPermission) {
            console.log('[PUSH] Нет разрешения для подписки');
            return false;
        }

        if (!this.registration) {
            console.log('[PUSH] Service Worker не зарегистрирован');
            return false;
        }
        
        try {
            const subscription = await this.registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array('BEl62iUYgUivxIkv69yViEuiBIa40HI0DLLuxazjqAKVXTJtkTXaXWKB4qDjSRUt8BlYDBFas2VPKKkOBXcQVxs')
            });
            
            console.log('[PUSH] Подписка создана:', subscription);
            
            // Отправляем подписку на сервер
            const response = await fetch('/api/push/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(subscription)
            });
            
            const result = await response.json();
            console.log('[PUSH] Ответ сервера:', result);
            
            return result.success;
        } catch (error) {
            console.error('[PUSH] Ошибка подписки:', error);
            return false;
        }
    }

    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }
}

// Глобальная переменная для доступа к системе уведомлений
let pushNotifications;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('[PUSH] Инициализация при загрузке страницы');
    pushNotifications = new PushNotifications();
    
    // Автоматически запрашиваем разрешение при первом посещении
    setTimeout(() => {
        if (pushNotifications.subscribe) {
            pushNotifications.subscribe();
        }
    }, 2000);
    

});