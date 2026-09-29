with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

# We need to inject the monthlyMap calculation for hotel/restaurant
old_hotel_block = """  if (['hotel', 'restaurant'].includes(activeProduct)) {
    totalInvoiced = (hotelGuestInvoices || []).reduce((s, i) => s + Number(i.amount_usd), 0)
    outstanding = (hotelGuestInvoices || []).reduce((s, i) => s + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
    collected = totalInvoiced - outstanding
    expenses = (hotelExpenseEntries || []).reduce((s, i) => s + Number(i.amount_usd), 0)
    overdueCount = (hotelGuestInvoices || []).filter(i => i.status === 'Overdue').length

    const statusCounts = (hotelGuestInvoices || []).reduce((acc, i) => { acc[i.status] = (acc[i.status] || 0) + 1; return acc }, {})
    statusPie = Object.entries(statusCounts).map(([name, value]) => ({ name, value }))

    txTypePie = [
      { name: 'Purchase Invoices', value: (purchases || []).length },
      { name: 'Guest Invoices', value: (hotelGuestInvoices || []).length },
      { name: 'Daily Room Rev', value: (hotelRoomStats || []).length },
      { name: 'Ancillary Rev', value: (hotelRevenueEntries || []).length },
      { name: 'Expense Entries', value: (hotelExpenseEntries || []).length }
    ].filter(x => x.value > 0)

  } else {"""

new_hotel_block = """  if (['hotel', 'restaurant'].includes(activeProduct)) {
    totalInvoiced = (hotelGuestInvoices || []).reduce((s, i) => s + Number(i.amount_usd), 0)
    outstanding = (hotelGuestInvoices || []).reduce((s, i) => s + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
    collected = totalInvoiced - outstanding
    expenses = (hotelExpenseEntries || []).reduce((s, i) => s + Number(i.amount_usd), 0)
    overdueCount = (hotelGuestInvoices || []).filter(i => i.status === 'Overdue').length

    const statusCounts = (hotelGuestInvoices || []).reduce((acc, i) => { acc[i.status] = (acc[i.status] || 0) + 1; return acc }, {})
    statusPie = Object.entries(statusCounts).map(([name, value]) => ({ name, value }))

    txTypePie = [
      { name: 'Purchase Invoices', value: (purchases || []).length },
      { name: 'Guest Invoices', value: (hotelGuestInvoices || []).length },
      { name: 'Daily Room Rev', value: (hotelRoomStats || []).length },
      { name: 'Ancillary Rev', value: (hotelRevenueEntries || []).length },
      { name: 'Daily Restaurant Rev', value: (restaurantRevenue || []).length },
      { name: 'Expense Entries', value: (hotelExpenseEntries || []).length }
    ].filter(x => x.value > 0)

    if (activeProduct === 'restaurant') {
        (restaurantRevenue || []).forEach(r => {
            const key = (r.revenue_date || '').slice(0, 7) || 'Unknown'
            monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
            const totalDaily = Number(r.food_sales_usd || 0) + Number(r.beverage_sales_usd || 0) + Number(r.other_revenue_usd || 0)
            monthlyMap[key].revenue += totalDaily
            monthlyMap[key].collected += totalDaily
            monthlyMap[key].invoices += 1 // Count as a daily entry
        })
        
        // Also add Guest Invoices to status pie if they use them in restaurant (usually they don't but just in case)
        if (statusPie.length === 0) {
            statusPie = [{ name: 'Daily Revenue', value: (restaurantRevenue || []).length }]
        }
    } else {
        (hotelRoomStats || []).forEach(r => {
            const key = (r.stat_date || '').slice(0, 7) || 'Unknown'
            monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
            monthlyMap[key].revenue += Number(r.room_revenue_usd || 0)
            monthlyMap[key].collected += Number(r.room_revenue_usd || 0)
        })
        ;(hotelRevenueEntries || []).forEach(r => {
            const key = (r.entry_date || '').slice(0, 7) || 'Unknown'
            monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
            monthlyMap[key].revenue += Number(r.amount_usd || 0)
            monthlyMap[key].collected += Number(r.amount_usd || 0)
        })
        ;(hotelGuestInvoices || []).forEach(i => {
            const key = (i.invoice_date || '').slice(0, 7) || 'Unknown'
            monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
            monthlyMap[key].invoices += 1
            // Revenue is already counted in daily stats, we don't double count it here.
        })
    }

  } else {"""

content = content.replace(old_hotel_block, new_hotel_block)

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(content)

# Bump sw.js
with open('public/sw.js', 'r') as f:
    sw = f.read()
sw = sw.replace('v114', 'v115')
with open('public/sw.js', 'w') as f:
    f.write(sw)
