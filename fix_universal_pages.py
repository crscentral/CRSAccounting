import re

# Fix Transactions.jsx
with open('src/pages/Transactions.jsx', 'r') as f:
    code = f.read()

old_load = """  async function loadAll() {
    setLoading(true)
    const [{ data: salesRows }, { data: purchaseRows }, { data: receiptRows }] = await Promise.all([
      wantSales ? supabase.from('sales_invoices').select('invoice_number, invoice_date, amount_usd, contact:contacts(name)').eq('company_id', activeCompany.id).gte('invoice_date', range.from).lte('invoice_date', range.to) : Promise.resolve({ data: [] }),
      wantPurchase ? supabase.from('purchase_invoices').select('invoice_number, invoice_date, amount_usd, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).gte('invoice_date', range.from).lte('invoice_date', range.to) : Promise.resolve({ data: [] }),
      wantReceipts ? supabase.from('payment_receipts').select('receipt_date, amount_usd').eq('company_id', activeCompany.id).gte('receipt_date', range.from).lte('receipt_date', range.to) : Promise.resolve({ data: [] }),
    ])
    const arr = []
    if (wantSales) (salesRows || []).forEach(r => arr.push({ id: `sales-${r.invoice_number}`, date: r.invoice_date, type: 'Sales Invoice', ref: r.invoice_number, contact: r.contact?.name || '—', amount: r.amount_usd, is_revenue: true }))
    if (wantPurchase) (purchaseRows || []).forEach(r => arr.push({ id: `purch-${r.invoice_number}`, date: r.invoice_date, type: 'Purchase Invoice', ref: r.invoice_number, contact: r.supplier_name_freeform || r.contact?.name || '—', amount: r.amount_usd, is_revenue: false }))
    if (wantReceipts) (receiptRows || []).forEach(r => arr.push({ id: `rect-${r.id}`, date: r.receipt_date, type: 'Receipt / Payment', ref: '—', contact: '—', amount: r.amount_usd, is_revenue: true }))
    setRows(arr.sort((a, b) => new Date(b.date) - new Date(a.date)))
    setLoading(false)
  }"""

new_load = """  async function loadAll() {
    setLoading(true)
    let salesPromise = Promise.resolve({ data: [] });
    let purchasePromise = Promise.resolve({ data: [] });
    let receiptPromise = wantReceipts ? supabase.from('payment_receipts').select('receipt_date, amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', range.from).lte('receipt_date', range.to) : Promise.resolve({ data: [] });

    if (activeProduct === 'hotel') {
      if (wantSales) salesPromise = supabase.from('hotel_guest_invoices').select('id, invoice_date, invoice_amount_usd, guest_name').eq('company_id', activeCompany.id).gte('invoice_date', range.from).lte('invoice_date', range.to);
      if (wantPurchase) purchasePromise = supabase.from('hotel_expense_entries').select('id, expense_date, amount_usd, supplier_name').eq('company_id', activeCompany.id).gte('expense_date', range.from).lte('expense_date', range.to);
    } else {
      if (wantSales) salesPromise = supabase.from('sales_invoices').select('invoice_number, invoice_date, amount_usd, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to);
      if (wantPurchase) purchasePromise = supabase.from('purchase_invoices').select('invoice_number, invoice_date, amount_usd, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to);
    }

    const [{ data: salesRows }, { data: purchaseRows }, { data: receiptRows }] = await Promise.all([salesPromise, purchasePromise, receiptPromise])
    
    const arr = []
    if (activeProduct === 'hotel') {
      if (wantSales) (salesRows || []).forEach(r => arr.push({ id: `sales-${r.id}`, date: r.invoice_date, type: 'Guest Invoice', ref: r.id.substring(0,8), contact: r.guest_name || '—', amount: r.invoice_amount_usd, is_revenue: true }))
      if (wantPurchase) (purchaseRows || []).forEach(r => arr.push({ id: `purch-${r.id}`, date: r.expense_date, type: 'Hotel Expense', ref: r.id.substring(0,8), contact: r.supplier_name || '—', amount: r.amount_usd, is_revenue: false }))
    } else {
      if (wantSales) (salesRows || []).forEach(r => arr.push({ id: `sales-${r.invoice_number}`, date: r.invoice_date, type: 'Sales Invoice', ref: r.invoice_number, contact: r.contact?.name || '—', amount: r.amount_usd, is_revenue: true }))
      if (wantPurchase) (purchaseRows || []).forEach(r => arr.push({ id: `purch-${r.invoice_number}`, date: r.invoice_date, type: 'Purchase Invoice', ref: r.invoice_number, contact: r.supplier_name_freeform || r.contact?.name || '—', amount: r.amount_usd, is_revenue: false }))
    }
    if (wantReceipts) (receiptRows || []).forEach(r => arr.push({ id: `rect-${r.id}`, date: r.receipt_date, type: 'Receipt / Payment', ref: '—', contact: '—', amount: r.amount_usd, is_revenue: true }))
    setRows(arr.sort((a, b) => new Date(b.date) - new Date(a.date)))
    setLoading(false)
  }"""
code = code.replace(old_load, new_load)
with open('src/pages/Transactions.jsx', 'w') as f: f.write(code)


# Fix Analytics.jsx
with open('src/pages/Analytics.jsx', 'r') as f:
    code = f.read()

old_load_analytics = """  async function loadAll() {
    const [{ data: accs }, { data: salesRows }, { data: purchaseRows }, { data: receiptRows }] = await Promise.all([
      supabase.from('accounts').select('id, name, type').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('sales_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
    ])"""

new_load_analytics = """  async function loadAll() {
    // For universal metrics, use ledger entries to capture all hotel/restaurant/basic activity
    const [{ data: accs }, { data: entries }] = await Promise.all([
      supabase.from('accounts').select('id, name, type').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd, entry_date').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
    ])
    
    // Fallbacks for chart parsing
    const salesRows = []
    const purchaseRows = []
    const receiptRows = []
    // To reconstruct sales/purchase arrays for the existing chart logic using ledger entries:
    entries.forEach(e => {
       const acc = accs.find(a => a.id === e.account_id)
       if (!acc) return
       if (acc.type === 'Revenue' && Number(e.credit_usd) > 0) salesRows.push({ invoice_date: e.entry_date, amount_usd: e.credit_usd, account_id: e.account_id })
       if (acc.type === 'Expenses' && Number(e.debit_usd) > 0) purchaseRows.push({ invoice_date: e.entry_date, amount_usd: e.debit_usd, account_id: e.account_id })
       if (acc.type === 'Bank/Cash' && Number(e.debit_usd) > 0) receiptRows.push({ receipt_date: e.entry_date, amount_usd: e.debit_usd })
    })"""
code = code.replace(old_load_analytics, new_load_analytics)

# Also fix the PDF generator load
old_pdf_analytics = """  async function generateAnalyticsReport(selections, format) {
    const [{ data: accs }, { data: salesRows }, { data: purchaseRows }, { data: receiptRows }] = await Promise.all([
      supabase.from('accounts').select('id, name, type').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('sales_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', range.from).lte('receipt_date', range.to),
    ])"""
new_pdf_analytics = """  async function generateAnalyticsReport(selections, format) {
    const [{ data: accs }, { data: entries }] = await Promise.all([
      supabase.from('accounts').select('id, name, type').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd, entry_date').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to),
    ])
    const salesRows = []
    const purchaseRows = []
    entries.forEach(e => {
       const acc = accs.find(a => a.id === e.account_id)
       if (!acc) return
       if (acc.type === 'Revenue' && Number(e.credit_usd) > 0) salesRows.push({ invoice_date: e.entry_date, amount_usd: e.credit_usd, account_id: e.account_id })
       if (acc.type === 'Expenses' && Number(e.debit_usd) > 0) purchaseRows.push({ invoice_date: e.entry_date, amount_usd: e.debit_usd, account_id: e.account_id })
    })"""
code = code.replace(old_pdf_analytics, new_pdf_analytics)
with open('src/pages/Analytics.jsx', 'w') as f: f.write(code)

