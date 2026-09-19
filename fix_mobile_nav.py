import re

with open('src/components/AppShell.jsx', 'r') as f:
    code = f.read()

old_label = "<span>{item.label.split(' ')[0]}</span>"
new_label = "{const short = item.to === '/hotel-stats' ? 'Rev & Occ' : item.to === '/hotel-revenue' ? 'Daily Rev' : item.label.split(' ')[0]; return <span>{short}</span>}()"

code = code.replace(old_label, new_label)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(code)
