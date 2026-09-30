import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# Fix Pace Variance label
content = re.sub(
    r"label=\{isCurrentMonth \? `Pace Variance \(Day \$\{daysElapsed\}/\$\{daysInActiveMonth\}\)` : `\$\{MONTH_NAMES\[activeMonth - 1\]\} Variance`\}",
    'label="Variance"',
    content
)

# Fix bottom KPI boxes
kpi_target = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} Total Budget`} value={fmt(revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev)} icon={TrendingUp} tone="indigo" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} ${activeProduct === "restaurant" ? "Food Sales Budget" : "FO Revenue Budget"}`} value={fmt(revenueSummary.frontOffice)} icon={TrendingUp} tone="gold" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} ${activeProduct === "restaurant" ? "Beverage Sales Budget" : "F&B Service Budget"}`} value={fmt(revenueSummary.fbService)} icon={TrendingUp} tone="blue" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} Other Revenue Budget`} value={fmt(revenueSummary.otherRev)} icon={TrendingUp} tone="emerald" />
      </div>"""

kpi_replace = """      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4 mb-6">
        <KpiCard label="YTD Actual Revenue" value={fmt(grandTotalRevenueActual)} icon={TrendingUp} tone="green" />
        <KpiCard label="YTD Total Budget" value={fmt(revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev)} icon={TrendingUp} tone="indigo" />
        <KpiCard label="YTD Variance" value={fmt(grandTotalRevenueActual - (revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev))} icon={grandTotalRevenueActual >= (revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev) ? TrendingUp : AlertTriangle} tone={grandTotalRevenueActual >= (revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev) ? 'green' : 'red'} />
        <KpiCard label={activeProduct === "restaurant" ? "YTD Food Sales Budget" : "YTD FO Revenue Budget"} value={fmt(revenueSummary.frontOffice)} icon={TrendingUp} tone="gold" />
        <KpiCard label={activeProduct === "restaurant" ? "YTD Beverage Sales Budget" : "YTD F&B Service Budget"} value={fmt(revenueSummary.fbService)} icon={TrendingUp} tone="blue" />
        <KpiCard label="YTD Other Revenue Budget" value={fmt(revenueSummary.otherRev)} icon={TrendingUp} tone="emerald" />
      </div>"""

content = content.replace(kpi_target, kpi_replace)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
