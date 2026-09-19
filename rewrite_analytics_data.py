import re

with open('src/pages/Analytics.jsx', 'r') as f:
    code = f.read()

# Add new state variables
new_state = """  const [sales, setSales] = useState([])
  const [purchases, setPurchases] = useState([])
  const [receipts, setReceipts] = useState([])
  const [hotelRoomStats, setHotelRoomStats] = useState([])
  const [hotelGuestInvoices, setHotelGuestInvoices] = useState([])
  const [hotelExpenseEntries, setHotelExpenseEntries] = useState([])
  const [hotelAmc, setHotelAmc] = useState([])
  const [hotelRevenueEntries, setHotelRevenueEntries] = useState([])"""
code = re.sub(r'  const \[sales, setSales\] = useState\(\[\]\)\n  const \[purchases, setPurchases\] = useState\(\[\]\)\n  const \[receipts, setReceipts\] = useState\(\[\]\)', new_state, code)

# Rewrite loadData
old_load = """  async function loadData() {
    const [{ data: s }, { data: p }, { data: r }] = await Promise.all([
      supabase.from('sales_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
    ])
    setSales(s || []); setPurchases(p || []); setReceipts(r || [])
  }"""
new_load = """  async function loadData() {
    const [{ data: s }, { data: p }, { data: r }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }] = await Promise.all([
      supabase.from('sales_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
      activeProduct === 'hotel' ? supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to) : Promise.resolve({ data: [] }),
    ])
    setSales(s || []); setPurchases(p || []); setReceipts(r || [])
    setHotelRoomStats(hrs || [])
    setHotelGuestInvoices(hgi || [])
    setHotelExpenseEntries(hee || [])
    setHotelAmc(hamc || [])
    setHotelRevenueEntries(hre || [])
  }"""
code = code.replace(old_load, new_load)

# Rewrite generateAnalyticsReport logic to fetch both
old_report_fetch = """    const [{ data: s }, { data: p }, { data: r }] = await Promise.all([
      supabase.from('sales_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', range.from).lte('receipt_date', range.to),
    ])
    const sSel = s || [], pSel = p || [], rSel = r || []"""
new_report_fetch = """    const [{ data: s }, { data: p }, { data: r }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }] = await Promise.all([
      supabase.from('sales_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', range.from).lte('receipt_date', range.to),
      activeProduct === 'hotel' ? supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', range.from).lte('expense_date', range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to) : Promise.resolve({ data: [] }),
    ])
    const sSel = s || [], pSel = p || [], rSel = r || []
    const hrsSel = hrs || [], hgiSel = hgi || [], heeSel = hee || [], hamcSel = hamc || [], hreSel = hre || []"""
code = code.replace(old_report_fetch, new_report_fetch)

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(code)
