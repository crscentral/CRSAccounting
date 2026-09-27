import re

with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

replacements = [
    ('i.invoice_date.slice(0, 7)', "(i.invoice_date || '').slice(0, 7) || 'Unknown'"),
    ('r.stat_date.slice(0, 7)', "(r.stat_date || '').slice(0, 7) || 'Unknown'"),
    ('r.entry_date.slice(0, 7)', "(r.entry_date || '').slice(0, 7) || 'Unknown'"),
    ('r.receipt_date.slice(0, 7)', "(r.receipt_date || '').slice(0, 7) || 'Unknown'"),
    ('a.month.localeCompare(b.month)', "(a.month || '').localeCompare(b.month || '')")
]

for old, new in replacements:
    content = content.replace(old, new)

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(content)
