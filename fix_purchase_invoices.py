with open('src/pages/PurchaseInvoices.jsx', 'r') as f:
    content = f.read()

old_logic = """  const totalUsd = invoices.reduce((s, i) => s + Number(i.amount_usd), 0)
  const paidUsd = invoices.filter(i => i.status === 'Paid').reduce((s, i) => s + Number(i.amount_usd), 0)
  const pendingUsd = invoices.filter(i => i.status !== 'Paid').reduce((s, i) => s + Number(i.amount_usd), 0)"""

new_logic = """  const totalUsd = invoices.reduce((s, i) => s + Number(i.amount_usd), 0)
  const pendingUsd = invoices.reduce((s, i) => s + (i.status === 'Paid' ? 0 : Number(i.amount_usd)), 0)
  const paidUsd = totalUsd - pendingUsd"""
  
content = content.replace(old_logic, new_logic)

with open('src/pages/PurchaseInvoices.jsx', 'w') as f:
    f.write(content)
