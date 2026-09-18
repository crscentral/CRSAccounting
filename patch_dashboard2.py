import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Fix the destructured Promise.all
old_promise = r"const \[\{ data: s \}, \{ data: p \}, \{ data: r \}, \{ data: allS \}, \{ data: allP \}, \{ data: accs \}, \{ data: led \}, \{ data: hrs \}, \{ data: hgi \}, \{ data: hee \}, \{ data: hamc \}\] = await Promise.all\(\["
new_promise = "const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }, { data: accs }, { data: led }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }] = await Promise.all(["
code = code.replace(old_promise, new_promise)

# Add the fetch
old_fetch = r"activeProduct === 'hotel' \? supabase.from\('hotel_amc_contracts'\).select\('\*'\).eq\('company_id', activeCompany.id\).eq\('product', activeProduct\) : Promise.resolve\(\{ data: \[\] \}\),"
new_fetch = """activeProduct === 'hotel' ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to) : Promise.resolve({ data: [] }),"""
code = code.replace(old_fetch, new_fetch)

# Add the state
old_state = r"const \[hotelAmc, setHotelAmc\] = useState\(\[\]\)"
new_state = """const [hotelAmc, setHotelAmc] = useState([])
  const [hotelRevenueEntries, setHotelRevenueEntries] = useState([])"""
code = code.replace(old_state, new_state)

old_set = r"setHotelAmc\(hamc \|\| \[\]\)"
new_set = """setHotelAmc(hamc || [])
    setHotelRevenueEntries(hre || [])"""
code = code.replace(old_set, new_set)

# Fix the `collected` and `monthlyMap` calculation for Hotel
old_calc = r"""    // Outstanding = Unpaid Guest Invoices
    outstanding = hotelGuestInvoices.reduce\(\(s, i\) => s \+ \(Number\(i.invoice_amount_usd\) - Number\(i.collected_amount_usd\)\), 0\)
    
    // Collected = Guest Invoices Paid \+ Daily Room Revenue Collected
    collected = hotelGuestInvoices.reduce\(\(s, i\) => s \+ Number\(i.collected_amount_usd\), 0\) \+ 
                hotelRoomStats.reduce\(\(s, r\) => s \+ Number\(r.room_revenue_collected_usd\), 0\)"""

new_calc = """    // Outstanding = Unpaid Guest Invoices
    outstanding = hotelGuestInvoices.reduce((s, i) => s + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)
    
    // Collected = Manual Room Revenue + Guest Invoices Paid + Ancillary Revenue
    const manualRoomCollected = hotelRoomStats.reduce((s, r) => s + Number(r.manual_room_revenue_collected_usd || 0), 0)
    const guestInvoiceCollected = hotelGuestInvoices.reduce((s, i) => s + Number(i.collected_amount_usd || 0), 0)
    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0)
    collected = manualRoomCollected + guestInvoiceCollected + ancillaryCollected"""
code = code.replace(old_calc, new_calc)

# Fix the pie chart visuals
old_pie1 = r"innerRadius=\{60\} outerRadius=\{80\} label=\{false\}"
new_pie1 = r'innerRadius={40} outerRadius={100} label={({ cx, cy, midAngle, innerRadius, outerRadius, value, name }) => { const RADIAN = Math.PI / 180; const radius = outerRadius + 20; const x = cx + radius * Math.cos(-midAngle * RADIAN); const y = cy + radius * Math.sin(-midAngle * RADIAN); return <text x={x} y={y} fill="#475569" textAnchor={x > cx ? "start" : "end"} dominantBaseline="central" fontSize={11}>{name}: {cp.fmt(value)}</text>; }}'
code = code.replace(old_pie1, new_pie1)

# Oh wait, the second pie chart uses USD formatting in the label! I'll just use the same regex but manually fix it below.

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
