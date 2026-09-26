import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

# We need to completely rewrite the section from:
#   // YTD (respects company fiscal year start month)
# down to:
#   const chartData = ...
# Let's find this section using regex.

old_section_regex = r"  // YTD \(respects company fiscal year start month\).*?  const chartData = "

# First let's extract the exact text so we can see what to replace.
match = re.search(old_section_regex, content, re.DOTALL)
if match:
    old_section = match.group(0)
    
    new_section = """  // YTD & All-Time logic + Charts
  const ytdRange = getYTDRange(activeCompany.fiscal_year_start_month || 1)
  let ytdRevenue = 0
  let ytdExpenses = 0
  let allTimeRevenue = 0
  let allTimeExpenses = 0
  const monthlyMap = {}
  
  if (['hotel', 'restaurant'].includes(activeProduct)) {
    // Build monthlyMap using ALL historical data for accurate Charts, YTD, and All-Time.
    const uniqueMonths = new Set()
    
    allHotelGuestInvoices.forEach(i => {
      const key = (i.invoice_date || '').slice(0, 7)
      uniqueMonths.add(key)
      if (!key) return
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Outstanding += (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd))
      monthlyMap[key].Collected += Number(i.collected_amount_usd)
    })
    
    allHotelRoomStats.forEach(r => {
      const key = (r.stat_date || '').slice(0, 7)
      uniqueMonths.add(key)
      if (!key) return
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(r.room_revenue_usd)
      monthlyMap[key].Collected += Number(r.manual_room_revenue_collected_usd || 0)
    })
    
    allHotelRevenueEntries.forEach(r => {
      const key = (r.entry_date || '').slice(0, 7)
      uniqueMonths.add(key)
      if (!key) return
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(r.amount_usd)
      monthlyMap[key].Collected += Number(r.collected_usd || 0)
      monthlyMap[key].Outstanding += (Number(r.amount_usd) - Number(r.collected_usd || 0))
    })
    
    allHotelExpenseEntries.forEach(r => {
      const key = (r.expense_date || '').slice(0, 7)
      uniqueMonths.add(key)
      if (!key) return
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Expenses += Number(r.amount_usd)
    })
    
    allRestaurantRevenue.forEach(r => {
      const key = (r.revenue_date || '').slice(0, 7)
      uniqueMonths.add(key)
      if (!key) return
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      const total = Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))
      monthlyMap[key].Revenue += total
      monthlyMap[key].Collected += Number(r.collected_usd || 0)
      monthlyMap[key].Outstanding += (total - Number(r.collected_usd || 0))
    })
    
    // For AMC, add 1/12th of annual amount to Expenses for each unique month that exists in the map
    const amcMonthly = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0)
    Object.keys(monthlyMap).forEach(k => {
      monthlyMap[k].Expenses += amcMonthly
    })
    
    // Now calculate YTD from the map
    ytdRevenue = Object.values(monthlyMap).filter(m => {
      if (!m.month) return false
      const [y, mo] = m.month.split('-')
      const d = new Date(Number(y), Number(mo)-1, 15).toISOString().split('T')[0]
      return d >= ytdRange.from && d <= ytdRange.to
    }).reduce((s, m) => s + m.Revenue, 0)
    
    ytdExpenses = Object.values(monthlyMap).filter(m => {
      if (!m.month) return false
      const [y, mo] = m.month.split('-')
      const d = new Date(Number(y), Number(mo)-1, 15).toISOString().split('T')[0]
      return d >= ytdRange.from && d <= ytdRange.to
    }).reduce((s, m) => s + m.Expenses, 0)
    
    // Calculate All-Time from the map
    allTimeRevenue = Object.values(monthlyMap).reduce((s, m) => s + m.Revenue, 0)
    allTimeExpenses = Object.values(monthlyMap).reduce((s, m) => s + m.Expenses, 0)
    
  } else {
    // Basic product
    allTimeRevenue = allSales.reduce((s, i) => s + Number(i.amount_usd), 0)
    allTimeExpenses = allPurchases.reduce((s, i) => s + Number(i.amount_usd), 0)
    
    const ytdSales = allSales.filter(i => i.invoice_date >= ytdRange.from && i.invoice_date <= ytdRange.to)
    const ytdPurchases = allPurchases.filter(i => i.invoice_date >= ytdRange.from && i.invoice_date <= ytdRange.to)
    ytdRevenue = ytdSales.reduce((s, i) => s + Number(i.amount_usd), 0)
    ytdExpenses = ytdPurchases.reduce((s, i) => s + Number(i.amount_usd), 0)
    
    sales.forEach(i => {
      const key = (i.invoice_date || '').slice(0, 7)
      if (!key) return
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(i.amount_usd)
      monthlyMap[key].Outstanding += (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd))
    })
    
    purchases.forEach(i => {
      const key = (i.invoice_date || '').slice(0, 7)
      if (!key) return
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Expenses += Number(i.amount_usd)
    })
    
    receipts.forEach(r => {
      const key = (r.receipt_date || '').slice(0, 7)
      if (!key) return
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Collected += Number(r.amount_usd)
    })
  }
  const chartData = """
    
    content = content.replace(old_section, new_section)
    with open('src/pages/Dashboard.jsx', 'w') as f:
        f.write(content)
    print("Replaced perfectly.")
else:
    print("Regex failed to match.")

