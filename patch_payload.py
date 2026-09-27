import re

for filename in ['src/pages/RestaurantExpenses.jsx', 'src/pages/HotelExpenses.jsx']:
    with open(filename, 'r') as f:
        content = f.read()

    old_payload = """      const payload = {
        company_id: companyId, product, expense_date: expenseDate, account_id: accountId,
        amount: Number(amount), currency, fx_rate_locked: fxRate, amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      }"""
      
    new_payload = """      const payload = {
        company_id: companyId, product, expense_date: expenseDate, account_id: accountId,
        amount: Number(amount), currency, fx_rate_locked: fxRate, amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
        invoice_number: invoiceNumber || null
      }"""

    content = content.replace(old_payload, new_payload)

    with open(filename, 'w') as f:
        f.write(content)
