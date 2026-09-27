with open('public/sw.js', 'r') as f:
    content = f.read()

content = content.replace("const CACHE_NAME = 'crs-accounting-shell-v96'", "const CACHE_NAME = 'crs-accounting-shell-v97'")

with open('public/sw.js', 'w') as f:
    f.write(content)
