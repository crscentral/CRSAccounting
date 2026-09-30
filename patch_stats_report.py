import re

with open('src/pages/HotelOccupancyStats.jsx', 'r') as f:
    content = f.read()

# I will insert generateStatsReport right before `const totalOccupied = ...`
report_func = """
  async function generateStatsReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    const reportView = selections.view || view
    const reportRange = rangeFor(reportView)

    const { data: statRows } = await supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', reportRange.from).lte('stat_date', reportRange.to).order('stat_date')
    const rows = statRows || []
    const sections = [{
      heading: `Occupancy & Revenue Statistics — ${VIEWS.find(v => v.key === reportView)?.label}`,
      columns: ['Date', 'Rooms Occupied', 'Occupancy %', 'ADR', 'RevPAR', 'Room Revenue', 'Collected'],
      rows: rows.map(r => {
        const occPct = totalRooms > 0 ? ((r.rooms_occupied / totalRooms) * 100).toFixed(1) + '%' : '—'
        const adr = r.rooms_occupied > 0 ? f(r.room_revenue_usd / r.rooms_occupied) : '—'
        const revpar = totalRooms > 0 ? f(r.room_revenue_usd / totalRooms) : '—'
        return [r.stat_date, r.rooms_occupied, occPct, adr, revpar, f(r.room_revenue_usd), f(r.room_revenue_collected_usd)]
      }),
    }]

    const title = 'Hotel Revenue & Occupancy Statistics'
    const subtitle = `${activeCompany.name} • ${reportRange.from} to ${reportRange.to} • ${selections.currency}`
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'hotel_occupancy_stats' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'hotel_occupancy_stats' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'hotel_occupancy_stats' })
  }

  if (!activeCompany) return null

  const totalOccupied = stats.reduce((s, r) => s + r.rooms_occupied, 0)"""

content = content.replace("  const totalOccupied = stats.reduce((s, r) => s + r.rooms_occupied, 0)", report_func)

with open('src/pages/HotelOccupancyStats.jsx', 'w') as f:
    f.write(content)
