with open('public/sw.js', 'r') as f:
    content = f.read()

content = content.replace("const CACHE_NAME = 'crs-accounting-shell-v103'", "const CACHE_NAME = 'crs-accounting-shell-v104'")

with open('public/sw.js', 'w') as f:
    f.write(content)
