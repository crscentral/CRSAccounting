import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

new_promise_all = """
    const [{ data }, { data: budget }, { data: expBudget }, { data: accountsData }] = await Promise.all([
      supabase.from('forecast_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('forecast_year', forecastYear).order('forecast_month'),
      activeProduct === 'hotel' ? supabase.from('hotel_room_revenue_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', forecastYear) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('budget_year', forecastYear) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('accounts').select('code, type').eq('company_id', activeCompany.id) : Promise.resolve({ data: [] })
    ])
"""

content = re.sub(
    r"const \[\{ data \}, \{ data: budget \}, \{ data: expBudget \}\] = await Promise\.all\(\[.*?\]\)",
    new_promise_all.strip(),
    content,
    flags=re.DOTALL
)

new_mapping = """
    const combined = data ? [...data] : []
    if (activeProduct === 'hotel') {
      const revMap = {}
      if (budget) budget.forEach(b => { const days = new Date(forecastYear, b.budget_month, 0).getDate(); revMap[b.budget_month] = (revMap[b.budget_month] || 0) + ((b.budgeted_room_revenue_usd || 0) * days) })
      
      const expMap = {}
      
      // Separate Ancillary Revenue from Expenses based on account type
      if (expBudget && accountsData) {
        const accountTypeMap = {}
        accountsData.forEach(a => accountTypeMap[a.code] = a.type)
        
        expBudget.forEach(b => {
          const type = accountTypeMap[b.account_code]
          if (type === 'Revenue') {
            revMap[b.budget_month] = (revMap[b.budget_month] || 0) + (Number(b.amount_usd) || 0)
          } else {
            expMap[b.budget_month] = (expMap[b.budget_month] || 0) + (Number(b.amount_usd) || 0)
          }
        })
      }
"""

content = re.sub(
    r"const combined = data \? \[\.\.\.data\] : \[\]\n\s*if \(activeProduct === 'hotel'\) \{.*const expMap = \{\}\n\s*if \(expBudget\) expBudget\.forEach.*?Number\(b\.amount_usd\) \|\| 0\)\)",
    new_mapping.strip(),
    content,
    flags=re.DOTALL
)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
