import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

old_forecast = """    if (activeProduct === 'hotel') {
      const revMap = {}
      if (budget) budget.forEach(b => { const days = new Date(forecastYear, b.budget_month, 0).getDate(); revMap[b.budget_month] = (revMap[b.budget_month] || 0) + ((b.budgeted_room_revenue_usd || 0) * days) })
      
      const expMap = {}"""

new_forecast = """    if (['hotel', 'restaurant'].includes(activeProduct)) {
      const revMap = {}
      if (budget) budget.forEach(b => { 
        if (activeProduct === 'hotel') {
          const days = new Date(forecastYear, b.budget_month, 0).getDate(); 
          revMap[b.budget_month] = (revMap[b.budget_month] || 0) + ((b.budgeted_room_revenue_usd || 0) * days) 
        }
      })
      
      const expMap = {}"""

content = content.replace(old_forecast, new_forecast)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
