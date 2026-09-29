with open('src/pages/Settings.jsx', 'r') as f:
    content = f.read()

content = content.replace("ShieldCheck, Check, X, Layers, Download", "ShieldCheck, Check, X, Layers, Download, AlertTriangle")

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(content)
