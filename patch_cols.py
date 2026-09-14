import re

with open('src/pages/CapitalTransactions.jsx', 'r') as f:
    code = f.read()

# Add Amount (USD) to tables
code = code.replace(
    "{ key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },",
    "{ key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },\n              { key: 'amount_usd', label: `Amount (${cp.displayCurrency})`, render: r => cp.fmt(r.amount_usd) },"
)

with open('src/pages/CapitalTransactions.jsx', 'w') as f:
    f.write(code)
