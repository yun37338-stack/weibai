// 个人工作台 Service Worker - 离线缓存
const CACHE = 'workstation-v1';

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll([
      '/',
      '/static/manifest.json',
      '/api/home/summary',
    ]))
  );
  self.skipWaiting();
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
