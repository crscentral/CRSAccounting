import os

# 1. src/main.jsx
with open('src/main.jsx', 'r') as f: content = f.read()
content = content.replace("register('/CRSAccounting/sw.js')", "register('/sw.js')")
with open('src/main.jsx', 'w') as f: f.write(content)

# 2. src/App.jsx
with open('src/App.jsx', 'r') as f: content = f.read()
content = content.replace('basename="/CRSAccounting"', 'basename="/"')
with open('src/App.jsx', 'w') as f: f.write(content)

# 3. public/404.html
with open('public/404.html', 'r') as f: content = f.read()
content = content.replace('var pathSegmentsToKeep = 1;', 'var pathSegmentsToKeep = 0;')
content = content.replace('// keep "/CRSAccounting"', '// keep root')
content = content.replace('l.pathname.split(\'/\').slice(0, 1 + pathSegmentsToKeep).join(\'/\') + \'/?/\'', 'l.pathname.split(\'/\').slice(0, 1 + pathSegmentsToKeep).join(\'/\') + (l.pathname.endsWith(\'/\') ? \'?/\' : \'/?/\')')
with open('public/404.html', 'w') as f: f.write(content)

# 4. public/manifest.webmanifest
with open('public/manifest.webmanifest', 'r') as f: content = f.read()
content = content.replace('"/CRSAccounting/"', '"/"')
content = content.replace('"/CRSAccounting/icon-192.png"', '"/icon-192.png"')
content = content.replace('"/CRSAccounting/icon-512.png"', '"/icon-512.png"')
content = content.replace('"/CRSAccounting/icon-maskable-512.png"', '"/icon-maskable-512.png"')
with open('public/manifest.webmanifest', 'w') as f: f.write(content)

# 5. public/sw.js
with open('public/sw.js', 'r') as f: content = f.read()
content = content.replace("'/CRSAccounting/',", "'/',")
content = content.replace("'/CRSAccounting/index.html',", "'/index.html',")
content = content.replace("'/CRSAccounting/manifest.webmanifest',", "'/manifest.webmanifest',")
content = content.replace("'/CRSAccounting/icon-192.png',", "'/icon-192.png',")
content = content.replace("'/CRSAccounting/icon-512.png',", "'/icon-512.png',")
# Also bump the cache version so it invalidates
content = content.replace("crs-accounting-shell-v92", "crs-accounting-shell-v93")
with open('public/sw.js', 'w') as f: f.write(content)

# 6. vite.config.js
with open('vite.config.js', 'r') as f: content = f.read()
content = content.replace("base: '/CRSAccounting/',", "base: '/',")
with open('vite.config.js', 'w') as f: f.write(content)

