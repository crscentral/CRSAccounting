import re

with open('src/index.css', 'r') as f:
    content = f.read()

content = content.replace(
    "@media (display-mode: standalone) {\n    .ios-safe-area-spacer {\n      /* Force a minimum of 24px for iOS devices, because iPads report 0px for safe-area-inset-top but still render the status bar overlapping the app */\n      height: max(env(safe-area-inset-top), 24px) !important;\n    }\n  }",
    ""
)
content = content.replace("@supports (-webkit-touch-callout: none) {", "")
content = content.replace("}", "", 1) # remove the closing brace of @supports

# Append the bulletproof class
css_patch = """
/* Bulletproof iOS Standalone fallback */
.ios-standalone .ios-safe-area-spacer {
  height: max(env(safe-area-inset-top), 24px) !important;
}
"""
content += css_patch

with open('src/index.css', 'w') as f:
    f.write(content)

with open('src/main.jsx', 'r') as f:
    main_content = f.read()

js_patch = """
// Bulletproof iOS PWA detection
if (typeof window !== 'undefined') {
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.userAgent.includes("Mac") && "ontouchend" in document);
  const isStandalone = window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches;
  if (isIOS && isStandalone) {
    document.documentElement.classList.add('ios-standalone');
  }
}
"""

if "ios-standalone" not in main_content:
    main_content = main_content.replace(
        "import App from './App.jsx'",
        "import App from './App.jsx'\n" + js_patch
    )
    with open('src/main.jsx', 'w') as f:
        f.write(main_content)

