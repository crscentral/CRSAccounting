with open('src/pages/RestaurantRevenue.jsx', 'r') as f:
    content = f.read()

old_kpis = """  const totalRevenue = entries.reduce((s, e) => s + Number(e.amount_usd), 0)
  const totalCovers = entries.reduce((s, e) => s + Number(e.covers), 0)
  const avgPerCover = totalCovers > 0 ? totalRevenue / totalCovers : 0

  const dailyMap = {}"""

new_kpis = """  const totalRevenue = entries.reduce((s, e) => s + Number(e.amount_usd), 0)
  const totalCovers = entries.reduce((s, e) => s + Number(e.covers), 0)
  const avgPerCover = totalCovers > 0 ? totalRevenue / totalCovers : 0
  const totalFood = entries.reduce((s, e) => s + Number(e.food_amount_usd), 0)
  const totalBeverage = entries.reduce((s, e) => s + Number(e.beverage_amount_usd), 0)
  const totalOther = entries.reduce((s, e) => s + Number(e.other_amount_usd), 0)

  const dailyMap = {}"""

content = content.replace(old_kpis, new_kpis)

old_grid = """      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <KpiCard label="Total Revenue" value={cp.fmt(totalRevenue)} icon={DollarSign} tone="green" />
        <KpiCard label="Total Covers" value={totalCovers} icon={Users} tone="blue" />
        <KpiCard label="Avg Revenue / Cover" value={cp.fmt(avgPerCover)} icon={TrendingUp} tone="gold" />
      </div>"""

new_grid = """      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <KpiCard label="Total Revenue" value={cp.fmt(totalRevenue)} icon={DollarSign} tone="green" />
        <KpiCard label="Total Covers" value={totalCovers} icon={Users} tone="blue" />
        <KpiCard label="Avg Revenue / Cover" value={cp.fmt(avgPerCover)} icon={TrendingUp} tone="gold" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <KpiCard label="Total Food Revenue" value={cp.fmt(totalFood)} icon={TrendingUp} tone="emerald" />
        <KpiCard label="Total Beverage Revenue" value={cp.fmt(totalBeverage)} icon={TrendingUp} tone="indigo" />
        <KpiCard label="Total Other Revenue" value={cp.fmt(totalOther)} icon={TrendingUp} tone="slate" />
      </div>"""

content = content.replace(old_grid, new_grid)

with open('src/pages/RestaurantRevenue.jsx', 'w') as f:
    f.write(content)

# Bump sw.js
with open('public/sw.js', 'r') as f:
    sw = f.read()
sw = sw.replace('v115', 'v116')
with open('public/sw.js', 'w') as f:
    f.write(sw)
