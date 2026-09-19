import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    code = f.read()

# Fix 1: Top KPIs
old_kpi = """  const revenue = sales.reduce((s, i) => s + Number(i.amount_usd), 0)
  const expenses = purchases.reduce((s, i) => s + Number(i.amount_usd), 0)
  const profit = revenue - expenses"""

new_kpi = """  const revenue = activeProduct === 'hotel' ? revenueByAccount.reduce((s, a) => s + a.amount, 0) : sales.reduce((s, i) => s + Number(i.amount_usd), 0)
  const expenses = activeProduct === 'hotel' ? expensesByAccount.reduce((s, a) => s + a.amount, 0) : purchases.reduce((s, i) => s + Number(i.amount_usd), 0)
  const profit = revenue - expenses"""
code = code.replace(old_kpi, new_kpi)

# Fix 2: loadForecast linking
old_load = """  async function loadForecast() {
    const { data } = await supabase.from('forecast_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('forecast_year', forecastYear).order('forecast_month')
    setForecast(data || [])
  }"""

new_load = """  async function loadForecast() {
    const [{ data }, { data: budget }] = await Promise.all([
      supabase.from('forecast_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('forecast_year', forecastYear).order('forecast_month'),
      activeProduct === 'hotel' ? supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', forecastYear) : Promise.resolve({ data: [] })
    ])
    
    const combined = data ? [...data] : []
    if (activeProduct === 'hotel' && budget) {
      budget.forEach(b => {
        let f = combined.find(x => x.forecast_month === b.budget_month)
        if (!f) {
           f = { forecast_month: b.budget_month, revenue_usd: 0, expenses_usd: 0 }
           combined.push(f)
        }
        // Force sync revenue from budget
        f.revenue_usd = b.budgeted_room_revenue_usd || 0
      })
    }
    combined.sort((a, b) => a.forecast_month - b.forecast_month)
    setForecast(combined)
  }"""
code = code.replace(old_load, new_load)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(code)
