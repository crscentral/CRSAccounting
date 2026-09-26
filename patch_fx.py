with open('src/lib/fx.js', 'r') as f:
    content = f.read()

content = content.replace("new Date().toISOString().slice(0, 10)", """(() => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; })()""")

with open('src/lib/fx.js', 'w') as f:
    f.write(content)
