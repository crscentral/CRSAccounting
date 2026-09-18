import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# 1. Budget sum fix
old_daily_trend = r"""    const budgetByMonth = \{\}
    ;\(budgetRows \|\| \[\]\).forEach\(b => \{ budgetByMonth\[`\$\{b.budget_year\}-\$\{b.budget_month\}`\] = Number\(b.budgeted_room_revenue_usd\) \}\)
    const dailyTrend = \(stats \|\| \[\]\).map\(s => \{
      const \[y, m\] = s.stat_date.split\('-'\)
      const key = `\$\{y\}-\$\{Number\(m\)\}`
      const dailyBudget = budgetByMonth\[key\] \|\| 0
      return \{ date: s.stat_date, Actual: Number\(s.room_revenue_usd\), Budget: dailyBudget \}
    \}\)
    const totalBudgetUsd = dailyTrend.reduce\(\(sum, d\) => sum \+ d.Budget, 0\)
    const totalVarianceUsd = totalRevenue - totalBudgetUsd"""

new_daily_trend = """    const budgetByMonth = {}
    ;(budgetRows || []).forEach(b => { budgetByMonth[`${b.budget_year}-${b.budget_month}`] = Number(b.budgeted_room_revenue_usd) })
    
    // Create a complete date range array for the trend chart and budget calculation
    const dailyTrendMap = {}
    let currentDate = new Date(cp.range.from)
    const endDate = new Date(cp.range.to)
    let totalBudgetUsd = 0
    
    while (currentDate <= endDate) {
      const d = currentDate.toISOString().slice(0, 10)
      const y = currentDate.getUTCFullYear()
      const m = currentDate.getUTCMonth() + 1
      const dailyBudget = budgetByMonth[`${y}-${m}`] || 0
      dailyTrendMap[d] = { date: d, Actual: 0, Budget: dailyBudget }
      totalBudgetUsd += dailyBudget
      currentDate.setUTCDate(currentDate.getUTCDate() + 1)
    }
    
    // Fill in the actuals
    ;(stats || []).forEach(s => {
      if (dailyTrendMap[s.stat_date]) {
        dailyTrendMap[s.stat_date].Actual = Number(s.room_revenue_usd)
      } else {
        const [y, m] = s.stat_date.split('-')
        const dailyBudget = budgetByMonth[`${y}-${Number(m)}`] || 0
        dailyTrendMap[s.stat_date] = { date: s.stat_date, Actual: Number(s.room_revenue_usd), Budget: dailyBudget }
        totalBudgetUsd += dailyBudget
      }
    })
    
    const dailyTrend = Object.values(dailyTrendMap).sort((a, b) => a.date.localeCompare(b.date))
    const totalVarianceUsd = totalRevenue - totalBudgetUsd"""
code = re.sub(old_daily_trend, new_daily_trend, code)

# 2. Add hotel_revenue_entries to loadData
old_promise = r"const \[\{ data: s \}, \{ data: p \}, \{ data: r \}, \{ data: allS \}, \{ data: allP \}, \{ data: accs \}, \{ data: led \}, \{ data: hrs \}, \{ data: hgi \}, \{ data: hee \}, \{ data: hamc \}\] = await Promise.all\(\["
new_promise = "const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }, { data: accs }, { data: led }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }] = await Promise.all(["
code = code.replace(old_promise, new_promise)

old_fetch = r"activeProduct === 'hotel' \? supabase.from\('hotel_amc_contracts'\).select\('\*'\).eq\('company_id', activeCompany.id\).eq\('product', activeProduct\) : Promise.resolve\(\{ data: \[\] \}\),"
new_fetch = """activeProduct === 'hotel' ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to) : Promise.resolve({ data: [] }),"""
code = code.replace(old_fetch, new_fetch)

old_state = r"const \[hotelAmc, setHotelAmc\] = useState\(\[\]\)"
new_state = """const [hotelAmc, setHotelAmc] = useState([])
  const [hotelRevenueEntries, setHotelRevenueEntries] = useState([])"""
code = code.replace(old_state, new_state)

old_set = r"setHotelAmc\(hamc \|\| \[\]\)"
new_set = """setHotelAmc(hamc || [])
    setHotelRevenueEntries(hre || [])"""
code = code.replace(old_set, new_set)

# 3. Fix the `collected` array
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

# 4. Fix `chartData` to map from Hotel tables
old_chart_data = r"""  const allTimeRevenue = allSales.reduce\(\(s, i\) => s \+ Number\(i.amount_usd\), 0\)
  const allTimeExpenses = allPurchases.reduce\(\(s, i\) => s \+ Number\(i.amount_usd\), 0\)

  const monthlyMap = \{\}
  sales.forEach\(i => \{
    const key = i.invoice_date.slice\(0, 7\)
    monthlyMap\[key\] = monthlyMap\[key\] \|\| \{ month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 \}
    monthlyMap\[key\].Revenue \+= Number\(i.amount_usd\)
    monthlyMap\[key\].Outstanding \+= \(i.status === 'Paid' \? 0 : \(Number\(i.balance_due\) / \(Number\(i.amount\) \|\| 1\)\) \* Number\(i.amount_usd\)\)
  \}\)
  purchases.forEach\(i => \{
    const key = i.invoice_date.slice\(0, 7\)
    monthlyMap\[key\] = monthlyMap\[key\] \|\| \{ month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 \}
    monthlyMap\[key\].Expenses \+= Number\(i.amount_usd\)
  \}\)
  receipts.forEach\(r => \{
    const key = r.receipt_date.slice\(0, 7\)
    monthlyMap\[key\] = monthlyMap\[key\] \|\| \{ month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 \}
    monthlyMap\[key\].Collected \+= Number\(r.amount_usd\)
  \}\)"""

new_chart_data = """  let allTimeRevenue = 0
  let allTimeExpenses = 0
  const monthlyMap = {}
  
  if (activeProduct === 'hotel') {
    allTimeRevenue = ledgerEntries.filter(e => accounts.find(a => a.id === e.account_id)?.type === 'Revenue').reduce((s, e) => s + (Number(e.credit_usd) - Number(e.debit_usd)), 0)
    allTimeExpenses = ledgerEntries.filter(e => accounts.find(a => a.id === e.account_id)?.type === 'Expenses').reduce((s, e) => s + (Number(e.debit_usd) - Number(e.credit_usd)), 0)
    
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
      monthlyMap[key].Collected += Number(r.amount_usd)
    })
    hotelExpenseEntries.forEach(r => {
      const key = r.expense_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Expenses += Number(r.amount_usd)
    })
    const start = new Date(cp.range.from)
    const end = new Date(cp.range.to)
    const amcMonthly = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0)
    let cur = new Date(start.getFullYear(), start.getMonth(), 1)
    while (cur <= end) {
      const key = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}`
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Expenses += amcMonthly
      cur.setMonth(cur.getMonth() + 1)
    }
  } else {
    allTimeRevenue = allSales.reduce((s, i) => s + Number(i.amount_usd), 0)
    allTimeExpenses = allPurchases.reduce((s, i) => s + Number(i.amount_usd), 0)
    
    sales.forEach(i => {
      const key = i.invoice_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Revenue += Number(i.amount_usd)
      monthlyMap[key].Outstanding += (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd))
    })
    purchases.forEach(i => {
      const key = i.invoice_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Expenses += Number(i.amount_usd)
    })
    receipts.forEach(r => {
      const key = r.receipt_date.slice(0, 7)
      monthlyMap[key] = monthlyMap[key] || { month: key, Revenue: 0, Expenses: 0, Collected: 0, Outstanding: 0 }
      monthlyMap[key].Collected += Number(r.amount_usd)
    })
  }"""
code = re.sub(old_chart_data, new_chart_data, code)

old_draft = r"""  const draftInvoices = sales.filter\(i => i.status !== 'Paid'\)
  const draftExpenses = purchases.filter\(i => i.status === 'Draft'\)"""
new_draft = """  const draftInvoices = activeProduct === 'hotel' ? hotelGuestInvoices.filter(i => Number(i.invoice_amount_usd) > Number(i.collected_amount_usd)) : sales.filter(i => i.status !== 'Paid')
  const draftExpenses = activeProduct === 'hotel' ? [] : purchases.filter(i => i.status === 'Draft')"""
code = re.sub(old_draft, new_draft, code)

old_recent = r"setRecentTx\(combined\)"
new_recent = """if (activeProduct === 'hotel') {
      const [{ data: hgi }, { data: hre }, { data: hee }] = await Promise.all([
        supabase.from('hotel_guest_invoices').select('invoice_number, invoice_date, invoice_amount_usd, currency, guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).order('invoice_date', { ascending: false }).limit(3),
        supabase.from('hotel_revenue_entries').select('entry_date, amount, currency, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('entry_date', { ascending: false }).limit(3),
        supabase.from('hotel_expense_entries').select('expense_date, amount, currency, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('expense_date', { ascending: false }).limit(3),
      ])
      const hCombined = [
        ...(hgi || []).map(r => ({ date: r.invoice_date, label: r.guest_name || r.invoice_number, amount: r.invoice_amount_usd, currency: 'USD' })),
        ...(hre || []).map(r => ({ date: r.entry_date, label: r.account?.name || 'Revenue', amount: r.amount, currency: r.currency })),
        ...(hee || []).map(r => ({ date: r.expense_date, label: r.account?.name || 'Expense', amount: r.amount, currency: r.currency })),
      ].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 5)
      setRecentTx(hCombined)
    } else {
      setRecentTx(combined)
    }"""
code = code.replace(old_recent, new_recent)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
