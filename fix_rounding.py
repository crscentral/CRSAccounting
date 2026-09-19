import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

# 1. Round the forecast_revenue_usd and forecast_expenses_usd when overriding
replacement = """
        // ALWAYS override forecast values with the budget values for Hotel product
        entry.forecast_revenue_usd = Math.round(revMap[i] || 0)
        entry.forecast_expenses_usd = Math.round(expMap[i] || 0)
"""

content = re.sub(
    r"// ALWAYS override forecast values with the budget values for Hotel product\n\s*entry\.forecast_revenue_usd = revMap\[i\] \|\| 0\n\s*entry\.forecast_expenses_usd = expMap\[i\] \|\| 0",
    replacement.strip(),
    content
)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
