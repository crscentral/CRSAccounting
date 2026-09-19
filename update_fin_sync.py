with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    code = f.read()

old_load_forecast = """  async function loadForecast() {
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
    }"""

new_load_forecast = """  async function loadForecast() {
    const [{ data }, { data: budget }, { data: expBudget }] = await Promise.all([
      supabase.from('forecast_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('forecast_year', forecastYear).order('forecast_month'),
      activeProduct === 'hotel' ? supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', forecastYear) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('budget_year', forecastYear) : Promise.resolve({ data: [] })
    ])
    
    const combined = data ? [...data] : []
    if (activeProduct === 'hotel') {
      const revMap = {}
      if (budget) budget.forEach(b => revMap[b.budget_month] = (revMap[b.budget_month] || 0) + (b.budgeted_room_revenue_usd || 0))
      
      const expMap = {}
      if (expBudget) expBudget.forEach(b => expMap[b.budget_month] = (expMap[b.budget_month] || 0) + (Number(b.amount_usd) || 0))
      
      for (let i=1; i<=12; i++) {
        if (revMap[i] || expMap[i]) {
          let f = combined.find(x => x.forecast_month === i)
          if (!f) {
             f = { forecast_month: i, revenue_usd: 0, expenses_usd: 0 }
             combined.push(f)
          }
          if (revMap[i] !== undefined) f.revenue_usd = revMap[i]
          if (expMap[i] !== undefined) f.expenses_usd = expMap[i]
        }
      }
    }"""

code = code.replace(old_load_forecast, new_load_forecast)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(code)
