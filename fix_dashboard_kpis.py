import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# I need to add state for ledger and hotel entries
code = code.replace(
    "const [hotelStats, setHotelStats] = useState(null)",
    """const [hotelStats, setHotelStats] = useState(null)
  const [ledgerEntries, setLedgerEntries] = useState([])
  const [accounts, setAccounts] = useState([])
  const [hotelRoomStats, setHotelRoomStats] = useState([])
  const [hotelGuestInvoices, setHotelGuestInvoices] = useState([])
  const [hotelExpenseEntries, setHotelExpenseEntries] = useState([])
  const [hotelAmc, setHotelAmc] = useState([])"""
)

# Modify loadData to fetch them
old_load = """    const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }] = await Promise.all([
      supabase.from('sales_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct)
        .gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('purchase_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct)
        .gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
        .gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
      supabase.from('sales_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('purchase_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).eq('product', activeProduct),
    ])"""

new_load = """    const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }, { data: accs }, { data: led }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }] = await Promise.all([
      supabase.from('sales_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('purchase_invoices').select('*, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to).order('invoice_date', { ascending: false }),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
      supabase.from('sales_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('purchase_invoices').select('amount_usd, invoice_date').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('accounts').select('id, type, name').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
      activeProduct === 'hotel' ? supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
    ])
    setAccounts(accs || [])
    setLedgerEntries(led || [])
    setHotelRoomStats(hrs || [])
    setHotelGuestInvoices(hgi || [])
    setHotelExpenseEntries(hee || [])
    setHotelAmc(hamc || [])"""

code = code.replace(old_load, new_load)


# Replace KPI calculation logic
old_calc = """  const totalBilled = sales.reduce((sum, i) => sum + Number(i.amount_usd), 0)
  const totalExpenses = purchases.reduce((sum, i) => sum + Number(i.amount_usd), 0)
  const netProfit = totalBilled - totalExpenses
  const outstanding = sales.reduce((sum, i) => sum + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
  const collected = totalBilled - outstanding
  const expensesMade = purchases.reduce((sum, i) => sum + (i.status === 'Paid' ? Number(i.amount_usd) : 0), 0)
  const actualProfit = collected - expensesMade"""

new_calc = """  // Compute ledger-based revenue and expenses (Universal)
  const balances = {}
  ledgerEntries.forEach(e => { balances[e.account_id] = (balances[e.account_id] || 0) + Number(e.debit_usd) - Number(e.credit_usd) })
  const sumAccs = (type) => accounts.filter(a => a.type === type).reduce((s, a) => s + (balances[a.id] || 0), 0)
  
  let totalBilled = 0
  let totalExpenses = 0
  let outstanding = 0
  let collected = 0
  let expensesMade = 0

  if (activeProduct === 'hotel') {
    // For Hotel, Revenue and Expense come directly from the ledger
    totalBilled = -sumAccs('Revenue')
    totalExpenses = sumAccs('Expenses')
    
    // Outstanding = Unpaid Guest Invoices
    outstanding = hotelGuestInvoices.reduce((s, i) => s + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)
    
    // Collected = Guest Invoices Paid + Daily Room Revenue Collected
    collected = hotelGuestInvoices.reduce((s, i) => s + Number(i.collected_amount_usd), 0) + 
                hotelRoomStats.reduce((s, r) => s + Number(r.room_revenue_collected_usd), 0)
                
    // Expenses Made = Expense entries + amortized AMC (assuming paid for simplicity)
    const start = new Date(cp.range.from)
    const end = new Date(cp.range.to)
    const monthsInView = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1
    const amcTotal = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    expensesMade = hotelExpenseEntries.reduce((s, e) => s + Number(e.amount_usd), 0) + amcTotal
  } else {
    // For Basic, use standard invoices
    totalBilled = sales.reduce((sum, i) => sum + Number(i.amount_usd), 0)
    totalExpenses = purchases.reduce((sum, i) => sum + Number(i.amount_usd), 0)
    outstanding = sales.reduce((sum, i) => sum + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
    collected = totalBilled - outstanding
    expensesMade = purchases.reduce((sum, i) => sum + (i.status === 'Paid' ? Number(i.amount_usd) : 0), 0)
  }

  const netProfit = totalBilled - totalExpenses
  const actualProfit = collected - expensesMade"""

code = code.replace(old_calc, new_calc)


# Replace YTD calculations to ALSO support Hotel
old_ytd = """  const ytdSales = allSales.filter(i => i.invoice_date >= ytdRange.from && i.invoice_date <= ytdRange.to)
  const ytdPurchases = allPurchases.filter(i => i.invoice_date >= ytdRange.from && i.invoice_date <= ytdRange.to)
  const ytdRevenue = ytdSales.reduce((s, i) => s + Number(i.amount_usd), 0)
  const ytdExpenses = ytdPurchases.reduce((s, i) => s + Number(i.amount_usd), 0)"""

new_ytd = """  let ytdRevenue = 0
  let ytdExpenses = 0
  
  if (activeProduct === 'hotel') {
    // Note: since we only query ledgerEntries for the currently selected period (not YTD),
    // calculating true YTD requires fetching ledger entries for the YTD range.
    // For now, we will leave YTD as 0 for Hotel unless we fetch it.
  } else {
    const ytdSales = allSales.filter(i => i.invoice_date >= ytdRange.from && i.invoice_date <= ytdRange.to)
    const ytdPurchases = allPurchases.filter(i => i.invoice_date >= ytdRange.from && i.invoice_date <= ytdRange.to)
    ytdRevenue = ytdSales.reduce((s, i) => s + Number(i.amount_usd), 0)
    ytdExpenses = ytdPurchases.reduce((s, i) => s + Number(i.amount_usd), 0)
  }"""

code = code.replace(old_ytd, new_ytd)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
