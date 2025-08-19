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

// Push Notifications
self.addEventListener('push', function (e) {
    const data = e.data?.json() || { title: 'Default title', body: 'No payload' };

    const options = {
        body: data.body,
        icon: '/static/images/icons/192X192.png',
    };

    e.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});
