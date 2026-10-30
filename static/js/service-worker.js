/* APP_VERSION is prepended by the Django view. Cache contains public assets only. */
const CACHE = `krishi-offline-${APP_VERSION}`;
const CORE = [
  '/static/css/language-fonts.css', '/static/vendor/fonts/notosansolchiki.ttf',
  '/static/vendor/fonts/notosansmeeteimayek.ttf', '/static/vendor/fonts/notonaskharabic.ttf',
  '/static/offline.html', '/static/js/offline-ui.js', '/static/css/app.css',
  '/static/vendor/bootstrap/bootstrap.min.css', '/static/vendor/bootstrap/bootstrap.rtl.min.css',
  '/static/vendor/bootstrap/bootstrap.bundle.min.js', '/static/vendor/bootstrap-icons/bootstrap-icons.min.css',
  '/static/vendor/bootstrap-icons/fonts/bootstrap-icons.woff2',
  '/static/vendor/bootstrap-icons/fonts/bootstrap-icons.woff', '/static/i18n/manifest.json',
];
self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const manifest = await (await fetch('/static/i18n/manifest.json', { cache: 'no-store' })).json();
    const cache = await caches.open(CACHE);
    await cache.addAll([...CORE, ...manifest.languages.map(language => `/static/i18n/${language.code}.json`)]);
    await self.skipWaiting();
  })());
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    await Promise.all((await caches.keys()).filter(key => key.startsWith('krishi-offline-') && key !== CACHE).map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || new URL(event.request.url).origin !== self.location.origin) return;
  if (event.request.mode === 'navigate') {
    event.respondWith(fetch(event.request).catch(() => caches.match('/static/offline.html')));
  } else if (new URL(event.request.url).pathname.startsWith('/static/')) {
    event.respondWith(caches.match(event.request, { ignoreSearch: true }).then(cached => cached || fetch(event.request)));
  }
});
