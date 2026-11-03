import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Bulletproof iOS PWA detection
if (typeof window !== 'undefined') {
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.userAgent.includes("Mac") && "ontouchend" in document);
  const isIPad = /iPad/.test(navigator.userAgent) || (navigator.userAgent.includes("Mac") && "ontouchend" in document);
  const isStandalone = window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches;
  
  if (isIOS && isStandalone) {
    document.documentElement.classList.add('ios-standalone');
  }
  if (isIPad && isStandalone) {
    document.documentElement.classList.add('ipad-standalone');
  }

  // Handle chunk loading errors when a new deployment invalidates old asset hashes
  window.addEventListener('vite:preloadError', async (event) => {
    console.warn('Vite preloadError detected (new deployment). Handling reload safely...', event);
    event.preventDefault();

    const RETRY_KEY = 'crs_vite_preload_retry';
    try {
      const lastRetry = sessionStorage.getItem(RETRY_KEY);
      const now = Date.now();
      if (lastRetry && now - parseInt(lastRetry, 10) < 20000) {
        console.error('Repeated Vite preload errors detected within 20s. Halting auto-reload loop.');
        return;
      }
      sessionStorage.setItem(RETRY_KEY, String(now));
    } catch {
      // If sessionStorage is unavailable, do not loop
      return;
    }

    try {
      if ('caches' in window) {
        const keys = await caches.keys();
        await Promise.all(keys.map((k) => caches.delete(k)));
      }
      if ('serviceWorker' in navigator) {
        const registrations = await navigator.serviceWorker.getRegistrations();
        await Promise.all(registrations.map((r) => r.unregister()));
      }
    } catch (e) {
      console.warn('Failed to clear caches/serviceWorker on preload error:', e);
    }

    window.location.reload();
  });
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// Register the service worker for PWA installability ("Add to Home Screen" / "Install app").
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').then((registration) => {
      // Check for worker updates
      registration.onupdatefound = () => {
        const installingWorker = registration.installing;
        if (installingWorker) {
          installingWorker.onstatechange = () => {
            if (installingWorker.state === 'installed' && navigator.serviceWorker.controller) {
              console.log('New service worker update available.');
            }
          };
        }
      };
    }).catch((err) => {
      console.warn('Service worker registration failed:', err)
    })
  })
}
