import re

with open('src/pages/Transactions.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    'const dStr = `${r.start_year}-${String(r.start_month).padStart(2, \'0\')}-01`',
    'const dStr = r.start_year ? `${r.start_year}-${String(r.start_month).padStart(2, \'0\')}-01` : (r.created_at || \'\').split(\'T\')[0]'
)

with open('src/pages/Transactions.jsx', 'w') as f:
    f.write(content)

