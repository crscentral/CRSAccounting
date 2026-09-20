import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

# 1. Replace the destructuring and Promise.all completely
old_loadData = """  async function loadData() {
    const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }, { data: accs }, { data: led }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }] = await Promise.all([
      supabase.from('sales_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('purchase_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
      supabase.from('sales_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('purchase_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('accounts').select('id, type, name').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
      activeProduct === 'hotel' ? supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] }),
      supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to),
      supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
      activeProduct === 'restaurant' ? supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to) : Promise.resolve({ data: [] })
    ])
    setAccounts(accs || [])
    setLedgerEntries(led || [])
    setHotelRoomStats(hrs || [])
    setHotelGuestInvoices(hgi || [])
    setHotelExpenseEntries(hee || [])
    setHotelAmc(hamc || [])
    setHotelRevenueEntries(hre || [])
    setSales(s || [])
    setPurchases(p || [])
    setReceipts(r || [])
    setAllSales(allS || [])
    setAllPurchases(allP || [])"""

new_loadData = """  const [restaurantRevenue, setRestaurantRevenue] = useState([])

  async function loadData() {
    const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }, { data: accs }, { data: led }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }, { data: rdr }] = await Promise.all([
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
    setAccounts(accs || [])
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

content = content.replace(old_loadData, new_loadData)


# 2. Fix the if (activeProduct === 'hotel') logic blocks
content = content.replace("if (activeProduct === 'hotel')", "if (['hotel', 'restaurant'].includes(activeProduct))")
content = content.replace("activeProduct === 'hotel' \n    ? hotelGuestInvoices", "['hotel', 'restaurant'].includes(activeProduct) \n    ? hotelGuestInvoices")

# 3. Add restaurantRevenue to the calculation of `totalBilled` and `collected`
old_calc = """    // Collected = Guest Invoices Paid + Daily Room Revenue Collected
    const manualRoomCollected = hotelRoomStats.reduce((s, r) => s + Number(r.manual_room_revenue_collected_usd || 0), 0)
    const guestInvoiceCollected = hotelGuestInvoices.reduce((s, i) => s + Number(i.collected_amount_usd || 0), 0)
    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0)
    collected = manualRoomCollected + guestInvoiceCollected + ancillaryCollected"""

new_calc = """    // Collected = Guest Invoices Paid + Daily Room Revenue Collected
    const manualRoomCollected = hotelRoomStats.reduce((s, r) => s + Number(r.manual_room_revenue_collected_usd || 0), 0)
    const guestInvoiceCollected = hotelGuestInvoices.reduce((s, i) => s + Number(i.collected_amount_usd || 0), 0)
    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.collected_usd || r.amount_usd || 0), 0)
    const restRevCollected = restaurantRevenue.reduce((s, r) => s + Number(r.collected_usd || 0), 0)
    collected = manualRoomCollected + guestInvoiceCollected + ancillaryCollected + restRevCollected
    
    // Add restaurant daily revenue to totalBilled
    const restRevTotal = restaurantRevenue.reduce((s, r) => s + (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))), 0)
    totalBilled += restRevTotal
    
    // Add missing ancillary billing to totalBilled
    const ancillaryTotal = hotelRevenueEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0)
    totalBilled += ancillaryTotal
    
    // Add missing room revenue to totalBilled
    const manualRoomTotal = hotelRoomStats.reduce((s, r) => s + Number(r.manual_room_revenue_usd || 0), 0)
    totalBilled += manualRoomTotal"""
content = content.replace(old_calc, new_calc)

# 4. Inject Restaurant Daily Revenue into All-Time and YTD calculations
# Let's just do it directly. In all-time monthlyMap, add restaurant_daily_revenue
old_all_time = """    hotelRevenueEntries.forEach(r => {
      const key = r.entry_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(r.amount_usd)
      monthlyMap[key].Collected += Number(r.amount_usd)
    })"""
new_all_time = """    hotelRevenueEntries.forEach(r => {
      const key = r.entry_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(r.amount_usd)
      monthlyMap[key].Collected += Number(r.collected_usd || r.amount_usd || 0)
      monthlyMap[key].Outstanding += (Number(r.amount_usd) - Number(r.collected_usd || r.amount_usd || 0))
    })
    restaurantRevenue.forEach(r => {
      const key = r.revenue_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      const total = Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))
      monthlyMap[key].Revenue += total
      monthlyMap[key].Collected += Number(r.collected_usd || 0)
      monthlyMap[key].Outstanding += (total - Number(r.collected_usd || 0))
    })"""
content = content.replace(old_all_time, new_all_time)

# Recent tx injection
old_hCombined = """      const hCombined = [
        ...(hgi || []).map(r => ({ date: r.invoice_date, label: r.guest_name || 'Guest Invoice', amount: r.invoice_amount_usd, currency: 'USD' })),
        ...(hre || []).map(r => ({ date: r.entry_date, label: r.account?.name || 'Revenue', amount: r.amount_usd, currency: 'USD' })),
        ...(hee || []).map(r => ({ date: r.expense_date, label: r.account?.name || 'Expense', amount: r.amount_usd, currency: 'USD' })),
      ]"""
new_hCombined = """      const hCombined = [
        ...(hgi || []).map(r => ({ date: r.invoice_date, label: r.guest_name || 'Guest Invoice', amount: r.invoice_amount_usd, currency: 'USD' })),
        ...(hre || []).map(r => ({ date: r.entry_date, label: r.account?.name || 'Revenue', amount: r.amount_usd, currency: 'USD' })),
        ...(hee || []).map(r => ({ date: r.expense_date, label: r.account?.name || 'Expense', amount: r.amount_usd, currency: 'USD' })),
        ...(restaurantRevenue || []).map(r => ({ date: r.revenue_date, label: r.meal_period + ' F&B Revenue', amount: (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))), currency: 'USD' }))
      ]"""
content = content.replace(old_hCombined, new_hCombined)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)

