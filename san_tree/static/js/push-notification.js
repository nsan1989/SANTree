function subscribeToPush(publicKey) {
    console.log("subscribeToPush called");

    Notification.requestPermission().then(function(permission) {
        if (permission !== "granted") {
            console.error("Notification permission denied");
            return;
        }

        navigator.serviceWorker.register('/static/js/serviceworker.js')
            .then(registration => {
                return navigator.serviceWorker.ready;
            })
            .then(registration => {

                return registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(publicKey)
                });
            })
            .then(subscription => {
                console.log("Subscription created:", subscription);
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
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
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
