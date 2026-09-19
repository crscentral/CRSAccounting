import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

# 1. Fix Room Revenue to multiply by days in month
content = content.replace(
    "if (budget) budget.forEach(b => revMap[b.budget_month] = (revMap[b.budget_month] || 0) + (b.budgeted_room_revenue_usd || 0))",
    "if (budget) budget.forEach(b => { const days = new Date(forecastYear, b.budget_month, 0).getDate(); revMap[b.budget_month] = (revMap[b.budget_month] || 0) + ((b.budgeted_room_revenue_usd || 0) * days) })"
)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
