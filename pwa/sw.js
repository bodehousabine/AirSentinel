const CACHE_NAME = 'airsentinel-pwa-v8';
const ASSETS = [
  './index.html',
  './manifest.json',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
  'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&family=DM+Mono:ital@0;1&display=swap'
];

self.addEventListener('install', (e) => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(keyList.map((key) => {
        if (key !== CACHE_NAME) {
          return caches.delete(key);
        }
      }));
    })
  );
});

self.addEventListener('fetch', (e) => {
  // Ignorer les appels API pour tjrs avoir de la donnée fraiche
  if (e.request.url.includes('localhost:') || e.request.url.includes('127.0.0.1')) {
    return;
  }
  
  e.respondWith(
    caches.match(e.request).then((res) => {
      // Retourne le cache s'il est dispo, sinon on fetch sur le web
      return res || fetch(e.request);
    })
  );
});
