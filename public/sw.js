// Minimal service worker: exists mainly to satisfy PWA installability requirements
// (Chrome/Android's automatic install prompt requires one) and to speed up repeat loads
// of the app shell. Deliberately does NOT cache Supabase API responses — your financial
// data should always come fresh from the network, never from a stale cache.

const CACHE_NAME = 'crs-accounting-shell-v1'
const APP_SHELL = [
  '/CRSAccounting/',
  '/CRSAccounting/index.html',
  '/CRSAccounting/manifest.webmanifest',
  '/CRSAccounting/icon-192.png',
  '/CRSAccounting/icon-512.png',
]

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)).catch(() => {})
  )
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  )
  self.clients.claim()
})

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url)

  // Never intercept Supabase API calls or non-GET requests — always go to network.
  if (event.request.method !== 'GET' || url.hostname.includes('supabase.co')) {
    return
  }

  // App shell / static assets: try cache first, fall back to network.
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  )
})
