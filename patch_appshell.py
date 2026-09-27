import re

with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

robust_detect = """const isIOS = typeof window !== 'undefined' && (
  /iPad|iPhone|iPod/.test(navigator.userAgent) ||
  (navigator.userAgent.includes("Mac") && "ontouchend" in document)
);
const isPWA = typeof window !== 'undefined' && (window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches);
const safeAreaStyle = { height: (isIOS && isPWA) ? 'max(env(safe-area-inset-top), 24px)' : 'env(safe-area-inset-top)' };
"""

# Replace the old logic
content = content.replace(
    "const isIOSPWA = typeof window !== 'undefined' && /iPad|iPhone|iPod/.test(navigator.userAgent) && (window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches)\nconst safeAreaStyle = { height: isIOSPWA ? 'max(env(safe-area-inset-top), 24px)' : 'env(safe-area-inset-top)' }",
    robust_detect
)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
