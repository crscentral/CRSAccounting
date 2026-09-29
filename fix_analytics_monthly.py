with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

# Find where hotelRevenueEntries loop ends, and inject restaurantRevenue loop
old_code = """    ;(hotelRevenueEntries || []).forEach(r => {
      const key = (r.entry_date || '').slice(0, 7) || 'Unknown'
      monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
      monthlyMap[key].invoices += 1
      monthlyMap[key].revenue += Number(r.amount_usd || 0)
      monthlyMap[key].collected += Number(r.amount_usd || 0)
    })"""

new_code = """    ;(hotelRevenueEntries || []).forEach(r => {
      const key = (r.entry_date || '').slice(0, 7) || 'Unknown'
      monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
      monthlyMap[key].invoices += 1
      monthlyMap[key].revenue += Number(r.amount_usd || 0)
      monthlyMap[key].collected += Number(r.amount_usd || 0)
    })
    ;(restaurantRevenue || []).forEach(r => {
      const key = (r.revenue_date || '').slice(0, 7) || 'Unknown'
      monthlyMap[key] = monthlyMap[key] || { month: key, invoices: 0, revenue: 0, collected: 0 }
      monthlyMap[key].invoices += 1
      monthlyMap[key].revenue += Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))
      monthlyMap[key].collected += Number(r.collected_usd || 0)
    })"""

content = content.replace(old_code, new_code)

# Add Daily Revenue to status pie chart if activeProduct === 'restaurant'
old_pie = """    const fullyPaidCount = (hotelGuestInvoices || []).filter(i => Number(i.collected_amount_usd) >= Number(i.invoice_amount_usd)).length
    const pendingCount = (hotelGuestInvoices || []).length - fullyPaidCount
    statusPie = [
      { name: 'Paid', value: fullyPaidCount },
      { name: 'Pending', value: pendingCount }
    ].filter(x => x.value > 0)"""

new_pie = """    const fullyPaidCount = (hotelGuestInvoices || []).filter(i => Number(i.collected_amount_usd) >= Number(i.invoice_amount_usd)).length
    const pendingCount = (hotelGuestInvoices || []).length - fullyPaidCount
    statusPie = [
      { name: 'Paid', value: fullyPaidCount },
      { name: 'Pending', value: pendingCount }
    ]
    if (activeProduct === 'restaurant') {
      const restRevPaid = (restaurantRevenue || []).filter(i => Number(i.collected_usd||0) >= (Number(i.food_amount_usd||0) + Number(i.beverage_amount_usd||0))).length
      const restRevPending = (restaurantRevenue || []).length - restRevPaid
      statusPie.push({ name: 'Daily Rev Paid', value: restRevPaid })
      statusPie.push({ name: 'Daily Rev Pending', value: restRevPending })
    }
    statusPie = statusPie.filter(x => x.value > 0)"""

content = content.replace(old_pie, new_pie)

# Do the same for the PDF report generation loop
old_pdf_code = """      hreSel.forEach(i => { const k = i.entry_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].invoices += 1; monthlyMap[k].revenue += Number(i.amount_usd || 0); monthlyMap[k].collected += Number(i.amount_usd || 0) })"""

new_pdf_code = """      hreSel.forEach(i => { const k = i.entry_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].invoices += 1; monthlyMap[k].revenue += Number(i.amount_usd || 0); monthlyMap[k].collected += Number(i.amount_usd || 0) })
      rdrSel.forEach(i => { const k = i.revenue_date.slice(0, 7); monthlyMap[k] = monthlyMap[k] || { month: k, invoices: 0, revenue: 0, collected: 0 }; monthlyMap[k].invoices += 1; monthlyMap[k].revenue += Number(i.total_amount_usd) || (Number(i.food_amount_usd||0) + Number(i.beverage_amount_usd||0)); monthlyMap[k].collected += Number(i.collected_usd || 0) })"""

content = content.replace(old_pdf_code, new_pdf_code)

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(content)

