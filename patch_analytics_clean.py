import re

with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

# 1. Update loadData in Analytics.jsx
old_loadData = """  async function loadData() {
    const [{ data: s }, { data: p }, { data: r }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }] = await Promise.all([
      supabase.from('sales_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to) : Promise.resolve({ data: [] }),
    ])
    setSales(s || []); setPurchases(p || []); setReceipts(r || [])
    setHotelRoomStats(hrs || [])
    setHotelGuestInvoices(hgi || [])
    setHotelExpenseEntries(hee || [])
    setHotelAmc(hamc || [])
    setHotelRevenueEntries(hre || [])
  }"""
new_loadData = """  const [restaurantRevenue, setRestaurantRevenue] = useState([])

  async function loadData() {
    const [{ data: s }, { data: p }, { data: r }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }, { data: rdr }] = await Promise.all([
      supabase.from('sales_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to) : Promise.resolve({ data: [] })
    ])
    setSales(s || []); setPurchases(p || []); setReceipts(r || [])
    setHotelRoomStats(hrs || [])
    setHotelGuestInvoices(hgi || [])
    setHotelExpenseEntries(hee || [])
    setHotelAmc(hamc || [])
    setHotelRevenueEntries(hre || [])
    setRestaurantRevenue(rdr || [])
  }"""
content = content.replace(old_loadData, new_loadData)

# 2. Add restaurantRevenue to the calculation
old_calc = """    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0)

    totalInvoiced = manualRoomRevenue + guestInvoiceRevenue + ancillaryCollected
    collected = manualRoomCollected + guestInvoiceCollected + ancillaryCollected"""

new_calc = """    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.collected_usd || r.amount_usd || 0), 0)
    const ancillaryRevenue = hotelRevenueEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0)
    
    const restRevRevenue = restaurantRevenue.reduce((s, r) => s + (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))), 0)
    const restRevCollected = restaurantRevenue.reduce((s, r) => s + Number(r.collected_usd || 0), 0)

    totalInvoiced = manualRoomRevenue + guestInvoiceRevenue + ancillaryRevenue + restRevRevenue
    collected = manualRoomCollected + guestInvoiceCollected + ancillaryCollected + restRevCollected"""
content = content.replace(old_calc, new_calc)

# 3. Add to monthlyMap
old_monthly = """    hotelRevenueEntries.forEach(i => {
      const key = i.entry_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(i.amount_usd)
      monthlyMap[key].Collected += Number(i.amount_usd)
    })"""
new_monthly = """    hotelRevenueEntries.forEach(i => {
      const key = i.entry_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(i.amount_usd)
      monthlyMap[key].Collected += Number(i.collected_usd || i.amount_usd || 0)
    })
    restaurantRevenue.forEach(i => {
      const key = i.revenue_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      const total = Number(i.total_amount_usd) || (Number(i.food_amount_usd||0) + Number(i.beverage_amount_usd||0) + Number(i.other_amount_usd||0))
      monthlyMap[key].Revenue += total
      monthlyMap[key].Collected += Number(i.collected_usd || 0)
    })"""
content = content.replace(old_monthly, new_monthly)

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(content)
