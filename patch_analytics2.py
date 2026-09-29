with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

old_kpis = """  if (['hotel', 'restaurant'].includes(activeProduct)) {
    totalInvoiced = (hotelGuestInvoices || []).reduce((s, i) => s + Number(i.amount_usd), 0)
    outstanding = (hotelGuestInvoices || []).reduce((s, i) => s + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
    collected = totalInvoiced - outstanding
    expenses = (hotelExpenseEntries || []).reduce((s, i) => s + Number(i.amount_usd), 0)
    overdueCount = (hotelGuestInvoices || []).filter(i => i.status === 'Overdue').length"""

new_kpis = """  if (['hotel', 'restaurant'].includes(activeProduct)) {
    if (activeProduct === 'restaurant') {
        totalInvoiced = (restaurantRevenue || []).reduce((s, r) => s + Number(r.food_sales_usd || 0) + Number(r.beverage_sales_usd || 0) + Number(r.other_revenue_usd || 0), 0)
        outstanding = 0
        collected = totalInvoiced
        expenses = (hotelExpenseEntries || []).reduce((s, i) => s + Number(i.amount_usd), 0) + (purchases || []).reduce((s, i) => s + Number(i.amount_usd), 0)
        overdueCount = 0
    } else {
        totalInvoiced = (hotelGuestInvoices || []).reduce((s, i) => s + Number(i.amount_usd), 0)
        outstanding = (hotelGuestInvoices || []).reduce((s, i) => s + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
        collected = totalInvoiced - outstanding
        expenses = (hotelExpenseEntries || []).reduce((s, i) => s + Number(i.amount_usd), 0) + (purchases || []).reduce((s, i) => s + Number(i.amount_usd), 0)
        overdueCount = (hotelGuestInvoices || []).filter(i => i.status === 'Overdue').length
    }"""

content = content.replace(old_kpis, new_kpis)

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(content)

