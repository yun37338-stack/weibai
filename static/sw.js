// 味白 Service Worker — PWA 离线缓存
const CACHE = 'weibai-v2';

// 安装时缓存核心静态资源
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache =>
      cache.addAll([
        '/',
        '/static/manifest.json',
      ])
    )
  );
  self.skipWaiting();
});

// 激活时清理旧缓存
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// 网络优先策略：能上网就用最新数据，离线用缓存兜底
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // API 请求：网络优先，离线返回提示
  if (url.pathname.startsWith('/api/')) {
    e.respondWith(
      fetch(e.request).catch(() =>
        new Response(JSON.stringify({ offline: true, message: '当前离线，请联网后刷新' }),
          { headers: { 'Content-Type': 'application/json' } })
      )
    );
    return;
  }

  // 静态资源：缓存优先
  if (url.pathname.startsWith('/static/')) {
    e.respondWith(
      caches.match(e.request).then(cached =>
        cached || fetch(e.request).then(resp => {
          const clone = resp.clone();
          caches.open(CACHE).then(cache => cache.put(e.request, clone));
          return resp;
        })
      )
    );
    return;
  }

  // 页面请求：网络优先
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
