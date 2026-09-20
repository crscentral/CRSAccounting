import re

with open('src/pages/Transactions.jsx', 'r') as f:
    content = f.read()

# 1. Update loadData
old_loadData = """    if (['hotel', 'restaurant'].includes(activeProduct)) {
      siPromise = supabase.from('hotel_guest_invoices').select('id, invoice_number:id, invoice_date, amount_usd:invoice_amount_usd, currency, amount:invoice_amount_usd, contact:guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
      piPromise = supabase.from('hotel_expense_entries').select('id, invoice_number:id, invoice_date:expense_date, amount_usd, currency, amount, contact:supplier_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to)
    } else {"""
new_loadData = """    let rdrPromise = Promise.resolve({ data: [] })
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      siPromise = supabase.from('hotel_guest_invoices').select('id, invoice_number:id, invoice_date, amount_usd:invoice_amount_usd, currency, amount:invoice_amount_usd, contact:guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
      piPromise = supabase.from('hotel_expense_entries').select('id, invoice_number:id, invoice_date:expense_date, amount_usd, currency, amount, contact:supplier_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to)
      rdrPromise = supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
    } else {"""
content = content.replace(old_loadData, new_loadData)

old_await = """    const [{ data: si }, { data: pi }, { data: pr }] = await Promise.all([siPromise, piPromise, prPromise])"""
new_await = """    const [{ data: si }, { data: pi }, { data: pr }, { data: rdr }] = await Promise.all([siPromise, piPromise, prPromise, rdrPromise])"""
content = content.replace(old_await, new_await)

old_combined = """    const combined = [
      ...(si || []).map(r => ({ id: `si-${r.id}`, date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Guest Invoice' : 'Sales Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.contact || ''}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
      ...(pi || []).map(r => ({ id: `pi-${r.id}`, date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Expense' : 'Purchase Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.supplier_name_freeform || r.contact || ''}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'out' })),
      ...(pr || []).map(r => ({ id: `pr-${r.id}`, date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
    ].sort((a, b) => b.date.localeCompare(a.date))"""

new_combined = """    const combined = [
      ...(si || []).map(r => ({ id: `si-${r.id}`, date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Guest Invoice' : 'Sales Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.contact || ''}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
      ...(pi || []).map(r => ({ id: `pi-${r.id}`, date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Expense' : 'Purchase Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.supplier_name_freeform || r.contact || ''}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'out' })),
      ...(pr || []).map(r => ({ id: `pr-${r.id}`, date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
      ...(rdr || []).map(r => { const total = Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0)); return { id: `rdr-${r.id}`, date: r.revenue_date, type: 'F&B Revenue', desc: `${r.meal_period} F&B Revenue`, amount_usd: total, amount: total, currency: 'USD', direction: 'in' } }),
    ].sort((a, b) => b.date.localeCompare(a.date))"""
content = content.replace(old_combined, new_combined)

with open('src/pages/Transactions.jsx', 'w') as f:
    f.write(content)
