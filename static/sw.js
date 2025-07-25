// Simple service worker for basic offline functionality
const CACHE_NAME = "demerzel-v1";
const STATIC_ASSETS = [
  "/",
  "/static/index.html",
  "/static/dune/index.html",
  "/static/the-one-ring/index.html",
  "/static/call-of-cthulhu/index.html",
  "/static/master-template/index.html",
];

// Install event - cache static assets
self.addEventListener("install", function (event) {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then(function (cache) {
        return cache.addAll(STATIC_ASSETS);
      })
      .catch(function (error) {
        console.log("Service Worker: Cache failed:", error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (cacheNames) {
      return Promise.all(
        cacheNames.map(function (cacheName) {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener("fetch", function (event) {
  // Only handle GET requests
  if (event.request.method !== "GET") {
    return;
  }

  event.respondWith(
    caches.match(event.request).then(function (response) {
      // Return cached version if available
      if (response) {
        return response;
      }

      // Otherwise, fetch from network
      return fetch(event.request)
        .then(function (response) {
          // Check if valid response
          if (
            !response ||
            response.status !== 200 ||
            response.type !== "basic"
          ) {
            return response;
          }

          // Clone the response for caching
          var responseToCache = response.clone();

          // Cache the fetched response
          caches.open(CACHE_NAME).then(function (cache) {
            cache.put(event.request, responseToCache);
          });

          return response;
        })
        .catch(function (error) {
          // Return offline fallback for main pages
          if (
            event.request.url.endsWith("/") ||
            event.request.url.includes("/dune") ||
            event.request.url.includes("/the-one-ring") ||
            event.request.url.includes("/call-of-cthulhu") ||
            event.request.url.includes("/master-template")
          ) {
            return new Response(
              "<!DOCTYPE html><html><head><title>Offline</title></head><body>" +
                "<h1>You are offline</h1>" +
                "<p>Please check your internet connection and try again.</p>" +
                '<p><a href="/">Return to main page</a></p>' +
                "</body></html>",
              {
                headers: { "Content-Type": "text/html" },
              }
            );
          }

          throw error;
        });
    })
  );
});
