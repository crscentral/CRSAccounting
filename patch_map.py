import re

with open('src/pages/Settings.jsx', 'r') as f:
    code = f.read()

code = code.replace(
    'company.company_products.map',
    '(company.company_products || []).map'
)
code = code.replace(
    'c.company_products.map',
    '(c.company_products || []).map'
)

with open('src/pages/Settings.jsx', 'w') as f:
    f.write(code)
