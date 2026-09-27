with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

# Sidebar spacer
content = content.replace(
    '<div className="w-full shrink-0" style={{ height: \'env(safe-area-inset-top)\' }} />',
    '<div className="w-full shrink-0 bg-navy-700" style={{ height: \'env(safe-area-inset-top)\' }} />'
)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
