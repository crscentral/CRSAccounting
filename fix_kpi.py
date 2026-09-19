with open('src/pages/HotelExpenseBudget.jsx', 'r') as f:
    code = f.read()

code = code.replace(
    '<KpiCard label={`${startYear} Budget`} amount={fmt(thisYearBudget)} icon={<TrendingUp size={20} className="text-emerald-600" />} />',
    '<KpiCard label={`${startYear} Budget`} value={fmt(thisYearBudget)} icon={TrendingUp} tone="gold" />'
)

code = code.replace(
    '<KpiCard label={`${startYear} Actual`} amount={fmt(thisYearActual)} icon={<TrendingUp size={20} className="text-emerald-600" />} />',
    '<KpiCard label={`${startYear} Actual`} value={fmt(thisYearActual)} icon={TrendingUp} tone="green" />'
)

code = code.replace(
    '<KpiCard label={`${startYear} Variance`} amount={fmt(thisYearVar)} amountColor={thisYearVar > 0 ? \'text-red-600\' : \'text-emerald-600\'} icon={<AlertTriangle size={20} className="text-rose-500" />} />',
    '<KpiCard label={`${startYear} Variance`} value={fmt(thisYearVar)} icon={AlertTriangle} tone={thisYearVar > 0 ? "red" : "green"} />'
)

with open('src/pages/HotelExpenseBudget.jsx', 'w') as f:
    f.write(code)
