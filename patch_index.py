import os

with open('index.html', 'r') as f:
    content = f.read()

content = content.replace('"/CRSAccounting/favicon.png"', '"/favicon.png"')
content = content.replace('"/CRSAccounting/manifest.webmanifest"', '"/manifest.webmanifest"')
content = content.replace('"/CRSAccounting/apple-touch-icon.png"', '"/apple-touch-icon.png"')

with open('index.html', 'w') as f:
    f.write(content)
