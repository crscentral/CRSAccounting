import re

# 1. Update AppShell.jsx
with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

content = content.replace("'F&B Revenue Budget'", "'Revenue Budget'")
content = content.replace("'F&B Expense Budget'", "'Expense Budget'")

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)

# 2. Update HotelBudget.jsx
with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# Make Total Budget the first widget
old_grid = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} ${activeProduct === "restaurant" ? "Food Sales Budget" : "FO Revenue Budget"}`} value={fmt(revenueSummary.frontOffice)} icon={TrendingUp} tone="gold" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} ${activeProduct === "restaurant" ? "Beverage Sales Budget" : "F&B Service Budget"}`} value={fmt(revenueSummary.fbService)} icon={TrendingUp} tone="blue" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} Other Revenue Budget`} value={fmt(revenueSummary.otherRev)} icon={TrendingUp} tone="emerald" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} Total Budget`} value={fmt(revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev)} icon={TrendingUp} tone="indigo" />
      </div>"""

new_grid = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} Total Budget`} value={fmt(revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev)} icon={TrendingUp} tone="indigo" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} ${activeProduct === "restaurant" ? "Food Sales Budget" : "FO Revenue Budget"}`} value={fmt(revenueSummary.frontOffice)} icon={TrendingUp} tone="gold" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} ${activeProduct === "restaurant" ? "Beverage Sales Budget" : "F&B Service Budget"}`} value={fmt(revenueSummary.fbService)} icon={TrendingUp} tone="blue" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} Other Revenue Budget`} value={fmt(revenueSummary.otherRev)} icon={TrendingUp} tone="emerald" />
      </div>"""

content = content.replace(old_grid, new_grid)

# Rename title to "Revenue Budget" when restaurant
content = content.replace('activeProduct === "restaurant" ? "F&B Revenue Budget"', 'activeProduct === "restaurant" ? "Revenue Budget"')

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)

# 3. Update HotelExpenseBudget.jsx
with open('src/pages/HotelExpenseBudget.jsx', 'r') as f:
    content = f.read()

# Make Total Budget the first widget
old_grid_exp = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} FO Budget`} value={fmt(monthlySummary.foBudget)} icon={TrendingUp} tone="gold" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} F&B Budget`} value={fmt(monthlySummary.fbBudget)} icon={TrendingUp} tone="blue" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} Other Budget`} value={fmt(monthlySummary.otherBudget)} icon={TrendingUp} tone="emerald" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} Total Budget`} value={fmt(monthlySummary.totalBudget)} icon={TrendingUp} tone="indigo" />
      </div>"""

new_grid_exp = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} Total Budget`} value={fmt(monthlySummary.totalBudget)} icon={TrendingUp} tone="indigo" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} FO Budget`} value={fmt(monthlySummary.foBudget)} icon={TrendingUp} tone="gold" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} F&B Budget`} value={fmt(monthlySummary.fbBudget)} icon={TrendingUp} tone="blue" />
        <KpiCard label={`${selectedMonth === 'all' ? selectedYear : MONTH_NAMES[Number(selectedMonth)-1] + ' ' + selectedYear} Other Budget`} value={fmt(monthlySummary.otherBudget)} icon={TrendingUp} tone="emerald" />
      </div>"""

content = content.replace(old_grid_exp, new_grid_exp)

# Rename title to "Expense Budget" when restaurant
content = content.replace('activeProduct === "restaurant" ? "F&B Expense Budget"', 'activeProduct === "restaurant" ? "Expense Budget"')

with open('src/pages/HotelExpenseBudget.jsx', 'w') as f:
    f.write(content)

# Bump sw.js
with open('public/sw.js', 'r') as f:
    sw = f.read()
sw = sw.replace('v113', 'v114')
with open('public/sw.js', 'w') as f:
    f.write(sw)
