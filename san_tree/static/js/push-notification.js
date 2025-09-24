function subscribeToPush(publicKey) {
    Notification.requestPermission().then(function(permission) {
        if (permission !== "granted") {
            console.error("Notification permission denied");
            return;
        }

        navigator.serviceWorker.register('/static/js/serviceworker.js')
            .then(function(registration) {
                return registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(publicKey)
                });
            })
            .then(function(subscription) {
                console.log("Subscription created:", subscription);
                return fetch('/webpush/save_information/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify(subscription),
                });
            })
            .then(function(res) {
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
