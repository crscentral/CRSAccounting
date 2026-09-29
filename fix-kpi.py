import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

target = "const totalExpenses = entriesTotalUsd + amcTotalForView + piTotalUsd"
replacement = """const totalExpenses = entriesTotalUsd + amcTotalForView + piTotalUsd

  const totalHotelExpenses = entries.filter(e => e.product === 'hotel').reduce((s, r) => s + Number(r.amount_usd), 0)
    + amcContracts.filter(e => e.product === 'hotel').reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    + purchaseInvoices.filter(e => e.product === 'hotel').reduce((s, r) => s + Number(r.amount_usd), 0);

  const totalRestExpenses = entries.filter(e => e.product === 'restaurant').reduce((s, r) => s + Number(r.amount_usd), 0)
    + amcContracts.filter(e => e.product === 'restaurant').reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    + purchaseInvoices.filter(e => e.product === 'restaurant').reduce((s, r) => s + Number(r.amount_usd), 0);
"""

content = content.replace(target, replacement)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)
