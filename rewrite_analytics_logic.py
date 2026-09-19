import re

with open('src/pages/Analytics.jsx', 'r') as f:
    code = f.read()

# Replace the calculation logic in the main render body
old_logic = """  const totalInvoiced = sales.reduce((s, i) => s + Number(i.amount_usd), 0)
  const outstanding = sales.reduce((s, i) => s + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
  const collected = totalInvoiced - outstanding
  const expenses = purchases.reduce((s, i) => s + Number(i.amount_usd), 0)
  const overdueCount = sales.filter(i => i.status === 'Overdue').length

  const monthlyMap = {}
  sales.forEach(i => {
    const key = i.invoice_date.slice(0, 7)
    monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
    monthlyMap[key].invoices += 1
    monthlyMap[key].revenue += Number(i.amount_usd)
  })
  receipts.forEach(r => {
    const key = r.receipt_date.slice(0, 7)
    monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
    monthlyMap[key].collected += Number(r.amount_usd)
  })
  const monthly = Object.values(monthlyMap).sort((a, b) => a.month.localeCompare(b.month))

  const statusCounts = sales.reduce((acc, i) => { acc[i.status] = (acc[i.status] || 0) + 1; return acc }, {})
  const statusPie = Object.entries(statusCounts).map(([name, value]) => ({ name, value }))

  const txTypePie = [
    { name: 'Sales Invoice', value: sales.length },
    { name: 'Purchase Invoice', value: purchases.length },
  ]"""

new_logic = """  let totalInvoiced = 0
  let outstanding = 0
  let collected = 0
  let expenses = 0
  let overdueCount = 0

  const monthlyMap = {}
  let statusPie = []
  let txTypePie = []

  if (activeProduct === 'hotel') {
    const manualRoomCollected = hotelRoomStats.reduce((s, r) => s + Number(r.manual_room_revenue_collected_usd || 0), 0)
    const manualRoomRevenue = hotelRoomStats.reduce((s, r) => s + Number(r.room_revenue_usd || 0), 0)
    const guestInvoiceCollected = hotelGuestInvoices.reduce((s, i) => s + Number(i.collected_amount_usd || 0), 0)
    const guestInvoiceRevenue = hotelGuestInvoices.reduce((s, i) => s + Number(i.invoice_amount_usd || 0), 0)
    const ancillaryCollected = hotelRevenueEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0)

    totalInvoiced = manualRoomRevenue + guestInvoiceRevenue + ancillaryCollected
    collected = manualRoomCollected + guestInvoiceCollected + ancillaryCollected
    outstanding = hotelGuestInvoices.reduce((s, i) => s + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)

    const start = new Date(cp.range.from)
    const end = new Date(Math.min(new Date(cp.range.to).getTime(), new Date().getTime()))
    const monthsInView = Math.max(1, (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1)
    const amcTotal = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    expenses = hotelExpenseEntries.reduce((s, e) => s + Number(e.amount_usd), 0) + amcTotal

    overdueCount = hotelGuestInvoices.filter(i => Number(i.invoice_amount_usd) > Number(i.collected_amount_usd)).length

    hotelGuestInvoices.forEach(i => {
      const key = i.invoice_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
      monthlyMap[key].invoices += 1
      monthlyMap[key].revenue += Number(i.invoice_amount_usd || 0)
      monthlyMap[key].collected += Number(i.collected_amount_usd || 0)
    })
    hotelRoomStats.forEach(r => {
      const key = r.stat_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
      monthlyMap[key].invoices += 1
      monthlyMap[key].revenue += Number(r.room_revenue_usd || 0)
      monthlyMap[key].collected += Number(r.manual_room_revenue_collected_usd || 0)
    })
    hotelRevenueEntries.forEach(r => {
      const key = r.entry_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
      monthlyMap[key].invoices += 1
      monthlyMap[key].revenue += Number(r.amount_usd || 0)
      monthlyMap[key].collected += Number(r.amount_usd || 0)
    })

    const fullyPaidCount = hotelGuestInvoices.filter(i => Number(i.collected_amount_usd) >= Number(i.invoice_amount_usd)).length
    const pendingCount = hotelGuestInvoices.length - fullyPaidCount
    statusPie = [
      { name: 'Paid', value: fullyPaidCount },
      { name: 'Pending', value: pendingCount }
    ].filter(x => x.value > 0)

    txTypePie = [
      { name: 'Guest Invoices', value: hotelGuestInvoices.length },
      { name: 'Daily Room Rev', value: hotelRoomStats.length },
      { name: 'Ancillary Rev', value: hotelRevenueEntries.length },
      { name: 'Expense Entries', value: hotelExpenseEntries.length }
    ].filter(x => x.value > 0)

  } else {
    totalInvoiced = sales.reduce((s, i) => s + Number(i.amount_usd), 0)
    outstanding = sales.reduce((s, i) => s + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
    collected = totalInvoiced - outstanding
    expenses = purchases.reduce((s, i) => s + Number(i.amount_usd), 0)
    overdueCount = sales.filter(i => i.status === 'Overdue').length

    sales.forEach(i => {
      const key = i.invoice_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
      monthlyMap[key].invoices += 1
      monthlyMap[key].revenue += Number(i.amount_usd)
    })
    receipts.forEach(r => {
      const key = r.receipt_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
      monthlyMap[key].collected += Number(r.amount_usd)
    })

    const statusCounts = sales.reduce((acc, i) => { acc[i.status] = (acc[i.status] || 0) + 1; return acc }, {})
    statusPie = Object.entries(statusCounts).map(([name, value]) => ({ name, value }))

    txTypePie = [
      { name: 'Sales Invoice', value: sales.length },
      { name: 'Purchase Invoice', value: purchases.length },
    ]
  }

  const monthly = Object.values(monthlyMap).sort((a, b) => a.month.localeCompare(b.month))"""

code = code.replace(old_logic, new_logic)

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(code)
