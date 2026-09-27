import re

with open('src/main.jsx', 'r') as f:
    content = f.read()

old_js = """  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.userAgent.includes("Mac") && "ontouchend" in document);
  const isStandalone = window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches;
  if (isIOS && isStandalone) {
    document.documentElement.classList.add('ios-standalone');
  }"""

new_js = """  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.userAgent.includes("Mac") && "ontouchend" in document);
  const isIPad = /iPad/.test(navigator.userAgent) || (navigator.userAgent.includes("Mac") && "ontouchend" in document);
  const isStandalone = window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches;
  
  if (isIOS && isStandalone) {
    document.documentElement.classList.add('ios-standalone');
  }
  if (isIPad && isStandalone) {
    document.documentElement.classList.add('ipad-standalone');
  }"""

content = content.replace(old_js, new_js)

with open('src/main.jsx', 'w') as f:
    f.write(content)

with open('src/index.css', 'r') as f:
    css_content = f.read()

old_css = """.ios-standalone .ios-safe-area-spacer {
  height: max(env(safe-area-inset-top), 24px) !important;
}"""

new_css = """.ios-standalone .ios-safe-area-spacer {
  height: env(safe-area-inset-top, 0px);
}

@media (min-width: 768px) {
  /* On iPads in full-screen PWA mode, Apple overlaps the status bar but reports 0px safe area.
     We force 24px padding. In split-view (<768px), it behaves correctly without padding. */
  .ipad-standalone .ios-safe-area-spacer {
    height: 24px !important;
  }
}"""

css_content = css_content.replace(old_css, new_css)

with open('src/index.css', 'w') as f:
    f.write(css_content)

