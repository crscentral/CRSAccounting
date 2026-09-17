import re

with open('src/pages/HotelOccupancyStats.jsx', 'r') as f:
    code = f.read()

# Update variance calculation to use DAILY budget properly multiplied.
old_budget = """  // Budget comparison
  const thisMonthBudget = budget.find(b => b.budget_year === now.getFullYear() && b.budget_month === now.getMonth() + 1)
  const ytdBudget = budget.filter(b => b.budget_year === now.getFullYear() && b.budget_month <= now.getMonth() + 1).reduce((s, b) => s + Number(b.budgeted_room_revenue_usd), 0)
  const variance = (view === 'mtd' && thisMonthBudget) ? totalRevenue - Number(thisMonthBudget.budgeted_room_revenue_usd)
    : (view === 'ytd' ? totalRevenue - ytdBudget : null)"""

new_budget = """  // Budget comparison (Budgets are now saved as DAILY amounts)
  const thisMonthBudget = budget.find(b => b.budget_year === now.getFullYear() && b.budget_month === now.getMonth() + 1)
  
  function daysInMonth(y, m) { return new Date(y, m, 0).getDate() }
  
  // Calculate MTD target by taking daily budget * number of days passed in current month
  const daysPassedMTD = now.getDate()
  const mtdTarget = thisMonthBudget ? Number(thisMonthBudget.budgeted_room_revenue_usd) * daysPassedMTD : 0
  
  // Calculate YTD target
  const ytdTarget = budget.filter(b => b.budget_year === now.getFullYear() && b.budget_month <= now.getMonth() + 1).reduce((s, b) => {
    const isCurrentMonth = b.budget_month === now.getMonth() + 1
    const daysToUse = isCurrentMonth ? daysPassedMTD : daysInMonth(b.budget_year, b.budget_month)
    return s + (Number(b.budgeted_room_revenue_usd) * daysToUse)
  }, 0)

  const variance = (view === 'mtd' && thisMonthBudget) ? totalRevenue - mtdTarget
    : (view === 'ytd' ? totalRevenue - ytdTarget : null)"""

code = code.replace(old_budget, new_budget)

with open('src/pages/HotelOccupancyStats.jsx', 'w') as f:
    f.write(code)
