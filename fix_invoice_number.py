import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

old_draft = "status: 'Pending'"
new_draft = "status: 'Pending',\n        invoice_number: i.id ? i.id.slice(0, 8).toUpperCase() : '—'"
code = code.replace(old_draft, new_draft)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
