with open('src/index.css', 'r') as f:
    content = f.read()

# Delete everything from "/* iOS PWA Safe Area Spacer */" to the end
idx = content.find("/* iOS PWA Safe Area Spacer */")
if idx != -1:
    content = content[:idx]

new_css = """/* iOS PWA Safe Area Spacer */
.ios-safe-area-spacer {
  height: env(safe-area-inset-top, 0px);
}

/* Bulletproof iOS Standalone fallback */
.ios-standalone .ios-safe-area-spacer {
  height: max(env(safe-area-inset-top), 24px) !important;
}
"""

with open('src/index.css', 'w') as f:
    f.write(content + new_css)
