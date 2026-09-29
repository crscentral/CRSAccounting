with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

old_promise = """    const [{ data: s }, { data: p }, { data: r }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }] = await Promise.all([
      supabase.from('sales_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', range.from).lte('receipt_date', range.to),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', range.from).lte('expense_date', range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to) : Promise.resolve({ data: [] }),
    ])
    const sSel = s || [], pSel = p || [], rSel = r || []
    const hrsSel = hrs || [], hgiSel = hgi || [], heeSel = hee || [], hamcSel = hamc || [], hreSel = hre || []"""

new_promise = """    const [{ data: s }, { data: p }, { data: r }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }, { data: rdr }] = await Promise.all([
      supabase.from('sales_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('purchase_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('payment_receipts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', range.from).lte('receipt_date', range.to),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', range.from).lte('expense_date', range.to) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct) : Promise.resolve({ data: [] }),
      ['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to) : Promise.resolve({ data: [] }),
      activeProduct === 'restaurant' ? supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to) : Promise.resolve({ data: [] }),
    ])
    const sSel = s || [], pSel = p || [], rSel = r || []
    const hrsSel = hrs || [], hgiSel = hgi || [], heeSel = hee || [], hamcSel = hamc || [], hreSel = hre || [], rdrSel = rdr || []"""

content = content.replace(old_promise, new_promise)

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(content)

