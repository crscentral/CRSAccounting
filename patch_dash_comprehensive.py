import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

# 1. Add status to the first Promise.all for purchase_invoices
content = content.replace(
    "supabase.from('purchase_invoices').select('invoice_date, amount_usd, currency, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }).limit(10)",
    "supabase.from('purchase_invoices').select('invoice_date, amount_usd, currency, status, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }).limit(10)"
)

# 2. Add status to the second Promise.all for purchase_invoices
content = content.replace(
    "supabase.from('purchase_invoices').select('invoice_date, amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct)",
    "supabase.from('purchase_invoices').select('invoice_date, amount_usd, status').eq('company_id', activeCompany.id).eq('product', activeProduct)"
)

# 3. Add piExpensesPaid to Expenses Made calculation
old_expenses_made = """    // Expenses Made = Actual cash out (hotel expense entries).
    expensesMade = directExpenses + amcTotal"""
new_expenses_made = """    // Expenses Made = Actual cash out (hotel expense entries).
    const piExpensesPaid = hotelPurchaseInvoices.reduce((s, e) => s + (e.status === 'Paid' ? Number(e.amount_usd || 0) : 0), 0)
    expensesMade = directExpenses + amcTotal + piExpensesPaid"""
content = content.replace(old_expenses_made, new_expenses_made)

# 4. Add allHotelPurchaseInvoices to the monthlyMap loop
old_monthly_loop = """    allHotelExpenseEntries.forEach(r => {
      const key = (r.expense_date || '').slice(0, 7)
      uniqueMonths.add(key)
      if (!key) return
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Expenses += Number(r.amount_usd)
    })"""
new_monthly_loop = """    allHotelExpenseEntries.forEach(r => {
      const key = (r.expense_date || '').slice(0, 7)
      uniqueMonths.add(key)
      if (!key) return
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Expenses += Number(r.amount_usd)
    })
    
    allHotelPurchaseInvoices.forEach(r => {
      const key = (r.invoice_date || '').slice(0, 7)
      uniqueMonths.add(key)
      if (!key) return
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Expenses += Number(r.amount_usd)
    })"""
content = content.replace(old_monthly_loop, new_monthly_loop)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)
