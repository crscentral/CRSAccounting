with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

old_hotel_logic = """  if (['hotel', 'restaurant'].includes(activeProduct)) {
    // For Hotel, Revenue and Expense come directly from the ledger
    totalBilled = -sumAccs('Revenue')
    totalExpenses = sumAccs('Expenses')
    
    // Outstanding = Unpaid Guest Invoices
    outstanding = hotelGuestInvoices.reduce((s, i) => s + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)
    
    // Collected = Room Revenue Collected + Ancillary Collected + Restaurant Collected
    const roomCollected = hotelRoomStats.reduce((s, r) => s + Number(r.room_revenue_collected_usd || 0), 0)
    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.collected_usd || 0), 0)
    const restRevCollected = restaurantRevenue.reduce((s, r) => s + Number(r.collected_usd || 0), 0)
    collected = roomCollected + ancillaryCollected + restRevCollected
    

                
    const start = new Date(cp.range.from)
    const end = new Date(cp.range.to)
    const monthsInView = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1
    const amcTotal = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    
    // Add AMC amortized to Total Expenses (Accrued) since it doesn't hit the ledger
    totalExpenses += amcTotal
    
    // Expenses Made = Actual cash out (hotel expense entries). AMC cash out is not modeled in the date range cleanly, so we only count direct expense entries.
    expensesMade = hotelExpenseEntries.reduce((s, e) => s + Number(e.amount_usd), 0)
  } else {"""

new_hotel_logic = """  if (['hotel', 'restaurant'].includes(activeProduct)) {
    const start = new Date(cp.range.from)
    const end = new Date(cp.range.to)
    const monthsInView = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1
    
    // Link Total Revenue directly to Daily Revenue Collection stats to perfectly match the page
    const roomRev = hotelRoomStats.reduce((s, r) => s + Number(r.room_revenue_usd || 0), 0)
    const ancRev = hotelRevenueEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0)
    const restRev = restaurantRevenue.reduce((s, r) => s + (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))), 0)
    totalBilled = roomRev + ancRev + restRev
    
    // Link Total Expenses directly to Expenses page
    const amcTotal = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    const directExpenses = hotelExpenseEntries.reduce((s, e) => s + Number(e.amount_usd || 0), 0)
    totalExpenses = directExpenses + amcTotal
    
    // Outstanding = Unpaid Guest Invoices
    outstanding = hotelGuestInvoices.reduce((s, i) => s + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)
    
    // Collected = Room Revenue Collected + Ancillary Collected + Restaurant Collected
    const roomCollected = hotelRoomStats.reduce((s, r) => s + Number(r.room_revenue_collected_usd || 0), 0)
    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.collected_usd || 0), 0)
    const restRevCollected = restaurantRevenue.reduce((s, r) => s + Number(r.collected_usd || 0), 0)
    collected = roomCollected + ancillaryCollected + restRevCollected
    
    // Expenses Made = Actual cash out (hotel expense entries).
    expensesMade = directExpenses
  } else {"""

content = content.replace(old_hotel_logic, new_hotel_logic)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)
