import re

with open('src/pages/Transactions.jsx', 'r') as f:
    code = f.read()

old_load = """  async function loadData() {
    const [{ data: si }, { data: pi }, { data: pr }] = await Promise.all([
      supabase.from('sales_invoices').select('id, invoice_number, invoice_date, amount_usd, currency, amount, contact:contacts(name)')
        .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('purchase_invoices').select('id, invoice_number, invoice_date, amount_usd, currency, amount, supplier_name_freeform, contact:contacts(name)')
        .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('payment_receipts').select('id, receipt_date, amount_usd, currency, amount')
        .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
    ])

    const combined = [
      ...(si || []).map(r => ({ id: `si-${r.id}`, date: r.invoice_date, type: 'Sales Invoice', desc: `${r.invoice_number} — ${r.contact?.name || ''}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
      ...(pi || []).map(r => ({ id: `pi-${r.id}`, date: r.invoice_date, type: 'Purchase Invoice', desc: `${r.invoice_number} — ${r.contact?.name || r.supplier_name_freeform || ''}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'out' })),
      ...(pr || []).map(r => ({ id: `pr-${r.id}`, date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
    ].sort((a, b) => b.date.localeCompare(a.date))

    setRows(combined)
  }"""

new_load = """  async function loadData() {
    let siPromise = Promise.resolve({ data: [] })
    let piPromise = Promise.resolve({ data: [] })
    let prPromise = supabase.from('payment_receipts').select('id, receipt_date, amount_usd, currency, amount').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to)
    
    if (activeProduct === 'hotel') {
      siPromise = supabase.from('hotel_guest_invoices').select('id, invoice_number:id, invoice_date, amount_usd:invoice_amount_usd, currency, amount:invoice_amount, contact:guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
      piPromise = supabase.from('hotel_expense_entries').select('id, invoice_number:id, invoice_date:expense_date, amount_usd, currency, amount, contact:supplier_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to)
    } else {
      siPromise = supabase.from('sales_invoices').select('id, invoice_number, invoice_date, amount_usd, currency, amount, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
      piPromise = supabase.from('purchase_invoices').select('id, invoice_number, invoice_date, amount_usd, currency, amount, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
    }

    const [{ data: si }, { data: pi }, { data: pr }] = await Promise.all([siPromise, piPromise, prPromise])

    const combined = [
      ...(si || []).map(r => ({ id: `si-${r.id}`, date: r.invoice_date, type: activeProduct === 'hotel' ? 'Guest Invoice' : 'Sales Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.contact || ''}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
      ...(pi || []).map(r => ({ id: `pi-${r.id}`, date: r.invoice_date, type: activeProduct === 'hotel' ? 'Expense' : 'Purchase Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.supplier_name_freeform || r.contact || ''}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'out' })),
      ...(pr || []).map(r => ({ id: `pr-${r.id}`, date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
    ].sort((a, b) => b.date.localeCompare(a.date))

    setRows(combined)
  }"""
code = code.replace(old_load, new_load)

old_pdf = """    const [{ data: si }, { data: pi }, { data: pr }] = await Promise.all([
      wantSales ? supabase.from('sales_invoices').select('invoice_number, invoice_date, amount_usd, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to) : Promise.resolve({ data: [] }),
      wantPurchase ? supabase.from('purchase_invoices').select('invoice_number, invoice_date, amount_usd, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to) : Promise.resolve({ data: [] }),
      wantReceipts ? supabase.from('payment_receipts').select('receipt_date, amount_usd').eq('company_id', activeCompany.id).gte('receipt_date', range.from).lte('receipt_date', range.to) : Promise.resolve({ data: [] }),
    ])

    const combined = [
      ...(si || []).map(r => ({ date: r.invoice_date, type: 'Sales Invoice', desc: `${r.invoice_number} — ${r.contact?.name || ''}`, amount: fmt(r.amount_usd), direction: '+' })),
      ...(pi || []).map(r => ({ date: r.invoice_date, type: 'Purchase Invoice', desc: `${r.invoice_number} — ${r.contact?.name || r.supplier_name_freeform || ''}`, amount: fmt(r.amount_usd), direction: '-' })),
      ...(pr || []).map(r => ({ date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount: fmt(r.amount_usd), direction: '+' })),
    ].sort((a, b) => b.date.localeCompare(a.date))"""

new_pdf = """    let siPromise = Promise.resolve({ data: [] })
    let piPromise = Promise.resolve({ data: [] })
    let prPromise = wantReceipts ? supabase.from('payment_receipts').select('receipt_date, amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', range.from).lte('receipt_date', range.to) : Promise.resolve({ data: [] })
    
    if (activeProduct === 'hotel') {
      if (wantSales) siPromise = supabase.from('hotel_guest_invoices').select('invoice_number:id, invoice_date, amount_usd:invoice_amount_usd, contact:guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
      if (wantPurchase) piPromise = supabase.from('hotel_expense_entries').select('invoice_number:id, invoice_date:expense_date, amount_usd, contact:supplier_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', range.from).lte('expense_date', range.to)
    } else {
      if (wantSales) siPromise = supabase.from('sales_invoices').select('invoice_number, invoice_date, amount_usd, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
      if (wantPurchase) piPromise = supabase.from('purchase_invoices').select('invoice_number, invoice_date, amount_usd, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
    }

    const [{ data: si }, { data: pi }, { data: pr }] = await Promise.all([siPromise, piPromise, prPromise])

    const combined = [
      ...(si || []).map(r => ({ date: r.invoice_date, type: activeProduct === 'hotel' ? 'Guest Invoice' : 'Sales Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.contact || ''}`, amount: fmt(r.amount_usd), direction: '+' })),
      ...(pi || []).map(r => ({ date: r.invoice_date, type: activeProduct === 'hotel' ? 'Expense' : 'Purchase Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.supplier_name_freeform || r.contact || ''}`, amount: fmt(r.amount_usd), direction: '-' })),
      ...(pr || []).map(r => ({ date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount: fmt(r.amount_usd), direction: '+' })),
    ].sort((a, b) => b.date.localeCompare(a.date))"""
code = code.replace(old_pdf, new_pdf)

with open('src/pages/Transactions.jsx', 'w') as f:
    f.write(code)
