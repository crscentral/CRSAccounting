import re

def patch():
    with open('src/pages/Ledger.jsx', 'r') as f:
        content = f.read()

    # 1. Fix AR injection for guest invoices to only push 1 entry (Pending amount)
    old_hgi = """        if ((selectedAccount.name || '').toLowerCase().includes('accounts receivable') || (selectedAccount.name || '').toLowerCase().includes('guest ledger')) {
          const { data: hgi } = await supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
          ;(hgi || []).forEach(i => {
            if (Number(i.invoice_amount_usd) > 0) {
              combined.push({ id: `hgi-inv-${i.id}`, entry_date: i.invoice_date, description: `Invoice ${(i.invoice_number || '').substring(0,8)} - ${i.guest_name}`, currency: i.currency || 'USD', debit_usd: i.invoice_amount_usd, credit_usd: 0 })
            }
            if (Number(i.collected_amount_usd) > 0) {
              combined.push({ id: `hgi-col-${i.id}`, entry_date: i.invoice_date, description: `Payment Collected - ${(i.invoice_number || '').substring(0,8)}`, currency: i.currency || 'USD', debit_usd: 0, credit_usd: i.collected_amount_usd })
            }
          })"""
          
    new_hgi = """        if ((selectedAccount.name || '').toLowerCase().includes('accounts receivable') || (selectedAccount.name || '').toLowerCase().includes('guest ledger')) {
          const { data: hgi } = await supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
          ;(hgi || []).forEach(i => {
            const pending = Number(i.invoice_amount_usd || 0) - Number(i.collected_amount_usd || 0);
            if (pending > 0) {
              combined.push({ id: `hgi-inv-${i.id}`, entry_date: i.invoice_date, description: `Invoice ${(i.invoice_number || '').substring(0,8)} - ${i.guest_name}`, currency: i.currency || 'USD', debit_usd: pending, credit_usd: 0 })
            } else if (pending < 0) {
              combined.push({ id: `hgi-inv-${i.id}`, entry_date: i.invoice_date, description: `Invoice ${(i.invoice_number || '').substring(0,8)} - ${i.guest_name}`, currency: i.currency || 'USD', debit_usd: 0, credit_usd: Math.abs(pending) })
            }
          })"""

    content = content.replace(old_hgi, new_hgi)
    
    # Do the same for the Report generator version
    old_hgi_rep = """      if ((account.name || '').toLowerCase().includes('accounts receivable') || (account.name || '').toLowerCase().includes('guest ledger')) {
        const { data: hgi } = await supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
        ;(hgi || []).forEach(i => {
          if (Number(i.invoice_amount_usd) > 0) {
            combined.push({ id: `hgi-inv-${i.id}`, entry_date: i.invoice_date, description: `Invoice ${(i.invoice_number || '').substring(0,8)} - ${i.guest_name}`, currency: i.currency || 'USD', debit_usd: i.invoice_amount_usd, credit_usd: 0 })
          }
          if (Number(i.collected_amount_usd) > 0) {
            combined.push({ id: `hgi-col-${i.id}`, entry_date: i.invoice_date, description: `Payment Collected - ${(i.invoice_number || '').substring(0,8)}`, currency: i.currency || 'USD', debit_usd: 0, credit_usd: i.collected_amount_usd })
          }
        })"""
    new_hgi_rep = """      if ((account.name || '').toLowerCase().includes('accounts receivable') || (account.name || '').toLowerCase().includes('guest ledger')) {
        const { data: hgi } = await supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
        ;(hgi || []).forEach(i => {
          const pending = Number(i.invoice_amount_usd || 0) - Number(i.collected_amount_usd || 0);
          if (pending > 0) {
            combined.push({ id: `hgi-inv-${i.id}`, entry_date: i.invoice_date, description: `Invoice ${(i.invoice_number || '').substring(0,8)} - ${i.guest_name}`, currency: i.currency || 'USD', debit_usd: pending, credit_usd: 0 })
          } else if (pending < 0) {
            combined.push({ id: `hgi-inv-${i.id}`, entry_date: i.invoice_date, description: `Invoice ${(i.invoice_number || '').substring(0,8)} - ${i.guest_name}`, currency: i.currency || 'USD', debit_usd: 0, credit_usd: Math.abs(pending) })
          }
        })"""
    content = content.replace(old_hgi_rep, new_hgi_rep)
    
    # 2. Fix Double-Counting in AR (remove hrs and rdr uncol from AR)
    # The block looks like: else if (isAr) { ;(hrs || []).forEach(...) }
    old_ar_inject = """          } else if (isAr) {
            ;(hrs || []).forEach(r => {
               const rev = Number(r.room_revenue_usd) || 0
               const col = Number(r.manual_room_revenue_collected_usd) || rev
               const uncol = Math.max(0, rev - col)
               if (uncol > 0) combined.push({ id: `hrs-ar-${r.id}`, entry_date: r.stat_date, description: 'Room Revenue Uncollected', currency: r.currency || 'USD', debit_usd: uncol, credit_usd: 0 })
            })
            ;(rdr || []).forEach(r => {
               const total = (Number(r.food_amount_usd)||0) + (Number(r.beverage_amount_usd)||0) + (Number(r.other_amount_usd)||0)
               const col = r.collected_usd !== null ? Number(r.collected_usd) : total
               const uncol = Math.max(0, total - col)
               if (uncol > 0) combined.push({ id: `rdr-ar-${r.id}`, entry_date: r.revenue_date, description: 'Restaurant Revenue Uncollected', currency: r.currency || 'USD', debit_usd: uncol, credit_usd: 0 })
            })
          }"""
          
    # Replace it with a simpler one that just handles restaurant revenue because restaurant doesn't have guest invoices
    # Wait, the user said "also for CRS Restaurant accounting". So Restaurant accounting ALSO needs its uncol handled correctly.
    # For Restaurant, uncollected = total - col. Is this 1 line? Yes, it already is 1 line.
    # The user says "And for that 1 transaction I see 3 entries are created... fix it for Hotel and Restaurant". 
    # Ah, the 3 entries the user complains about are exactly what happens if they use BOTH Guest Invoices AND Room Revenue for the SAME day.
    # If they only want Guest Invoices to feed AR, what about Restaurant? Restaurant doesn't have guest invoices.
    # If Restaurant doesn't have guest invoices, then `rdr-ar` is already just 1 line ("Restaurant Revenue Uncollected").
    # For Hotel, we MUST comment out the `hrs-ar` because `hgi` is covering it.
    new_ar_inject = """          } else if (isAr) {
            // Disabled hotel_room_stats AR injection to prevent double counting with Guest Invoices
            ;(rdr || []).forEach(r => {
               const total = (Number(r.food_amount_usd)||0) + (Number(r.beverage_amount_usd)||0) + (Number(r.other_amount_usd)||0)
               const col = r.collected_usd !== null ? Number(r.collected_usd) : total
               const uncol = total - col
               if (uncol > 0) {
                 combined.push({ id: `rdr-ar-${r.id}`, entry_date: r.revenue_date, description: 'Restaurant Revenue Uncollected', currency: r.currency || 'USD', debit_usd: uncol, credit_usd: 0 })
               } else if (uncol < 0) {
                 combined.push({ id: `rdr-ar-${r.id}`, entry_date: r.revenue_date, description: 'Restaurant Overcollection', currency: r.currency || 'USD', debit_usd: 0, credit_usd: Math.abs(uncol) })
               }
            })
          }"""
    content = content.replace(old_ar_inject, new_ar_inject)
    
    # 3. Fix Running Balance logic
    old_bal = """  const withBalance = entries.map(e => {
    return { ...e, balance: Number(e.debit_usd) - Number(e.credit_usd) }
  })"""
    new_bal = """  let running = 0;
  const withBalance = entries.slice().reverse().map(e => {
    running += Number(e.debit_usd) - Number(e.credit_usd)
    return { ...e, balance: running }
  }).reverse()"""
    # Wait, the entries are sorted by date descending? Let's check the columns and rendering.
    # The UI shows latest dates at the top. If latest is at the top, a running balance from the top adds up backwards.
    # If they are sorted descending, `e[0]` is the latest. So the oldest is `e[e.length-1]`.
    # Therefore, we start from the bottom, accumulate, and store.
    # `slice().reverse().map().reverse()` does exactly this!
    content = content.replace(old_bal, new_bal)
    
    # Also fix it for the report generator
    old_rep_bal = """    const rows = combined.map(e => {
      const lineBalance = Number(e.debit_usd) - Number(e.credit_usd)
      const balStr = lineBalance < 0 ? `-${fmt(Math.abs(lineBalance))}` : fmt(lineBalance); 
      return [e.entry_date, e.description, e.currency, Number(e.debit_usd) ? fmt(e.debit_usd) : '—', Number(e.credit_usd) ? fmt(e.credit_usd) : '—', balStr]
    })"""
    new_rep_bal = """    let repRun = 0;
    const rows = combined.slice().reverse().map(e => {
      repRun += Number(e.debit_usd) - Number(e.credit_usd)
      return { ...e, balance: repRun }
    }).reverse().map(e => {
      const balStr = e.balance < 0 ? `-${fmt(Math.abs(e.balance))}` : fmt(e.balance); 
      return [e.entry_date, e.description, e.currency, Number(e.debit_usd) ? fmt(e.debit_usd) : '—', Number(e.credit_usd) ? fmt(e.credit_usd) : '—', balStr]
    })"""
    content = content.replace(old_rep_bal, new_rep_bal)

    with open('src/pages/Ledger.jsx', 'w') as f:
        f.write(content)
        print("Patched Ledger.jsx")

patch()
