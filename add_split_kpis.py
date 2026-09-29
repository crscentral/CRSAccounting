with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

anchor_calc = "const totalExpenses = entriesTotalUsd + amcTotalForView + piTotalUsd"
new_calc = """const totalExpenses = entriesTotalUsd + amcTotalForView + piTotalUsd

  const hotelAmcMonthlyUsd = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0)
  const hotelAmcForView = hotelAmcMonthlyUsd * monthsInView
  const hotelPiTotal = hotelPI.reduce((s, r) => s + Number(r.amount_usd), 0)
  const totalHotelExpenses = hotelEntriesTotal + hotelAmcForView + hotelPiTotal

  const restAmcMonthlyUsd = restAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0)
  const restAmcForView = restAmcMonthlyUsd * monthsInView
  const restPiTotal = restPI.reduce((s, r) => s + Number(r.amount_usd), 0)
  const totalRestExpenses = restEntriesTotal + restAmcForView + restPiTotal
"""

content = content.replace(anchor_calc, new_calc)

anchor_kpi = """      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-3">
        <KpiCard label="Total Expenses" value={cp.fmt(totalExpenses)} tone="red" />
        {topHeads.map(([name, usd]) => <KpiCard key={name} label={name} value={cp.fmt(usd)} tone="slate" />)}
      </div>"""

# Wait, let me check what the KPI grid actually looks like.
