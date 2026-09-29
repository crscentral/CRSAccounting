with open('src/pages/RestaurantRevenue.jsx', 'r') as f:
    content = f.read()

old_grid = """      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Revenue" value={cp.fmt(totalRevenue)} icon={DollarSign} tone="green" />
        <KpiCard label="Total Covers" value={totalCovers} icon={Users} tone="blue" />
        <KpiCard label="Avg Revenue / Cover" value={cp.fmt(avgPerCover)} icon={TrendingUp} tone="gold" />
      </div>"""

new_grid = """      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-4">
        <KpiCard label="Total Revenue" value={cp.fmt(totalRevenue)} icon={DollarSign} tone="green" />
        <KpiCard label="Total Covers" value={totalCovers} icon={Users} tone="blue" />
        <KpiCard label="Avg Revenue / Cover" value={cp.fmt(avgPerCover)} icon={TrendingUp} tone="gold" />
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Food Revenue" value={cp.fmt(totalFood)} icon={TrendingUp} tone="emerald" />
        <KpiCard label="Total Beverage Revenue" value={cp.fmt(totalBeverage)} icon={TrendingUp} tone="indigo" />
        <KpiCard label="Total Other Revenue" value={cp.fmt(totalOther)} icon={TrendingUp} tone="slate" />
      </div>"""

content = content.replace(old_grid, new_grid)

with open('src/pages/RestaurantRevenue.jsx', 'w') as f:
    f.write(content)
