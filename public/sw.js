// Minimal service worker: exists mainly to satisfy PWA installability requirements
// (Chrome/Android's automatic install prompt requires one) and to give the app
// something to fall back to if you're genuinely offline. Deliberately does NOT cache
// Supabase API responses — your financial data should always come fresh from the
// network, never from a stale cache.
//
// NETWORK-FIRST: always try the network first for everything. Only serve the cached
// copy if the network request actually fails (i.e. you're offline). This is what
// makes new deploys show up immediately instead of needing a manual refresh -- a
// cache-first strategy would keep serving the page shell from the very first visit
// forever, since this file's own bytes rarely change and browsers only re-check a
// service worker for updates when its file content changes.

const CACHE_NAME = 'crs-accounting-shell-v2'
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

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Keep the offline fallback copy up to date with whatever we just fetched.
        const copy = response.clone()
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy)).catch(() => {})
        return response
      })
      .catch(() => caches.match(event.request))
  )
})
