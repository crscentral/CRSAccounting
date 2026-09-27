with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

definition = """const isIOSDevice = typeof window !== 'undefined' && (
  /iPad|iPhone|iPod/.test(navigator.userAgent) ||
  (navigator.userAgent.includes("Mac") && "ontouchend" in document)
);
const isPWAMode = typeof window !== 'undefined' && (window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches);
const safeAreaStyle = { height: (isIOSDevice && isPWAMode) ? 'max(env(safe-area-inset-top), 24px)' : 'env(safe-area-inset-top)' };
"""

# Insert right after the imports (look for the lucide-react import end)
content = content.replace(
    "import logo from '../assets/crs-logo.png'",
    "import logo from '../assets/crs-logo.png'\n\n" + definition
)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
