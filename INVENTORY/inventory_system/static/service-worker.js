self.addEventListener('install', event => {
  console.log('Service worker installed');
  event.waitUntil(
    caches.open('nfc-cache').then(cache => {
      return cache.addAll([
        '/',
        '/static/manifest.json'
      ]);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
