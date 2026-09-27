import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "const revenue = activeProduct === 'hotel' ? revenueByAccount.reduce((s, a) => s + a.amount, 0) : sales.reduce((s, i) => s + Number(i.amount_usd), 0)",
    "const revenue = ['hotel', 'restaurant'].includes(activeProduct) ? revenueByAccount.reduce((s, a) => s + a.amount, 0) : sales.reduce((s, i) => s + Number(i.amount_usd), 0)"
)
content = content.replace(
    "const expenses = activeProduct === 'hotel' ? expensesByAccount.reduce((s, a) => s + a.amount, 0) : purchases.reduce((s, i) => s + Number(i.amount_usd), 0)",
    "const expenses = ['hotel', 'restaurant'].includes(activeProduct) ? expensesByAccount.reduce((s, a) => s + a.amount, 0) : purchases.reduce((s, i) => s + Number(i.amount_usd), 0)"
)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
