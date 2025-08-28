// Service Worker для push-уведомлений
self.addEventListener('push', function(event) {
    if (event.data) {
        const data = event.data.json();
        
        const options = {
            body: data.body,
            icon: '/static/favicon.ico',
            badge: '/static/favicon.ico',
            vibrate: [200, 100, 200],
            data: {
                chat_id: data.chat_id,
                url: data.url || '/'
            },
            actions: [
                {
                    action: 'open',
                    title: 'Открыть чат'
                }
            ]
        };

        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();

    if (event.action === 'open' || !event.action) {
        const url = event.notification.data.url || '/';
        
        event.waitUntil(
            clients.matchAll().then(function(clientList) {
                for (let i = 0; i < clientList.length; i++) {
                    const client = clientList[i];
                    if (client.url === url && 'focus' in client) {
                        return client.focus();
                    }
                }
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
        );
    }
});