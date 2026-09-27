with open('src/index.css', 'r') as f:
    content = f.read()

css_patch = """
/* iOS PWA Safe Area Spacer */
.ios-safe-area-spacer {
  height: env(safe-area-inset-top, 0px);
}

/* Force minimum 24px on iOS PWAs */
@supports (-webkit-touch-callout: none) {
  @media (display-mode: standalone) {
    .ios-safe-area-spacer {
      height: max(env(safe-area-inset-top), 24px) !important;
    }
  }
}
"""

if "ios-safe-area-spacer" not in content:
    with open('src/index.css', 'a') as f:
        f.write(css_patch)

with open('src/components/AppShell.jsx', 'r') as f:
    app_content = f.read()

app_content = app_content.replace(
    'style={safeAreaStyle}',
    'className="w-full shrink-0 bg-navy-700 ios-safe-area-spacer"'
)
# Also remove the duplicate className in the template since we replaced the style prop with the full className string
app_content = app_content.replace(
    'className="w-full shrink-0 bg-navy-700" className="w-full shrink-0 bg-navy-700 ios-safe-area-spacer"',
    'className="w-full shrink-0 bg-navy-700 ios-safe-area-spacer"'
)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(app_content)
