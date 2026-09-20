import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

old_promise = """  async function loadForecast() {
    const [{ data }, { data: budget }, { data: expBudget }, { data: accountsData }] = await Promise.all([
      supabase.from('forecast_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('forecast_year', forecastYear).order('forecast_month'),
      activeProduct === 'hotel' ? supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', forecastYear) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('budget_year', forecastYear) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('accounts').select('code, type').eq('company_id', activeCompany.id).eq('product', 'hotel') : Promise.resolve({ data: [] })
    ])"""

new_promise = """  async function loadForecast() {
    const [{ data }, { data: budget }, { data: expBudget }, { data: accountsData }] = await Promise.all([
      supabase.from('forecast_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('forecast_year', forecastYear).order('forecast_month'),
      supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', forecastYear),
      supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', forecastYear),
      supabase.from('accounts').select('code, type').eq('company_id', activeCompany.id).eq('product', activeProduct)
    ])"""

content = content.replace(old_promise, new_promise)

# Fix the IF block
old_if = """    const combined = data ? [...data] : []
    if (activeProduct === 'hotel') {
      const revMap = {}
      if (budget) budget.forEach(b => { const days = new Date(forecastYear, b.budget_month, 0).getDate(); revMap[b.budget_month] = (revMap[b.budget_month] || 0) + ((b.budgeted_room_revenue_usd || 0) * days) })
      
      const expMap = {}
      
      // Separate Ancillary Revenue from Expenses based on account type
      if (expBudget && accountsData) {
        const accountTypeMap = {}
        accountsData.forEach(a => accountTypeMap[a.code] = a.type)
        
        expBudget.forEach(b => {
          if (accountTypeMap[b.account_code] === 'Revenue') {
            revMap[b.budget_month] = (revMap[b.budget_month] || 0) + (Number(b.amount_usd) || 0)
          } else {
            expMap[b.budget_month] = (expMap[b.budget_month] || 0) + (Number(b.amount_usd) || 0)
          }
        })
      }

      for (let m = 1; m <= 12; m++) {
        let entry = combined.find(x => x.forecast_month === m)
        if (!entry) {
          entry = { forecast_month: m, revenue_usd: revMap[m] || 0, expenses_usd: expMap[m] || 0 }
          combined.push(entry)
        } else {
          if (!entry.revenue_usd && revMap[m]) entry.revenue_usd = revMap[m]
          if (!entry.expenses_usd && expMap[m]) entry.expenses_usd = expMap[m]
        }
      }
    }"""

new_if = """    const combined = data ? [...data] : []
    
    const revMap = {}
    if (budget) budget.forEach(b => { 
        if (activeProduct === 'hotel') {
            const days = new Date(forecastYear, b.budget_month, 0).getDate(); 
            revMap[b.budget_month] = (revMap[b.budget_month] || 0) + ((b.budgeted_room_revenue_usd || 0) * days) 
        }
    })
    
    const expMap = {}
    
    if (expBudget && accountsData) {
      const accountTypeMap = {}
      accountsData.forEach(a => accountTypeMap[a.code] = a.type)
      
      expBudget.forEach(b => {
        if (accountTypeMap[b.account_code] === 'Revenue') {
          revMap[b.budget_month] = (revMap[b.budget_month] || 0) + (Number(b.amount_usd) || 0)
        } else {
          expMap[b.budget_month] = (expMap[b.budget_month] || 0) + (Number(b.amount_usd) || 0)
        }
      })
    }

    for (let m = 1; m <= 12; m++) {
      let entry = combined.find(x => x.forecast_month === m)
      if (!entry) {
        entry = { forecast_month: m, revenue_usd: revMap[m] || 0, expenses_usd: expMap[m] || 0 }
        combined.push(entry)
      } else {
        // ALWAYS overwrite with the budget if the budget exists, because user wants it to "travel".
        // The previous logic only set it if !entry.expenses_usd!
        if (revMap[m] !== undefined && revMap[m] > 0) entry.revenue_usd = revMap[m]
        if (expMap[m] !== undefined && expMap[m] > 0) entry.expenses_usd = expMap[m]
      }
    }"""

content = content.replace(old_if, new_if)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
