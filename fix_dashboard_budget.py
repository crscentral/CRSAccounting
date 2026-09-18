import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Fix the budget sum to cover the entire date range, not just the days with stats
old_daily_trend = r"""    const budgetByMonth = \{\}
    ;\(budgetRows \|\| \[\]\).forEach\(b => \{ budgetByMonth\[`\$\{b.budget_year\}-\$\{b.budget_month\}`\] = Number\(b.budgeted_room_revenue_usd\) \}\)
    const dailyTrend = \(stats \|\| \[\]\).map\(s => \{
      const \[y, m\] = s.stat_date.split\('-'\)
      const key = `\$\{y\}-\$\{Number\(m\)\}`
      const dailyBudget = budgetByMonth\[key\] \|\| 0
      return \{ date: s.stat_date, Actual: Number\(s.room_revenue_usd\), Budget: dailyBudget \}
    \}\)
    const totalBudgetUsd = dailyTrend.reduce\(\(sum, d\) => sum \+ d.Budget, 0\)
    const totalVarianceUsd = totalRevenue - totalBudgetUsd"""

new_daily_trend = """    const budgetByMonth = {}
    ;(budgetRows || []).forEach(b => { budgetByMonth[`${b.budget_year}-${b.budget_month}`] = Number(b.budgeted_room_revenue_usd) })
    
    // Create a complete date range array for the trend chart and budget calculation
    const dailyTrendMap = {}
    let currentDate = new Date(cp.range.from)
    const endDate = new Date(cp.range.to)
    let totalBudgetUsd = 0
    
    while (currentDate <= endDate) {
      const d = currentDate.toISOString().slice(0, 10)
      const y = currentDate.getUTCFullYear()
      const m = currentDate.getUTCMonth() + 1
      const dailyBudget = budgetByMonth[`${y}-${m}`] || 0
      dailyTrendMap[d] = { date: d, Actual: 0, Budget: dailyBudget }
      totalBudgetUsd += dailyBudget
      currentDate.setUTCDate(currentDate.getUTCDate() + 1)
    }
    
    // Fill in the actuals
    ;(stats || []).forEach(s => {
      if (dailyTrendMap[s.stat_date]) {
        dailyTrendMap[s.stat_date].Actual = Number(s.room_revenue_usd)
      } else {
        // If it's somehow out of bounds but returned by the query, add it anyway
        const [y, m] = s.stat_date.split('-')
        const dailyBudget = budgetByMonth[`${y}-${Number(m)}`] || 0
        dailyTrendMap[s.stat_date] = { date: s.stat_date, Actual: Number(s.room_revenue_usd), Budget: dailyBudget }
        totalBudgetUsd += dailyBudget
      }
    })
    
    const dailyTrend = Object.values(dailyTrendMap).sort((a, b) => a.date.localeCompare(b.date))
    const totalVarianceUsd = totalRevenue - totalBudgetUsd"""

code = re.sub(old_daily_trend, new_daily_trend, code)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
