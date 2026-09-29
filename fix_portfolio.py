import re

def patch():
    with open('src/pages/PortfolioDashboard.jsx', 'r') as f:
        content = f.read()

    # Find the end of the Promise.all
    old_code = """
    const balances = {}
    ;(entries || []).forEach(e => { balances[e.account_id] = (balances[e.account_id] || 0) + Number(e.debit_usd) - Number(e.credit_usd) })
    const byType = (type) => (accounts || []).filter(a => a.type === type)
    const sumAccs = (list) => list.reduce((s, a) => s + (balances[a.id] || 0), 0)

    const revenue = -sumAccs(byType('Revenue'))
    const belowLine = byType('Expenses').filter(a => ['Below GOP', 'Below EBITDA'].includes(a.subtype))
    const otherBelowLineAccs = belowLine.filter(a => !DA_INTEREST_NAMES.includes(a.name))
    const operatingAccs = byType('Expenses').filter(a => !['Below GOP', 'Below EBITDA'].includes(a.subtype))
    const operatingExpenses = sumAccs(operatingAccs)
    const otherBelowLine = sumAccs(otherBelowLineAccs)
    const totalExpenses = sumAccs(byType('Expenses'))
    const gop = revenue - operatingExpenses
    const ebitda = gop - otherBelowLine
"""
    
    new_code = """
    const balances = {}
    const ignoredSources = ['restaurant_revenue', 'hotel_room_stats', 'hotel_revenue_entry', 'hotel_expense_entry', 'hotel_amc_contract', 'hotel_guest_invoice', 'owner_contribution', 'owner_dividend', 'loan_taken', 'loan_principal']
    const filteredEntries = (entries || []).filter(e => {
      if (['hotel', 'restaurant'].includes(product)) return !ignoredSources.includes(e.source_type)
      return true
    })
    ;(filteredEntries || []).forEach(e => { balances[e.account_id] = (balances[e.account_id] || 0) + Number(e.debit_usd) - Number(e.credit_usd) })
    
    const byType = (type) => (accounts || []).filter(a => a.type === type)
    const sumAccs = (list) => list.reduce((s, a) => s + (balances[a.id] || 0), 0)

    let revenue = -sumAccs(byType('Revenue'))
    let totalExpenses = sumAccs(byType('Expenses'))
    
    let operatingExpenses = sumAccs(byType('Expenses').filter(a => !['Below GOP', 'Below EBITDA'].includes(a.subtype)))
    let otherBelowLine = sumAccs(byType('Expenses').filter(a => ['Below GOP', 'Below EBITDA'].includes(a.subtype) && !DA_INTEREST_NAMES.includes(a.name)))
    
    let invoicesRaised = (salesInv || []).length
    let collected = (receipts || []).reduce((s, r) => s + Number(r.amount_usd), 0)

    if (['hotel', 'restaurant'].includes(product)) {
      const [{ data: hrs }, { data: hre }, { data: rdr }, { data: hee }, { data: amc }, { data: hgi }, { data: pur }] = await Promise.all([
        supabase.from('hotel_room_stats').select('*').eq('company_id', companyId).eq('product', product).gte('stat_date', range.from).lte('stat_date', range.to),
        supabase.from('hotel_revenue_entries').select('*').eq('company_id', companyId).eq('product', product).gte('entry_date', range.from).lte('entry_date', range.to),
        supabase.from('restaurant_daily_revenue').select('*').eq('company_id', companyId).eq('product', product).gte('revenue_date', range.from).lte('revenue_date', range.to),
        supabase.from('hotel_expense_entries').select('*').eq('company_id', companyId).eq('product', product).gte('expense_date', range.from).lte('expense_date', range.to),
        supabase.from('hotel_amc_contracts').select('*').eq('company_id', companyId).eq('product', product),
        supabase.from('hotel_guest_invoices').select('*').eq('company_id', companyId).eq('product', product).gte('invoice_date', range.from).lte('invoice_date', range.to),
        supabase.from('purchase_invoices').select('*').eq('company_id', companyId).eq('product', product).gte('invoice_date', range.from).lte('invoice_date', range.to)
      ])
      
      const r_hrs = (hrs || []).reduce((s, r) => s + Number(r.room_revenue_usd || 0), 0)
      const r_hre = (hre || []).reduce((s, r) => s + Number(r.amount_usd || 0), 0)
      const r_rdr = (rdr || []).reduce((s, r) => s + (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))), 0)
      
      revenue += r_hrs + r_hre + r_rdr
      
      // Expenses
      // For AMC, we need monthsInView
      const monthsInView = (range.to.substring(0,4) - range.from.substring(0,4)) * 12 + (range.to.substring(5,7) - range.from.substring(5,7)) + 1
      const e_amc = (amc || []).reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * (isNaN(monthsInView)?12:monthsInView)
      const e_hee = (hee || []).reduce((s, r) => s + Number(r.amount_usd || 0), 0)
      const e_pur = (pur || []).reduce((s, r) => s + Number(r.amount_usd || 0), 0)
      
      totalExpenses += e_amc + e_hee + e_pur
      operatingExpenses += e_amc + e_hee + e_pur // Just putting them all in operating for simplicity in portfolio view
      
      // Invoices
      invoicesRaised += (hgi || []).length
      
      // Collected
      const c_hrs = (hrs || []).reduce((s, r) => s + Number(r.room_revenue_collected_usd || 0), 0)
      const c_hre = (hre || []).reduce((s, r) => s + Number(r.collected_usd || 0), 0)
      const c_rdr = (rdr || []).reduce((s, r) => s + Number(r.collected_usd || 0), 0)
      const c_hgi = (hgi || []).reduce((s, r) => s + Number(r.collected_amount_usd || 0), 0)
      
      collected += c_hrs + c_hre + c_rdr + c_hgi
    }

    const gop = revenue - operatingExpenses
    const ebitda = gop - otherBelowLine
"""
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        # We also need to fix the select for ledger_entries to include source_type
        content = content.replace("select('account_id, debit_usd, credit_usd')", "select('account_id, debit_usd, credit_usd, source_type')")
        
        with open('src/pages/PortfolioDashboard.jsx', 'w') as f:
            f.write(content)
        print("Patched PortfolioDashboard.jsx")
    else:
        print("Could not find old code block")

patch()
