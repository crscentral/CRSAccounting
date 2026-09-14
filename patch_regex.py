with open('src/lib/exportUtils.js', 'r') as f:
    content = f.read()

content = content.replace(r'const segments = remainder.split(/(\**.*?\**)/g);', r'const segments = remainder.split(/(\*\*.*?\*\*)/g);')

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(content)
