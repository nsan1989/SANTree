// serviceworker.js

// Install event
self.addEventListener('install', event => {
    console.log('[Service Worker] Installed');
    // Optionally skip waiting
    self.skipWaiting();
});

// Activate event
self.addEventListener('activate', event => {
    console.log('[Service Worker] Activated');
    // Optionally take control of clients immediately
    self.clients.claim();
});

// Fetch event
self.addEventListener('fetch', event => {
    console.log('[Service Worker] Fetching:', event.request.url);
    // Optionally respond with a cached version or fetch from network
    event.respondWith(fetch(event.request));
});

// Push event - receives notification payload from server
self.addEventListener('push', function (e) {
    console.log('[Service Worker] Push received');

    let data = {};
    try {
        data = e.data.json();
    } catch (err) {
        data = { title: "Notification", body: e.data.text() };
    }

    const options = {
        body: data.body,
        icon: '/static/images/icons/192X192.png',
        badge: '/static/images/icons/192X192.png', // optional: smaller monochrome icon
        data: {
            url: data.url || '/',   // navigate when clicked
            extra: data.extra || {} // you can send additional info
        }
    };

    e.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Handle notification click (open dashboard, complaint, or task page)
self.addEventListener('notificationclick', function (event) {
    event.notification.close();
    const targetUrl = event.notification.data.url || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
            for (let client of windowClients) {
                if (client.url.includes(targetUrl) && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});
