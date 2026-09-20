import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

# Fix rounding in ForecastRow
content = content.replace(
    "const [revenue, setRevenue] = useState(row.revenue_usd)",
    "const [revenue, setRevenue] = useState(Math.round(row.revenue_usd || 0))"
)
content = content.replace(
    "const [exp, setExp] = useState(row.expenses_usd)",
    "const [exp, setExp] = useState(Math.round(row.expenses_usd || 0))"
)
content = content.replace(
    "useEffect(() => { setRevenue(row.revenue_usd); setExp(row.expenses_usd) }, [row])",
    "useEffect(() => { setRevenue(Math.round(row.revenue_usd || 0)); setExp(Math.round(row.expenses_usd || 0)) }, [row])"
)

# Also ensure the overwrite only happens if there is NO manual entry, OR if we strictly want it to travel, let's keep the overwrite logic I just added (revMap[m] > 0). Actually, if they want a manual forecast, they can just update the budget! Let's just leave the overwrite logic since they complained it wasn't travelling.

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
