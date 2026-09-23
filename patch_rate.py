import re

with open('src/pages/SalesInvoices.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "r.currency === 'USD' ? '1.0000' : (r.fx_rate_locked || (r.amount / r.amount_usd).toFixed(4))",
    "r.currency === 'USD' ? '1.00' : Number(r.fx_rate_locked || (r.amount / r.amount_usd)).toFixed(2)"
)

with open('src/pages/SalesInvoices.jsx', 'w') as f:
    f.write(content)
