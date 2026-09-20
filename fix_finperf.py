import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

# 1. Update revenue and expenses calculations
old_rev = """  const revenue = activeProduct === 'hotel' ? revenueByAccount.reduce((s, a) => s + a.amount, 0) : sales.reduce((s, i) => s + Number(i.amount_usd), 0)
  const expenses = activeProduct === 'hotel' ? expensesByAccount.reduce((s, a) => s + a.amount, 0) : purchases.reduce((s, i) => s + Number(i.amount_usd), 0)"""
new_rev = """  const revenue = ['hotel', 'restaurant'].includes(activeProduct) ? revenueByAccount.reduce((s, a) => s + a.amount, 0) : sales.reduce((s, i) => s + Number(i.amount_usd), 0)
  const expenses = ['hotel', 'restaurant'].includes(activeProduct) ? expensesByAccount.reduce((s, a) => s + a.amount, 0) : purchases.reduce((s, i) => s + Number(i.amount_usd), 0)"""
content = content.replace(old_rev, new_rev)

# 2. Update loadForecast to include restaurant logic for budget
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
        } else {
          revMap[b.budget_month] = (revMap[b.budget_month] || 0) + (Number(b.amount_usd) || 0) 
        }
      })
      
      const expMap = {}"""
content = content.replace(old_forecast, new_forecast)

# Wait! The restaurant budget is in `hotel_revenue_budget`?
# In F&B Revenue Budget, the table is `hotel_expense_budget` because we store all budgeted accounts there for restaurant!
# Actually, wait. Let's look at `HotelBudget.jsx` to see how Restaurant Budget is saved!
