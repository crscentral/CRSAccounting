import re
with open('src/pages/SalesInvoices.jsx', 'r') as f:
    content = f.read()

old_logic = """  const totalUsd = invoices.reduce((s, i) => s + Number(i.amount_usd), 0)
  const collectedUsd = invoices.filter(i => i.status === 'Paid').reduce((s, i) => s + Number(i.amount_usd), 0)
  const pendingUsd = invoices.filter(i => i.status !== 'Paid').reduce((s, i) => s + ((Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)"""

new_logic = """  const totalUsd = invoices.reduce((s, i) => s + Number(i.amount_usd), 0)
  const pendingUsd = invoices.reduce((s, i) => s + (i.status === 'Paid' ? 0 : ((Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd))), 0)
  const collectedUsd = totalUsd - pendingUsd"""

content = content.replace(old_logic, new_logic)

old_overdue = "value={cp.fmt(invoices.filter(i => i.status === 'Overdue').reduce((s, i) => s + Number(i.amount_usd), 0))}"
new_overdue = "value={cp.fmt(invoices.filter(i => i.status === 'Overdue').reduce((s, i) => s + ((Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0))}"
content = content.replace(old_overdue, new_overdue)

with open('src/pages/SalesInvoices.jsx', 'w') as f:
    f.write(content)
