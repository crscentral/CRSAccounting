import re

with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "icon: PiggyBank",
    "icon: Target"
)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
