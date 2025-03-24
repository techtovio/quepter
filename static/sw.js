// static/js/sw.js
const CACHE_NAME = 'youth-empowerment-v1';
const ASSETS = [
  '/',  // Home URL (handled by Django view)
  {% static 'css/main.css' %},
  {% static 'js/app.js' %},
  {% static 'images/logo.png' %},
  '/projects/',  // Django URL pattern
  '/clubs/'      // Django URL pattern
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});