import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

old_trend = """    // Daily Actual vs Budget trend -- budget is the monthly figure spread evenly
    // across that month's days, matching the same daily-budget logic as the Room
    // Revenue Budget page.
    const budgetByMonth = {}
    ;(budgetRows || []).forEach(b => { budgetByMonth[`${b.budget_year}-${b.budget_month}`] = Number(b.budgeted_room_revenue_usd) })
    const dailyTrend = (stats || []).map(s => {
      const [y, m] = s.stat_date.split('-')
      const key = `${y}-${Number(m)}`
      const daysInMon = new Date(Number(y), Number(m), 0).getDate()
      const monthlyBudget = budgetByMonth[key] || 0
      return { date: s.stat_date, Actual: Number(s.room_revenue_usd), Budget: Math.round((monthlyBudget / daysInMon) * 100) / 100 }
    })"""

new_trend = """    // Daily Actual vs Budget trend -- budget is now saved as the DAILY budgeted figure directly.
    const budgetByMonth = {}
    ;(budgetRows || []).forEach(b => { budgetByMonth[`${b.budget_year}-${b.budget_month}`] = Number(b.budgeted_room_revenue_usd) })
    const dailyTrend = (stats || []).map(s => {
      const [y, m] = s.stat_date.split('-')
      const key = `${y}-${Number(m)}`
      const dailyBudget = budgetByMonth[key] || 0
      return { date: s.stat_date, Actual: Number(s.room_revenue_usd), Budget: dailyBudget }
    })"""
code = code.replace(old_trend, new_trend)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
