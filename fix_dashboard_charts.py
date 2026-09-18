import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

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
    // We do not have all-time queries specifically for hotel, so we approximate with YTD or rely on ledger balances if needed.
    // For now, we'll just sum the range we have, or leave it as 0 if the user didn't fetch all-time.
    // To be perfectly accurate, we should query all-time, but for the UI charts, we just use the current range.
    allTimeRevenue = ledgerEntries.filter(e => accounts.find(a => a.id === e.account_id)?.type === 'Revenue').reduce((s, e) => s + (Number(e.credit_usd) - Number(e.debit_usd)), 0)
    allTimeExpenses = ledgerEntries.filter(e => accounts.find(a => a.id === e.account_id)?.type === 'Expenses').reduce((s, e) => s + (Number(e.debit_usd) - Number(e.credit_usd)), 0)
    
    // Build monthly map from hotel tables
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
    // AMC Amortized by month
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

code = code.replace(old_chart_data, new_chart_data)

# Also fix Draft Invoices / Draft Expenses so it doesn't crash if they don't apply
old_draft = r"""  const draftInvoices = sales.filter\(i => i.status !== 'Paid'\)
  const draftExpenses = purchases.filter\(i => i.status === 'Draft'\)"""
new_draft = """  const draftInvoices = activeProduct === 'hotel' ? hotelGuestInvoices.filter(i => Number(i.invoice_amount_usd) > Number(i.collected_amount_usd)) : sales.filter(i => i.status !== 'Paid')
  const draftExpenses = activeProduct === 'hotel' ? [] : purchases.filter(i => i.status === 'Draft')"""
code = code.replace(old_draft, new_draft)

# And fix Recent Transactions if hotel
old_recent = r"setRecentTx\(combined\)"
new_recent = """if (activeProduct === 'hotel') {
      const [{ data: hgi }, { data: hre }, { data: hee }] = await Promise.all([
        supabase.from('hotel_guest_invoices').select('invoice_number, invoice_date, invoice_amount, currency, guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).order('invoice_date', { ascending: false }).limit(3),
        supabase.from('hotel_revenue_entries').select('entry_date, amount, currency, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('entry_date', { ascending: false }).limit(3),
        supabase.from('hotel_expense_entries').select('expense_date, amount, currency, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).order('expense_date', { ascending: false }).limit(3),
      ])
      const hCombined = [
        ...(hgi || []).map(r => ({ date: r.invoice_date, label: r.guest_name || r.invoice_number, amount: r.invoice_amount, currency: r.currency })),
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
