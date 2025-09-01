// Service Worker для push-уведомлений
self.addEventListener('push', function(event) {
    if (event.data) {
        const data = event.data.json();
        
        const options = {
            body: data.body,
            icon: data.icon || '/static/harvest_darkweb.svg',
            badge: data.badge || '/static/harvest_darkweb.svg',
            vibrate: [200, 100, 200],
            requireInteraction: data.requireInteraction || false,
            tag: data.tag || 'harvest-message',
            data: {
                url: data.url || '/'
            },
            actions: [
                {
                    action: 'open',
                    title: 'Открыть'
                },
                {
                    action: 'close',
                    title: 'Закрыть'
                }
            ]
        };

        event.waitUntil(
            self.registration.showNotification(data.title || 'Harvest', options)
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