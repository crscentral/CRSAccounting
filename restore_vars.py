with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

anchor = "const restEntriesTotal = restEntries.reduce((s, r) => s + Number(r.amount_usd), 0)"
to_insert = """
  const piTotalUsd = purchaseInvoices.reduce((s, r) => s + Number(r.amount_usd), 0)
  const totalExpenses = entriesTotalUsd + amcTotalForView + piTotalUsd

  const entriesTotalPaidUsd = entries.reduce((s, r) => s + Number(r.paid_amount_usd || 0), 0)
  const amcMonthlyPaidUsd = amcContracts.reduce((s, r) => s + (Number(r.paid_amount_usd || 0) / 12), 0)
  const amcTotalPaidForView = amcMonthlyPaidUsd * monthsInView
  const piTotalPaidUsd = purchaseInvoices.reduce((s, r) => s + (r.status === 'Paid' ? Number(r.amount_usd) : 0), 0)
"""

content = content.replace(anchor, anchor + "\n" + to_insert)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)
