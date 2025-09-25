
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}


function subscribeToPush(publicKey) {
    console.log(Notification.permission); 
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
