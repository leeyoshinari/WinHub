const CACHE_NAME = 'winhub';
const staticFileExtensions = ['/img/', '/css/', '/js/', '.html', '.json', '/module/', 'head.js', 'sw.js'];
const excludeFiles = ['/background.jpg', '/avatar.jpg'];
const regex = new RegExp(`(${staticFileExtensions.join('|').replace(/\./g, '\\.')})`, 'i');
const excludeRegex = new RegExp(`(${excludeFiles.join('|').replace(/\./g, '\\.')})`, 'i');
const urlsToCache = [''];

// 安装事件
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

// 激活事件
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});

// Fetch事件
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(event.request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && regex.test(networkResponse.url) && !excludeRegex.test(networkResponse.url) && networkResponse.type === 'basic') {
          const clonedResponse = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, clonedResponse);
          });
        }
        return networkResponse;
      });
    })
  );
});
