import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

new_mapping = """
          if (revMap[i] !== undefined) f.revenue_usd = Math.round(revMap[i])
          if (expMap[i] !== undefined) f.expenses_usd = Math.round(expMap[i])
"""

content = re.sub(
    r"if \(revMap\[i\] !== undefined\) f\.revenue_usd = revMap\[i\]\n\s*if \(expMap\[i\] !== undefined\) f\.expenses_usd = expMap\[i\]",
    new_mapping.strip(),
    content
)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
