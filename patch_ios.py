import re

with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

old_ios_text = """          <span className="text-slate-700 truncate">
            Install this app: tap <Share size={13} className="inline -mt-0.5" /> Share, then <strong>"Add to Home Screen"</strong>.
          </span>"""

new_ios_text = """          <span className="text-slate-700 text-xs sm:text-sm">
            <strong>To install on iOS/iPad:</strong> Tap the <Share size={13} className="inline -mt-0.5 mx-1" /> Share icon in the Safari address bar above, then scroll down and select <strong>"Add to Home Screen"</strong>.
          </span>"""

content = content.replace(old_ios_text, new_ios_text)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)

with open('index.html', 'r') as f:
    html = f.read()

html = html.replace('content="black-translucent"', 'content="default"')
html = html.replace('viewport-fit=cover', '') # just standard viewport is safer to avoid all safe area bugs if we don't have css env vars set everywhere

with open('index.html', 'w') as f:
    f.write(html)
