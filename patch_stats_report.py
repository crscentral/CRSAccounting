import re

with open('src/pages/HotelOccupancyStats.jsx', 'r') as f:
    code = f.read()

old_gen = """    // If the modal selected a different view, we should theoretically re-fetch, but 
    // for simplicity, let's trigger a view change if it doesn't match and warn, OR
    // just use the current data since the page state drives the data.
    // To properly support it, we'd need to await loadData for that view.
    // For now, if selections.view !== view, we'll just alert that they should change it on the page first, or we can just fetch it!
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)

    const { data: statRows } = await supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to).order('stat_date')
    const rows = statRows || []
    const sections = [{
      heading: `Occupancy & Revenue Statistics — ${VIEWS.find(v => v.key === view)?.label}`,"""

new_gen = """    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    const reportView = selections.view || view
    const reportRange = rangeFor(reportView)

    const { data: statRows } = await supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', reportRange.from).lte('stat_date', reportRange.to).order('stat_date')
    const rows = statRows || []
    const sections = [{
      heading: `Occupancy & Revenue Statistics — ${VIEWS.find(v => v.key === reportView)?.label}`,"""
code = code.replace(old_gen, new_gen)

old_range = "const range = rangeFor(view)"
code = code.replace(old_range, "")

old_subtitle = "const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`"
new_subtitle = "const subtitle = `${activeCompany.name} • ${reportRange.from} to ${reportRange.to} • ${selections.currency}`"
code = code.replace(old_subtitle, new_subtitle)

with open('src/pages/HotelOccupancyStats.jsx', 'w') as f:
    f.write(code)
