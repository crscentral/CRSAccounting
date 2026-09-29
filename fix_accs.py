import re
with open('src/pages/Comparison.jsx', 'r') as f:
    content = f.read()

content = content.replace("accs || []", "accounts || []")

with open('src/pages/Comparison.jsx', 'w') as f:
    f.write(content)
