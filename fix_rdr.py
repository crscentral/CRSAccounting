import re

with open('src/pages/Transactions.jsx', 'r') as f:
    content = f.read()

content = content.replace(
"""    let prPromise = supabase.from('payment_receipts').select('id, receipt_date, amount_usd, currency, amount').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to)
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {""",
"""    let prPromise = supabase.from('payment_receipts').select('id, receipt_date, amount_usd, currency, amount').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to)
    let rdrPromise = Promise.resolve({ data: [] })
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {"""
)

content = content.replace(
"""      piPromise = supabase.from('hotel_expense_entries').select('id, invoice_number:id, invoice_date:expense_date, amount_usd, currency, amount, contact:supplier_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to)
    } else {""",
"""      piPromise = supabase.from('hotel_expense_entries').select('id, invoice_number:id, invoice_date:expense_date, amount_usd, currency, amount, contact:supplier_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to)
      rdrPromise = supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
    } else {"""
)

with open('src/pages/Transactions.jsx', 'w') as f:
    f.write(content)

