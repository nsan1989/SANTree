function subscribeToPush(publicKey) {
    if (!('serviceWorker' in navigator)) {
        console.warn('❌ Service workers are not supported.');
        return;
    }

    if (!('PushManager' in window)) {
        console.warn('❌ Push messaging is not supported.');
        return;
    }

    Notification.requestPermission().then(function(permission) {
//        console.log('🔔 Notification permission:', permission);
        if (permission !== 'granted') {
            alert('⚠️ Push notification permission was denied.');
            return;
        }

        navigator.serviceWorker.register('/static/js/serviceworker.js')
            .then(function(registration) {
//                console.log('✅ Service Worker registered:', registration);

                return registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(publicKey)
                });
            })
            .then(function(subscription) {
//                console.log('📨 Push subscription object:', subscription);

                // Send to server
                return fetch('/webpush/save_information/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify(subscription),
                });
            })
            .then(res => {
                if (res.ok) {
                    console.log('✅ Subscription sent to server successfully.');
                } else {
                    console.error('❌ Failed to send subscription:', res.statusText);
                }
            })
            .catch(function(err) {
                console.error('❌ Error during service worker registration or push subscription:', err);
            });
    });
}

// Helper to convert VAPID public key
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = atob(base64);
    return new Uint8Array([...rawData].map(char => char.charCodeAt(0)));
}

// Helper for CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(function(cookie) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
            }
        });
    }
    return cookieValue;
}
