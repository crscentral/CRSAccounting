with open('public/sw.js', 'r') as f:
    content = f.read()

content = content.replace("const CACHE_NAME = 'crs-accounting-shell-v101'", "const CACHE_NAME = 'crs-accounting-shell-v102'")
content = content.replace("const CACHE_NAME = 'crs-accounting-shell-v100'", "const CACHE_NAME = 'crs-accounting-shell-v102'")

with open('public/sw.js', 'w') as f:
    f.write(content)
