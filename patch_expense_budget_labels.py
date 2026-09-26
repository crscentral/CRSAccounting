import re

with open('src/pages/HotelExpenseBudget.jsx', 'r') as f:
    content = f.read()

old_kpis = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} FO Expenses Budget`} value={fmt(monthlySummary.foBudget)} icon={TrendingUp} tone="gold" sublabel="FO Accounts" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} F&B Expenses Budget`} value={fmt(monthlySummary.fbBudget)} icon={TrendingUp} tone="blue" sublabel="F&B Accounts" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} Other Expenses Budget`} value={fmt(monthlySummary.otherBudget)} icon={TrendingUp} tone="emerald" sublabel="Other Expenses" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} Total Budget`} value={fmt(monthlySummary.totalBudget)} icon={TrendingUp} tone="indigo" sublabel="Combined Expenses" />
      </div>"""

new_kpis = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} FO Budget`} value={fmt(monthlySummary.foBudget)} icon={TrendingUp} tone="gold" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} F&B Budget`} value={fmt(monthlySummary.fbBudget)} icon={TrendingUp} tone="blue" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} Other Budget`} value={fmt(monthlySummary.otherBudget)} icon={TrendingUp} tone="emerald" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} Total Budget`} value={fmt(monthlySummary.totalBudget)} icon={TrendingUp} tone="indigo" />
      </div>"""

content = content.replace(old_kpis, new_kpis)

with open('src/pages/HotelExpenseBudget.jsx', 'w') as f:
    f.write(content)

