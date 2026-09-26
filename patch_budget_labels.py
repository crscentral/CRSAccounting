import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

old_kpis = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} ${activeProduct === "restaurant" ? "Food Sales Budget" : "FO Revenue Budget"}`} value={fmt(revenueSummary.frontOffice)} icon={TrendingUp} tone="gold" sublabel={activeProduct === "restaurant" ? "Food Sales Account" : "Room Revenue + FO Accounts"} />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} ${activeProduct === "restaurant" ? "Beverage Sales Budget" : "F&B Service Budget"}`} value={fmt(revenueSummary.fbService)} icon={TrendingUp} tone="blue" sublabel={activeProduct === "restaurant" ? "Beverage Sales Account" : "F&B Service Accounts"} />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} Other Revenue Budget`} value={fmt(revenueSummary.otherRev)} icon={TrendingUp} tone="emerald" sublabel="Other Operating Income" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} Total Budget`} value={fmt(revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev)} icon={TrendingUp} tone="indigo" sublabel="Combined Total Budget" />
      </div>"""

new_kpis = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} ${activeProduct === "restaurant" ? "Food Sales Budget" : "FO Revenue Budget"}`} value={fmt(revenueSummary.frontOffice)} icon={TrendingUp} tone="gold" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} ${activeProduct === "restaurant" ? "Beverage Sales Budget" : "F&B Service Budget"}`} value={fmt(revenueSummary.fbService)} icon={TrendingUp} tone="blue" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} Other Revenue Budget`} value={fmt(revenueSummary.otherRev)} icon={TrendingUp} tone="emerald" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} Total Budget`} value={fmt(revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev)} icon={TrendingUp} tone="indigo" />
      </div>"""

content = content.replace(old_kpis, new_kpis)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)

