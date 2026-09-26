import re

with open('src/pages/Transactions.jsx', 'r') as f:
    content = f.read()

# We need to add hrsPromise, hrePromise, etc.

old_fetch_block = """    let siPromise = Promise.resolve({ data: [] })
    let piPromise = Promise.resolve({ data: [] })
    let prPromise = supabase.from('payment_receipts').select('id, receipt_date, amount_usd, currency, amount').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to)
    let rdrPromise = Promise.resolve({ data: [] })
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      siPromise = supabase.from('hotel_guest_invoices').select('id, invoice_number:id, invoice_date, amount_usd:invoice_amount_usd, currency, amount:invoice_amount, contact:guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
      piPromise = supabase.from('hotel_expense_entries').select('id, invoice_number:id, invoice_date:expense_date, amount_usd, currency, amount, contact:supplier_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to)
      rdrPromise = supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
    } else {
      siPromise = supabase.from('sales_invoices').select('id, invoice_number, invoice_date, amount_usd, currency, amount, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
      piPromise = supabase.from('purchase_invoices').select('id, invoice_number, invoice_date, amount_usd, currency, amount, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
    }

    const [{ data: si }, { data: pi }, { data: pr }, { data: rdr }] = await Promise.all([siPromise, piPromise, prPromise, rdrPromise])

    const combined = [
      ...(si || []).map(r => ({ id: `si-${r.id}`, date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Guest Invoice' : 'Sales Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.contact || ''}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
      ...(pi || []).map(r => ({ id: `pi-${r.id}`, date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Expense' : 'Purchase Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.supplier_name_freeform || r.contact || ''}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'out' })),
      ...(pr || []).map(r => ({ id: `pr-${r.id}`, date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
      ...(rdr || []).map(r => { const total = Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0)); return { id: `rdr-${r.id}`, date: r.revenue_date, type: 'F&B Revenue', desc: `${r.meal_period} F&B Revenue`, amount_usd: total, amount: total, currency: 'USD', direction: 'in' } }),
    ].sort((a, b) => b.date.localeCompare(a.date))"""

new_fetch_block = """    let siPromise = Promise.resolve({ data: [] })
    let piPromise = Promise.resolve({ data: [] })
    let prPromise = supabase.from('payment_receipts').select('id, receipt_date, amount_usd, currency, amount').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to)
    let rdrPromise = Promise.resolve({ data: [] })
    let hrsPromise = Promise.resolve({ data: [] })
    let hrePromise = Promise.resolve({ data: [] })
    let amcPromise = Promise.resolve({ data: [] })
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      siPromise = supabase.from('hotel_guest_invoices').select('id, invoice_number:id, invoice_date, amount_usd:invoice_amount_usd, currency, amount:invoice_amount, contact:guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
      piPromise = supabase.from('hotel_expense_entries').select('id, invoice_number:id, invoice_date:expense_date, amount_usd, currency, amount, contact:notes').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to)
      rdrPromise = supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
      hrsPromise = supabase.from('hotel_room_stats').select('id, stat_date, room_revenue_usd, manual_room_revenue_collected_usd, currency, room_revenue').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to)
      hrePromise = supabase.from('hotel_revenue_entries').select('id, entry_date, amount_usd, currency, amount, notes, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to)
      amcPromise = supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    } else {
      siPromise = supabase.from('sales_invoices').select('id, invoice_number, invoice_date, amount_usd, currency, amount, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
      piPromise = supabase.from('purchase_invoices').select('id, invoice_number, invoice_date, amount_usd, currency, amount, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
    }

    const [{ data: si }, { data: pi }, { data: pr }, { data: rdr }, { data: hrs }, { data: hre }, { data: amc }] = await Promise.all([siPromise, piPromise, prPromise, rdrPromise, hrsPromise, hrePromise, amcPromise])

    const combined = [
      ...(si || []).map(r => ({ id: `si-${r.id}`, date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Guest Invoice' : 'Sales Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.contact || ''}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
      ...(pi || []).map(r => ({ id: `pi-${r.id}`, date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Expense' : 'Purchase Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.supplier_name_freeform || r.contact || 'Expense'}`, amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'out' })),
      ...(pr || []).map(r => ({ id: `pr-${r.id}`, date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
      ...(rdr || []).map(r => { const total = Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0)); return { id: `rdr-${r.id}`, date: r.revenue_date, type: 'F&B Revenue', desc: `${r.meal_period} F&B Revenue`, amount_usd: total, amount: total, currency: 'USD', direction: 'in' } }),
      ...(hre || []).map(r => ({ id: `hre-${r.id}`, date: r.entry_date, type: 'Ancillary Revenue', desc: r.account?.name || r.notes || 'Revenue', amount_usd: r.amount_usd, amount: r.amount, currency: r.currency, direction: 'in' })),
      ...(hrs || []).filter(r => Number(r.room_revenue_usd) > 0).map(r => ({ id: `hrs-${r.id}`, date: r.stat_date, type: 'Room Revenue', desc: 'Daily Room Revenue', amount_usd: r.room_revenue_usd, amount: r.room_revenue || r.room_revenue_usd, currency: r.currency || 'USD', direction: 'in' })),
    ]
    
    // Add AMC amortization lines
    if (amc && amc.length > 0) {
      const amcMonthlyTotal = amc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0)
      if (amcMonthlyTotal > 0) {
        const start = new Date(cp.range.from)
        const end = new Date(cp.range.to)
        let cur = new Date(start.getFullYear(), start.getMonth(), 1)
        while (cur <= end) {
          const dStr = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}-28`
          if (dStr >= cp.range.from && dStr <= cp.range.to) {
            combined.push({ id: `amc-${dStr}`, date: dStr, type: 'AMC Contract', desc: 'Amortized AMC (Monthly)', amount_usd: amcMonthlyTotal, amount: amcMonthlyTotal, currency: 'USD', direction: 'out' })
          }
          cur.setMonth(cur.getMonth() + 1)
        }
      }
    }
    
    combined.sort((a, b) => b.date.localeCompare(a.date))"""

content = content.replace(old_fetch_block, new_fetch_block)


# Now for the report generation block
old_report_block = """    let siPromise = Promise.resolve({ data: [] })
    let piPromise = Promise.resolve({ data: [] })
    let prPromise = wantReceipts ? supabase.from('payment_receipts').select('receipt_date, amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', range.from).lte('receipt_date', range.to) : Promise.resolve({ data: [] })
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      if (wantSales) siPromise = supabase.from('hotel_guest_invoices').select('invoice_number:id, invoice_date, amount_usd:invoice_amount_usd, contact:guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
      if (wantPurchase) piPromise = supabase.from('hotel_expense_entries').select('invoice_number:id, invoice_date:expense_date, amount_usd, contact:supplier_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', range.from).lte('expense_date', range.to)
    } else {
      if (wantSales) siPromise = supabase.from('sales_invoices').select('invoice_number, invoice_date, amount_usd, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
      if (wantPurchase) piPromise = supabase.from('purchase_invoices').select('invoice_number, invoice_date, amount_usd, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
    }

    const [{ data: si }, { data: pi }, { data: pr }, { data: rdr }] = await Promise.all([siPromise, piPromise, prPromise, rdrPromise])

    const combined = [
      ...(si || []).map(r => ({ date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Guest Invoice' : 'Sales Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.contact || ''}`, amount: fmt(r.amount_usd), direction: '+' })),
      ...(pi || []).map(r => ({ date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Expense' : 'Purchase Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.supplier_name_freeform || r.contact || ''}`, amount: fmt(r.amount_usd), direction: '-' })),
      ...(pr || []).map(r => ({ date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount: fmt(r.amount_usd), direction: '+' })),
    ].sort((a, b) => b.date.localeCompare(a.date))"""


new_report_block = """    let siPromise = Promise.resolve({ data: [] })
    let piPromise = Promise.resolve({ data: [] })
    let prPromise = wantReceipts ? supabase.from('payment_receipts').select('receipt_date, amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('receipt_date', range.from).lte('receipt_date', range.to) : Promise.resolve({ data: [] })
    let rdrPromise = Promise.resolve({ data: [] })
    let hrsPromise = Promise.resolve({ data: [] })
    let hrePromise = Promise.resolve({ data: [] })
    let amcPromise = Promise.resolve({ data: [] })
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      if (wantSales) siPromise = supabase.from('hotel_guest_invoices').select('invoice_number:id, invoice_date, amount_usd:invoice_amount_usd, contact:guest_name').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
      if (wantPurchase) piPromise = supabase.from('hotel_expense_entries').select('invoice_number:id, invoice_date:expense_date, amount_usd, contact:notes').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', range.from).lte('expense_date', range.to)
      if (wantSales) rdrPromise = supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to)
      if (wantSales) hrsPromise = supabase.from('hotel_room_stats').select('id, stat_date, room_revenue_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to)
      if (wantSales) hrePromise = supabase.from('hotel_revenue_entries').select('id, entry_date, amount_usd, notes, account:accounts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to)
      if (wantPurchase) amcPromise = supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    } else {
      if (wantSales) siPromise = supabase.from('sales_invoices').select('invoice_number, invoice_date, amount_usd, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
      if (wantPurchase) piPromise = supabase.from('purchase_invoices').select('invoice_number, invoice_date, amount_usd, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
    }

    const [{ data: si }, { data: pi }, { data: pr }, { data: rdr }, { data: hrs }, { data: hre }, { data: amc }] = await Promise.all([siPromise, piPromise, prPromise, rdrPromise, hrsPromise, hrePromise, amcPromise])

    const combined = [
      ...(si || []).map(r => ({ date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Guest Invoice' : 'Sales Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.contact || ''}`, amount: fmt(r.amount_usd), direction: '+' })),
      ...(pi || []).map(r => ({ date: r.invoice_date, type: ['hotel', 'restaurant'].includes(activeProduct) ? 'Expense' : 'Purchase Invoice', desc: `${(r.invoice_number || '').substring(0,8)} — ${r.contact?.name || r.supplier_name_freeform || r.contact || 'Expense'}`, amount: fmt(r.amount_usd), direction: '-' })),
      ...(pr || []).map(r => ({ date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount: fmt(r.amount_usd), direction: '+' })),
      ...(rdr || []).map(r => { const total = Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0)); return { date: r.revenue_date, type: 'F&B Revenue', desc: `${r.meal_period} F&B Revenue`, amount: fmt(total), direction: '+' } }),
      ...(hre || []).map(r => ({ date: r.entry_date, type: 'Ancillary Revenue', desc: r.account?.name || r.notes || 'Revenue', amount: fmt(r.amount_usd), direction: '+' })),
      ...(hrs || []).filter(r => Number(r.room_revenue_usd) > 0).map(r => ({ date: r.stat_date, type: 'Room Revenue', desc: 'Daily Room Revenue', amount: fmt(r.room_revenue_usd), direction: '+' })),
    ]

    // Add AMC amortization lines
    if (amc && amc.length > 0) {
      const amcMonthlyTotal = amc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0)
      if (amcMonthlyTotal > 0) {
        const start = new Date(range.from)
        const end = new Date(range.to)
        let cur = new Date(start.getFullYear(), start.getMonth(), 1)
        while (cur <= end) {
          const dStr = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}-28`
          if (dStr >= range.from && dStr <= range.to) {
            combined.push({ date: dStr, type: 'AMC Contract', desc: 'Amortized AMC (Monthly)', amount: fmt(amcMonthlyTotal), direction: '-' })
          }
          cur.setMonth(cur.getMonth() + 1)
        }
      }
    }
    
    combined.sort((a, b) => b.date.localeCompare(a.date))"""

content = content.replace(old_report_block, new_report_block)

with open('src/pages/Transactions.jsx', 'w') as f:
    f.write(content)
