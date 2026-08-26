import { useEffect, useState } from 'react'

/**
 * Captures Chrome/Android's `beforeinstallprompt` event so we can show our own
 * "Install App" button instead of relying on people finding the browser's menu.
 * iOS Safari doesn't support this API at all -- there, "Add to Home Screen" only
 * exists via the manual Share sheet, which we point people to instead.
 */
export function useInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState(null)
  const [installed, setInstalled] = useState(false)

  useEffect(() => {
    function onBeforeInstallPrompt(e) {
      e.preventDefault()
      setDeferredPrompt(e)
    }
    function onInstalled() {
      setInstalled(true)
      setDeferredPrompt(null)
    }
    window.addEventListener('beforeinstallprompt', onBeforeInstallPrompt)
    window.addEventListener('appinstalled', onInstalled)
    return () => {
      window.removeEventListener('beforeinstallprompt', onBeforeInstallPrompt)
      window.removeEventListener('appinstalled', onInstalled)
    }
  }, [])

  const isStandalone =
    window.matchMedia?.('(display-mode: standalone)').matches || window.navigator.standalone === true

  async function promptInstall() {
    if (!deferredPrompt) return
    deferredPrompt.prompt()
    await deferredPrompt.userChoice
    setDeferredPrompt(null)
  }

  return {
    canInstall: !!deferredPrompt && !installed && !isStandalone,
    isStandalone,
    promptInstall,
  }
}
