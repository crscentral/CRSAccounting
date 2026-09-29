with open('src/pages/Ledger.jsx', 'r') as f:
    content = f.read()

# Fix table render
old_render = "          { key: 'balance', label: `Balance (${cp.displayCurrency})`, render: r => cp.fmt(r.balance) },"
new_render = "          { key: 'balance', label: `Balance (${cp.displayCurrency})`, render: r => r.balance < 0 ? `${cp.fmt(Math.abs(r.balance))} Cr` : (r.balance > 0 ? `${cp.fmt(r.balance)} Dr` : cp.fmt(0)) },"
content = content.replace(old_render, new_render)

# Fix export render
old_export = "return [e.entry_date, e.description, e.currency, Number(e.debit_usd) ? fmt(e.debit_usd) : '—', Number(e.credit_usd) ? fmt(e.credit_usd) : '—', fmt(running)]"
new_export = "const balStr = running < 0 ? `${fmt(Math.abs(running))} Cr` : (running > 0 ? `${fmt(running)} Dr` : fmt(0)); return [e.entry_date, e.description, e.currency, Number(e.debit_usd) ? fmt(e.debit_usd) : '—', Number(e.credit_usd) ? fmt(e.credit_usd) : '—', balStr]"
content = content.replace(old_export, new_export)

with open('src/pages/Ledger.jsx', 'w') as f:
    f.write(content)

