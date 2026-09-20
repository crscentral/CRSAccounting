import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

# 1. State for restRevenue
content = content.replace(
    "const [totalRooms, setTotalRooms] = useState(0)",
    "const [totalRooms, setTotalRooms] = useState(0)\n  const [restRevenue, setRestRevenue] = useState([])"
)

# 2. Update loadAll()
old_promise = """    const [{ data: room }, { data: anc }, { data: accs }, { data: settings }] = await Promise.all([
      supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to).order('stat_date', { ascending: false }),
      supabase.from('hotel_revenue_entries').select('*, account:accounts(code, name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to).order('entry_date', { ascending: false }),
      supabase.from('accounts').select('id, code, name').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Revenue').neq('code', '4010').order('code'),
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
    ])"""

new_promise = """    const [{ data: room }, { data: anc }, { data: accs }, { data: settings }, { data: restRev }] = await Promise.all([
      supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to).order('stat_date', { ascending: false }),
      supabase.from('hotel_revenue_entries').select('*, account:accounts(code, name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to).order('entry_date', { ascending: false }),
      supabase.from('accounts').select('id, code, name').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Revenue').neq('code', '4010').order('code'),
      supabase.from('hotel_settings').select('total_rooms').eq('company_id', activeCompany.id).eq('product', activeProduct).maybeSingle(),
      activeProduct === 'hotel' ? supabase.from('restaurant_daily_revenue').select('food_amount_usd, beverage_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to) : Promise.resolve({ data: [] })
    ])"""

content = content.replace(old_promise, new_promise)

content = content.replace(
    "setTotalRooms(settings?.total_rooms || 0)",
    "setTotalRooms(settings?.total_rooms || 0)\n    setRestRevenue(restRev || [])"
)

# 3. KPI Calculations
old_calcs = """  const totalRoomRevenue = roomStats.reduce((s, r) => s + Number(r.room_revenue_usd), 0)
  const totalCollected = roomStats.reduce((s, r) => s + Number(r.room_revenue_collected_usd), 0)
  const totalAncillary = ancillary.reduce((s, r) => s + Number(r.amount_usd), 0)"""

new_calcs = """  const totalRoomRevenue = roomStats.reduce((s, r) => s + Number(r.room_revenue_usd), 0)
  const totalCollected = roomStats.reduce((s, r) => s + Number(r.room_revenue_collected_usd), 0)
  const totalAncillary = ancillary.reduce((s, r) => s + Number(r.amount_usd), 0)
  const fbRev = restRevenue.reduce((s, r) => s + (Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0), 0)
  
  const totalRev = totalRoomRevenue + totalAncillary + fbRev
  const totalRevCollected = totalCollected + totalAncillary + fbRev
  const pendingCollection = totalRev - totalRevCollected"""

content = content.replace(old_calcs, new_calcs)

# 4. Grid Render
old_grid = """      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Daily Revenue" value={cp.fmt(totalRoomRevenue + totalAncillary)} tone="slate" />
        <KpiCard label="Room Revenue" value={cp.fmt(totalRoomRevenue)} tone="green" />
        <KpiCard label="Room Rev. Collected" value={cp.fmt(totalCollected)} tone="blue" />
        <KpiCard label="Ancillary Revenue" value={cp.fmt(totalAncillary)} tone="gold" />
      </div>"""

new_grid = """      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Revenue" value={cp.fmt(totalRev)} tone="slate" />
        <KpiCard label="Room Revenue" value={cp.fmt(totalRoomRevenue)} tone="green" />
        <KpiCard label="F&B Revenue" value={cp.fmt(fbRev)} tone="amber" />
        <KpiCard label="Other Revenue" value={cp.fmt(totalAncillary)} tone="gold" />
        <KpiCard label="Rev. Collected" value={cp.fmt(totalRevCollected)} tone="blue" />
        <KpiCard label="Revenue Pending Collection" value={cp.fmt(pendingCollection)} tone="red" />
      </div>"""

content = content.replace(old_grid, new_grid)

# 5. Fix Default Date via useCurrencyAndPeriod
content = content.replace(
    "const cp = useCurrencyAndPeriod()",
    "const cp = useCurrencyAndPeriod('YESTERDAY')"
)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)
