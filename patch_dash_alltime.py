import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

# 1. Add states
content = content.replace("  const [allPurchases, setAllPurchases] = useState([])",
                          "  const [allPurchases, setAllPurchases] = useState([])\n  const [allHotelRoomStats, setAllHotelRoomStats] = useState([])\n  const [allHotelGuestInvoices, setAllHotelGuestInvoices] = useState([])\n  const [allHotelExpenseEntries, setAllHotelExpenseEntries] = useState([])\n  const [allHotelRevenueEntries, setAllHotelRevenueEntries] = useState([])\n  const [allRestaurantRevenue, setAllRestaurantRevenue] = useState([])")

# 2. Add queries to Promise.all
# We are currently fetching 13 queries. Let's add 5 more.
# Wait, it's safer to just run a separate Promise.all for the "all time" hotel data to avoid index confusion.
old_loadData = """    const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }, { data: accs }, { data: led }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }, { data: rdr }] = await Promise.all(["""

new_loadData = """    const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }, { data: accs }, { data: led }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }, { data: rdr }] = await Promise.all([
      supabase.from('sales_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('purchase_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
      supabase.from('sales_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('purchase_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('accounts').select('id, type, name').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to) : Promise.resolve({ data: [] })
    ])

    let allHrs = [], allHgi = [], allHee = [], allHre = [], allRdr = [];
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      const [{ data: aHrs }, { data: aHgi }, { data: aHee }, { data: aHre }, { data: aRdr }] = await Promise.all([
        supabase.from('hotel_room_stats').select('stat_date, room_revenue_usd, manual_room_revenue_collected_usd, invoiced_room_revenue_collected').eq('company_id', activeCompany.id).eq('product', activeProduct),
        supabase.from('hotel_guest_invoices').select('invoice_date, invoice_amount_usd, collected_amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct),
        supabase.from('hotel_expense_entries').select('expense_date, amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct),
        supabase.from('hotel_revenue_entries').select('entry_date, amount_usd, collected_usd').eq('company_id', activeCompany.id).eq('product', activeProduct),
        supabase.from('restaurant_daily_revenue').select('revenue_date, total_amount_usd, food_amount_usd, beverage_amount_usd, other_amount_usd, collected_usd').eq('company_id', activeCompany.id).eq('product', activeProduct)
      ])
      allHrs = aHrs || []
      allHgi = aHgi || []
      allHee = aHee || []
      allHre = aHre || []
      allRdr = aRdr || []
    }
    setAllHotelRoomStats(allHrs)
    setAllHotelGuestInvoices(allHgi)
    setAllHotelExpenseEntries(allHee)
    setAllHotelRevenueEntries(allHre)
    setAllRestaurantRevenue(allRdr)"""

# Instead of blindly replacing the loadData array which might be slightly different in whitespace, let's just use regex.
content = re.sub(
    r"(const \[\{ data: s \}, .*?\] = await Promise\.all\(\[[\s\S]*?\]\))",
    new_loadData,
    content
)

# Replace the setter blocks inside loadData
setter_old = """    setAccounts(accs || [])
    setLedgerEntries(led || [])
    setHotelRoomStats(hrs || [])
    setHotelGuestInvoices(hgi || [])
    setHotelExpenseEntries(hee || [])
    setHotelAmc(hamc || [])
    setHotelRevenueEntries(hre || [])
    setRestaurantRevenue(rdr || [])
    setSales(s || [])
    setPurchases(p || [])
    setReceipts(r || [])
    setAllSales(allS || [])
    setAllPurchases(allP || [])"""

# it's already perfectly matched.

# 3. Update the monthlyMap logic and YTD/All-Time logic
# We need to calculate ALL-TIME stats accurately.
logic_old = """  if (['hotel', 'restaurant'].includes(activeProduct)) {
    allTimeRevenue = totalBilled
    allTimeExpenses = totalExpenses
    
    hotelGuestInvoices.forEach(i => {
      const key = i.invoice_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Outstanding += (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd))
      monthlyMap[key].Collected += Number(i.collected_amount_usd)
    })
    hotelRoomStats.forEach(r => {
      const key = r.stat_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(r.room_revenue_usd)
      monthlyMap[key].Collected += Number(r.manual_room_revenue_collected_usd || 0)
    })
    hotelRevenueEntries.forEach(r => {
      const key = r.entry_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(r.amount_usd)
      monthlyMap[key].Collected += Number(r.collected_usd || 0)
    })
    hotelExpenseEntries.forEach(e => {
      const key = e.expense_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Expenses += Number(e.amount_usd)
    })
    restaurantRevenue.forEach(r => {
      const key = r.revenue_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0)))
      monthlyMap[key].Collected += Number(r.collected_usd || 0)
    })
    // For AMC, add 1/12th of annual amount to Expenses for each month that exists in the map
    const monthlyAmc = hotelAmc.reduce((sum, c) => sum + (Number(c.annual_amount_usd) / 12), 0)
    Object.keys(monthlyMap).forEach(k => {
      monthlyMap[k].Expenses += monthlyAmc
    })
  } else {"""

logic_new = """  if (['hotel', 'restaurant'].includes(activeProduct)) {
    // Determine the unique months across ALL hotel data to properly amortize AMC
    const uniqueMonths = new Set()
    
    allHotelGuestInvoices.forEach(i => {
      const key = i.invoice_date.slice(0, 7)
      uniqueMonths.add(key)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Outstanding += (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd))
      monthlyMap[key].Collected += Number(i.collected_amount_usd)
    })
    allHotelRoomStats.forEach(r => {
      const key = r.stat_date.slice(0, 7)
      uniqueMonths.add(key)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(r.room_revenue_usd)
      monthlyMap[key].Collected += Number(r.manual_room_revenue_collected_usd || 0)
    })
    allHotelRevenueEntries.forEach(r => {
      const key = r.entry_date.slice(0, 7)
      uniqueMonths.add(key)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(r.amount_usd)
      monthlyMap[key].Collected += Number(r.collected_usd || 0)
    })
    allHotelExpenseEntries.forEach(e => {
      const key = e.expense_date.slice(0, 7)
      uniqueMonths.add(key)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Expenses += Number(e.amount_usd)
    })
    allRestaurantRevenue.forEach(r => {
      const key = r.revenue_date.slice(0, 7)
      uniqueMonths.add(key)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0)))
      monthlyMap[key].Collected += Number(r.collected_usd || 0)
    })
    // For AMC, add 1/12th of annual amount to Expenses for each month that exists in the map
    const monthlyAmc = hotelAmc.reduce((sum, c) => sum + (Number(c.annual_amount_usd) / 12), 0)
    Object.keys(monthlyMap).forEach(k => {
      monthlyMap[k].Expenses += monthlyAmc
    })
    
    // Now calculate allTimeRevenue and allTimeExpenses accurately
    allTimeRevenue = Object.values(monthlyMap).reduce((s, m) => s + m.Revenue, 0)
    allTimeExpenses = Object.values(monthlyMap).reduce((s, m) => s + m.Expenses, 0)
  } else {"""

content = content.replace(logic_old, logic_new)

ytd_old = """  if (['hotel', 'restaurant'].includes(activeProduct)) {
    ytdRevenue = totalBilled
    ytdExpenses = totalExpenses
  } else {"""

ytd_new = """  if (['hotel', 'restaurant'].includes(activeProduct)) {
    // Use monthlyMap to derive YTD for Hotel
    ytdRevenue = Object.values(monthlyMap).filter(m => {
      const [y, mo] = m.month.split('-')
      const d = new Date(Number(y), Number(mo)-1, 15).toISOString().split('T')[0]
      return d >= ytdRange.from && d <= ytdRange.to
    }).reduce((s, m) => s + m.Revenue, 0)
    
    ytdExpenses = Object.values(monthlyMap).filter(m => {
      const [y, mo] = m.month.split('-')
      const d = new Date(Number(y), Number(mo)-1, 15).toISOString().split('T')[0]
      return d >= ytdRange.from && d <= ytdRange.to
    }).reduce((s, m) => s + m.Expenses, 0)
  } else {"""

content = content.replace(ytd_old, ytd_new)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)

