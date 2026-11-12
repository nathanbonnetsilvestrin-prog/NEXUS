
const CACHE_NAME = "nexus-v4";

const FILES = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon-192.png",
  "./icon-512.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(FILES))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(key => key.startsWith("nexus-") && key !== CACHE_NAME)
          .map(key => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const request = event.request;

  if (request.method !== "GET") return;

  const url = new URL(request.url);

  if (url.origin !== self.location.origin) return;

  const isNews = url.pathname.endsWith("/news.json");
  const isHtml = request.mode === "navigate" ||
    url.pathname.endsWith("/index.html");
  const isManifest = url.pathname.endsWith("/manifest.json");

  if (isNews || isHtml || isManifest) {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response && response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then(cache =>
              cache.put(request, copy)
            );
          }
          return response;
        })
        .catch(() => caches.match(request).then(cached => {
          if (cached) return cached;
          if (isHtml) return caches.match("./index.html");

          return new Response("Contenu indisponible hors ligne.", {
            status: 503,
            headers: { "Content-Type": "text/plain; charset=utf-8" }
          });
        }))
    );
    return;
  }

  event.respondWith(
    caches.match(request).then(cached => {
      if (cached) return cached;

      return fetch(request).then(response => {
        if (response && response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(cache =>
            cache.put(request, copy)
          );
        }
        return response;
      });
    })
  );
});

self.addEventListener("push", event => {
  let data = {};

  try {
    data = event.data ? event.data.json() : {};
  } catch (error) {}

  event.waitUntil(
    self.registration.showNotification(
      data.title || "NEXUS Intelligence",
      {
        body: data.body || "Votre journal est prêt.",
        icon: "./icon-192.png",
        badge: "./icon-192.png",
        data: { url: data.url || "./" }
      }
    )
  );
});

self.addEventListener("notificationclick", event => {
  event.notification.close();

  event.waitUntil(
    clients.openWindow(
      new URL(
        event.notification.data.url || "./",
        self.location.origin
      ).href
    )
  );
});
