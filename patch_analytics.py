import re

with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

# 1. Add PI to the promises
old_promise = "const [{ data: hrs }, { data: hgi }, { data: hre }, { data: hee }, { data: rdr }] = await Promise.all(["
new_promise = "const [{ data: hrs }, { data: hgi }, { data: hre }, { data: hee }, { data: rdr }, { data: hPi }] = await Promise.all(["
content = content.replace(old_promise, new_promise)

# 2. Add the PI query
old_query = "supabase.from('restaurant_daily_revenue').select('revenue_date, total_amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('revenue_date', range.from).lte('revenue_date', range.to)"
new_query = "supabase.from('restaurant_daily_revenue').select('revenue_date, total_amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('revenue_date', range.from).lte('revenue_date', range.to),\n        supabase.from('purchase_invoices').select('invoice_date, amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)"
content = content.replace(old_query, new_query)

# 3. Add to daily loops
old_loop = """      (hee || []).forEach(r => {
        const d = r.expense_date; if (!m[d]) m[d] = { ...emptyDay() }
        m[d].expenses += Number(r.amount_usd)
      });"""
new_loop = """      (hee || []).forEach(r => {
        const d = r.expense_date; if (!m[d]) m[d] = { ...emptyDay() }
        m[d].expenses += Number(r.amount_usd)
      });
      (hPi || []).forEach(r => {
        const d = r.invoice_date; if (!m[d]) m[d] = { ...emptyDay() }
        m[d].expenses += Number(r.amount_usd)
      });"""
content = content.replace(old_loop, new_loop)

# 4. Same for totals
old_totals = """      setTotals({
        revenue: Object.values(m).reduce((s, d) => s + d.revenue, 0),
        expenses: Object.values(m).reduce((s, d) => s + d.expenses, 0),
        invoiced: Object.values(m).reduce((s, d) => s + d.invoiced, 0),
        collected: Object.values(m).reduce((s, d) => s + d.collected, 0)
      })"""
# Actually totals are dynamically derived from `m`, so they will just automatically work!

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(content)
