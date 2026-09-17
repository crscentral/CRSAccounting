import re

with open('src/pages/HotelOccupancyStats.jsx', 'r') as f:
    code = f.read()

old_gen = """  async function generateStatsReport(selections, format) {
    
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)

    const { data: statRows } = await supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to).order('stat_date')
    const rows = statRows || []
    const sections = [{
      heading: `Occupancy & Revenue Statistics — ${VIEWS.find(v => v.key === view)?.label}`,"""

new_gen = """  async function generateStatsReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    const reportView = selections.view || view
    const reportRange = rangeFor(reportView)

    const { data: statRows } = await supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', reportRange.from).lte('stat_date', reportRange.to).order('stat_date')
    const rows = statRows || []
    const sections = [{
      heading: `Occupancy & Revenue Statistics — ${VIEWS.find(v => v.key === reportView)?.label}`,"""

code = code.replace(old_gen, new_gen)

with open('src/pages/HotelOccupancyStats.jsx', 'w') as f:
    f.write(code)
