const CACHE = "daymark-static-v2";
const SHELL = ["./", "./index.html", "./manifest.webmanifest"];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key)))));
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin) return;

  event.respondWith(fetch(request).then(response => {
    if (response.ok && (url.pathname.endsWith("/index.html") || url.pathname.endsWith("/manifest.webmanifest") || url.pathname.endsWith("/"))) {
      const copy = response.clone();
      caches.open(CACHE).then(cache => cache.put(request, copy)).catch(() => {});
    }
    return response;
  }).catch(async () => (await caches.match(request)) || caches.match("./index.html")));
});
