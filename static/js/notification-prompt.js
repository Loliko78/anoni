// Простой запрос разрешений на уведомления
document.addEventListener('DOMContentLoaded', function() {
    console.log('Notification prompt loaded');
    console.log('Notification support:', 'Notification' in window);
    console.log('Current permission:', Notification.permission);
    
    // Показываем баннер с запросом разрешений
    if ('Notification' in window) {
        if (Notification.permission === 'default') {
            console.log('Showing notification banner in 1 second');
            setTimeout(() => {
                showNotificationBanner();
            }, 1000);
        } else if (Notification.permission === 'denied') {
            console.log('Showing help banner for denied permissions');
            setTimeout(() => {
                showHelpBanner();
            }, 1000);
        } else {
            console.log('Notifications already granted');
        }
    } else {
        console.log('Browser does not support notifications');
    }
});

function showNotificationBanner() {
    console.log('Creating notification banner');
    
    const banner = document.createElement('div');
    banner.id = 'notification-banner';
    banner.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #1a1a1a;
        color: #00ff41;
        padding: 15px;
        text-align: center;
        z-index: 10000;
        border-bottom: 1px solid #00ff41;
        font-family: 'Courier New', monospace;
        box-shadow: 0 2px 10px rgba(0,0,0,0.5);
    `;
    
    banner.innerHTML = `
        <div style="max-width: 600px; margin: 0 auto;">
            🔔 Разрешите уведомления, чтобы получать сообщения даже когда сайт закрыт
            <button onclick="requestNotificationPermission()" style="margin-left: 15px; background: #00ff41; color: black; border: none; padding: 8px 15px; border-radius: 3px; cursor: pointer;">
                Разрешить
            </button>
            <button onclick="this.parentElement.parentElement.remove()" style="margin-left: 10px; background: transparent; color: #00ff41; border: 1px solid #00ff41; padding: 8px 15px; border-radius: 3px; cursor: pointer;">
                Позже
            </button>
        </div>
    `;
    
    document.body.appendChild(banner);
    console.log('Banner added to page');
    
    // Проверяем, что баннер добавлен
    const addedBanner = document.getElementById('notification-banner');
    if (addedBanner) {
        console.log('Banner successfully added and visible');
    } else {
        console.error('Banner not found after adding');
    }
}

function requestNotificationPermission() {
    console.log('Requesting notification permission');
    
    Notification.requestPermission().then(function(permission) {
        console.log('Разрешение на уведомления:', permission);
        
        // Убираем баннер
        const banner = document.getElementById('notification-banner');
        if (banner) {
            banner.remove();
            console.log('Banner removed');
        }
        
        if (permission === 'granted') {
            console.log('Permission granted, subscribing to push notifications');
            
            // Подписываемся на push-уведомления
            if (window.pushNotifications) {
                window.pushNotifications.subscribe();
            }
        } else {
            console.log('Permission denied or dismissed');
        }
    }).catch(error => {
        console.error('Error requesting permission:', error);
    });
}

function showHelpBanner() {
    console.log('Creating help banner for denied notifications');
    
    const banner = document.createElement('div');
    banner.id = 'help-banner';
    banner.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #ff4444;
        color: white;
        padding: 15px;
        text-align: center;
        z-index: 10000;
        border-bottom: 1px solid #ff6666;
        font-family: 'Courier New', monospace;
        box-shadow: 0 2px 10px rgba(0,0,0,0.5);
    `;
    
    banner.innerHTML = `
        <div style="max-width: 600px; margin: 0 auto;">
            ⚠️ Уведомления заблокированы! Нажмите на замок в адресной строке и разрешите уведомления
            <button onclick="this.parentElement.parentElement.remove()" style="margin-left: 15px; background: white; color: #ff4444; border: none; padding: 8px 15px; border-radius: 3px; cursor: pointer;">
                Понятно
            </button>
        </div>
    `;
    
    document.body.appendChild(banner);
    console.log('Help banner added to page');
    
    // Автоматически убираем через 10 секунд
    setTimeout(() => {
        if (banner.parentNode) {
            banner.remove();
        }
    }, 10000);
}