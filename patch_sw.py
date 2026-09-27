with open('public/sw.js', 'r') as f:
    content = f.read()

content = content.replace("const CACHE_NAME = 'crs-accounting-shell-v97'", "const CACHE_NAME = 'crs-accounting-shell-v98'")

with open('public/sw.js', 'w') as f:
    f.write(content)
