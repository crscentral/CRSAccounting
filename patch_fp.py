import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

# 1. Add PI to the promises
old_promise = "const [{ data: hrs }, { data: hgi }, { data: hee }, { data: hre }, { data: rdr }] = await Promise.all(["
new_promise = "const [{ data: hrs }, { data: hgi }, { data: hee }, { data: hre }, { data: rdr }, { data: hPi }] = await Promise.all(["
content = content.replace(old_promise, new_promise)

# 2. Add the PI query
old_query = "supabase.from('restaurant_daily_revenue').select('revenue_date, total_amount_usd, food_amount_usd, beverage_amount_usd, other_amount_usd, collected_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('revenue_date', range.from).lte('revenue_date', range.to)"
new_query = "supabase.from('restaurant_daily_revenue').select('revenue_date, total_amount_usd, food_amount_usd, beverage_amount_usd, other_amount_usd, collected_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('revenue_date', range.from).lte('revenue_date', range.to),\n        supabase.from('purchase_invoices').select('invoice_date, amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)"
content = content.replace(old_query, new_query)

# 3. Add to totalExpenses
old_exp = "const expensesUsd = (hee || []).reduce((s, r) => s + Number(r.amount_usd), 0) + amcUsd"
new_exp = "const expensesUsd = (hee || []).reduce((s, r) => s + Number(r.amount_usd), 0) + amcUsd + (hPi || []).reduce((s, r) => s + Number(r.amount_usd), 0)"
content = content.replace(old_exp, new_exp)

# 4. Add to breakdown (we can classify purchase_invoices as 'Purchase Invoices' subtype)
old_breakdown = "totalOperatingExpenses: 0,"
new_breakdown = "totalOperatingExpenses: 0,\n      totalPurchaseInvoices: 0,"
content = content.replace(old_breakdown, new_breakdown)

old_loop = """      (hee || []).forEach(r => {
        if (r.account?.subtype === 'Hotel Operating Expenses') {
          m.totalOperatingExpenses += Number(r.amount_usd)"""
new_loop = """      (hPi || []).forEach(r => m.totalPurchaseInvoices += Number(r.amount_usd));
      (hee || []).forEach(r => {
        if (r.account?.subtype === 'Hotel Operating Expenses') {
          m.totalOperatingExpenses += Number(r.amount_usd)"""
content = content.replace(old_loop, new_loop)

# 5. Add to Total Expenses inside period logic
old_tot_exp = "m.totalExpenses = amcPortion + m.totalOperatingExpenses + m.totalFixedExpenses"
new_tot_exp = "m.totalExpenses = amcPortion + m.totalOperatingExpenses + m.totalFixedExpenses + m.totalPurchaseInvoices"
content = content.replace(old_tot_exp, new_tot_exp)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
