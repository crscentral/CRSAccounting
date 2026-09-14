import re
with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# 1. Update KpiCard for Net Profit
code = code.replace(
    """<KpiCard label="Net Profit" value={cp.fmt(netProfit)} sublabel="billed minus expenses" icon={DollarSign} tone="blue" />""",
    """<KpiCard label="Net Profit" value={cp.fmt(netProfit)} sublabel="billed minus expenses" icon={DollarSign} tone={netProfit >= 0 ? 'green' : 'red'} />"""
)

# 2. Update OverviewCard props in rendering
new_overview_cards = """      <div className="grid lg:grid-cols-3 gap-5 mb-6">
        <OverviewCard title="Company Overview - YTD" subtitle={`${activeCompany.name} • Amounts in ${cp.displayCurrency}`}
          revenue={cp.fmt(ytdRevenue)} expenses={cp.fmt(ytdExpenses)} profit={cp.fmt(ytdRevenue - ytdExpenses)} profitValue={ytdRevenue - ytdExpenses}
          revenueLabel="YTD Revenue" expensesLabel="YTD Expenses" profitLabel="YTD Net Profit" />
        <OverviewCard title="Company Overview - All Time" subtitle={`${activeCompany.name} • Amounts in ${cp.displayCurrency}`}
          revenue={cp.fmt(allTimeRevenue)} expenses={cp.fmt(allTimeExpenses)} profit={cp.fmt(allTimeRevenue - allTimeExpenses)} profitValue={allTimeRevenue - allTimeExpenses}
          revenueLabel="All Time Revenue" expensesLabel="All Time Expenses" profitLabel="All Time Net Profit" />"""

code = re.sub(
    r"      <div className=\"grid lg:grid-cols-3 gap-5 mb-6\">\n        <OverviewCard title=\"Company Overview - YTD\" subtitle=\{\`\$\{activeCompany\.name\} • Amounts in \$\{cp\.displayCurrency\}\`\}\n          revenue=\{cp\.fmt\(ytdRevenue\)\} expenses=\{cp\.fmt\(ytdExpenses\)\} profit=\{cp\.fmt\(ytdRevenue - ytdExpenses\)\}\n          revenueLabel=\"YTD Revenue\" expensesLabel=\"YTD Expenses\" profitLabel=\"YTD Net Profit\" />\n        <OverviewCard title=\"Company Overview - All Time\" subtitle=\{\`\$\{activeCompany\.name\} • Amounts in \$\{cp\.displayCurrency\}\`\}\n          revenue=\{cp\.fmt\(allTimeRevenue\)\} expenses=\{cp\.fmt\(allTimeExpenses\)\} profit=\{cp\.fmt\(allTimeRevenue - allTimeExpenses\)\}\n          revenueLabel=\"All Time Revenue\" expensesLabel=\"All Time Expenses\" profitLabel=\"All Time Net Profit\" />",
    new_overview_cards,
    code,
    flags=re.DOTALL
)

# 3. Update OverviewCard component
old_comp = """function OverviewCard({ title, subtitle, revenue, expenses, profit, revenueLabel, expensesLabel, profitLabel }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5">
      <h3 className="font-semibold text-slate-700 flex items-center gap-2"><Building2 size={16} /> {title}</h3>
      <p className="text-xs text-slate-400 mb-3">{subtitle}</p>
      <div className="space-y-2">
        <div className="flex items-center justify-between bg-emerald-50 rounded-lg px-3 py-2">
          <span className="text-sm text-emerald-700 flex items-center gap-1"><TrendingUp size={14} /> {revenueLabel}</span>
          <span className="font-bold text-slate-800">{revenue}</span>
        </div>
        <div className="flex items-center justify-between bg-rose-50 rounded-lg px-3 py-2">
          <span className="text-sm text-rose-700 flex items-center gap-1"><TrendingDown size={14} /> {expensesLabel}</span>
          <span className="font-bold text-slate-800">{expenses}</span>
        </div>
        <div className="flex items-center justify-between bg-blue-50 rounded-lg px-3 py-2">
          <span className="text-sm text-blue-700 flex items-center gap-1"><DollarSign size={14} /> {profitLabel}</span>
          <span className="font-bold text-slate-800">{profit}</span>
        </div>
      </div>
    </div>
  )
}"""

new_comp = """function OverviewCard({ title, subtitle, revenue, expenses, profit, profitValue = 0, revenueLabel, expensesLabel, profitLabel }) {
  const isPositive = profitValue >= 0
  const pBg = isPositive ? 'bg-emerald-50' : 'bg-red-50'
  const pText = isPositive ? 'text-emerald-700' : 'text-red-700'
  
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5">
      <h3 className="font-semibold text-slate-700 flex items-center gap-2"><Building2 size={16} /> {title}</h3>
      <p className="text-xs text-slate-400 mb-3">{subtitle}</p>
      <div className="space-y-2">
        <div className="flex items-center justify-between bg-emerald-50 rounded-lg px-3 py-2">
          <span className="text-sm text-emerald-700 flex items-center gap-1"><TrendingUp size={14} /> {revenueLabel}</span>
          <span className="font-bold text-slate-800">{revenue}</span>
        </div>
        <div className="flex items-center justify-between bg-rose-50 rounded-lg px-3 py-2">
          <span className="text-sm text-rose-700 flex items-center gap-1"><TrendingDown size={14} /> {expensesLabel}</span>
          <span className="font-bold text-slate-800">{expenses}</span>
        </div>
        <div className={`flex items-center justify-between ${pBg} rounded-lg px-3 py-2`}>
          <span className={`text-sm ${pText} flex items-center gap-1`}><DollarSign size={14} /> {profitLabel}</span>
          <span className="font-bold text-slate-800">{profit}</span>
        </div>
      </div>
    </div>
  )
}"""

code = code.replace(old_comp, new_comp)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
