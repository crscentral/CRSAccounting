import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

# 1. Update loadData to fetch restRev and accs
old_loaddata_1 = """    const [{ data: s }, { data: p }, { data: entries }] = await Promise.all([
      supabase.from('sales_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('purchase_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(id, code, name, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
    ])
    setSales(s || []); setPurchases(p || [])"""

new_loaddata_1 = """    const [{ data: s }, { data: p }, { data: entries }, { data: accs }, { data: restRev }] = await Promise.all([
      supabase.from('sales_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('purchase_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(id, code, name, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
      activeProduct === 'hotel' ? supabase.from('accounts').select('id, code, name, type').eq('company_id', activeCompany.id).eq('product', 'hotel') : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('restaurant_daily_revenue').select('food_amount_usd, beverage_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to) : Promise.resolve({ data: [] })
    ])
    
    let salesData = s || []
    if (activeProduct === 'hotel' && restRev) {
      restRev.forEach(r => {
        const total = (Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0)
        if (total > 0) salesData.push({ amount_usd: total })
      })
    }
    setSales(salesData); setPurchases(p || [])"""

content = content.replace(old_loaddata_1, new_loaddata_1)

# 2. Update the breakdown in loadData
old_loaddata_2 = """    const revMap = {}, expMap = {}
    ;(entries || []).forEach(e => {
      const acc = e.accounts
      if (!acc) return
      const net = Number(e.debit_usd) - Number(e.credit_usd)
      if (acc.type === 'Revenue') {
        revMap[acc.id] = revMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }
        revMap[acc.id].amount += -net // revenue is credit-normal
      } else if (acc.type === 'Expenses') {
        expMap[acc.id] = expMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }
        expMap[acc.id].amount += net
      }
    })
    setRevenueBreakdown(Object.values(revMap).sort((a,b)=>a.code.localeCompare(b.code)))
    setExpenseBreakdown(Object.values(expMap).sort((a,b)=>a.code.localeCompare(b.code)))"""

new_loaddata_2 = """    const revMap = {}, expMap = {}
    ;(entries || []).forEach(e => {
      const acc = e.accounts
      if (!acc) return
      const net = Number(e.debit_usd) - Number(e.credit_usd)
      if (acc.type === 'Revenue') {
        revMap[acc.id] = revMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }
        revMap[acc.id].amount += -net // revenue is credit-normal
      } else if (acc.type === 'Expenses') {
        expMap[acc.id] = expMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }
        expMap[acc.id].amount += net
      }
    })
    
    if (activeProduct === 'hotel' && restRev && accs) {
      const acc4019 = accs.find(a => a.code === '4019')
      const acc4011 = accs.find(a => a.code === '4011')
      restRev.forEach(r => {
        const f = Number(r.food_amount_usd) || 0
        const b = Number(r.beverage_amount_usd) || 0
        if (f > 0 && acc4019) {
          revMap[acc4019.id] = revMap[acc4019.id] || { code: acc4019.code, name: acc4019.name, amount: 0 }
          revMap[acc4019.id].amount += f
        }
        if (b > 0 && acc4011) {
          revMap[acc4011.id] = revMap[acc4011.id] || { code: acc4011.code, name: acc4011.name, amount: 0 }
          revMap[acc4011.id].amount += b
        }
      })
    }
    
    setRevenueBreakdown(Object.values(revMap).sort((a,b)=>a.code.localeCompare(b.code)))
    setExpenseBreakdown(Object.values(expMap).sort((a,b)=>a.code.localeCompare(b.code)))"""

content = content.replace(old_loaddata_2, new_loaddata_2)


# 3. Update generateReport to fetch restRev and accs
old_report_1 = """    const [{ data: s }, { data: p }, { data: entries }] = await Promise.all([
      supabase.from('sales_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('purchase_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(id, code, name, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to),
    ])
    const rev = (s || []).reduce((s2, i) => s2 + Number(i.amount_usd), 0)
    const exp = (p || []).reduce((s2, i) => s2 + Number(i.amount_usd), 0)"""

new_report_1 = """    const [{ data: s }, { data: p }, { data: entries }, { data: accs }, { data: restRev }] = await Promise.all([
      supabase.from('sales_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('purchase_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to),
      supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(id, code, name, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to),
      activeProduct === 'hotel' ? supabase.from('accounts').select('id, code, name, type').eq('company_id', activeCompany.id).eq('product', 'hotel') : Promise.resolve({ data: [] }),
      activeProduct === 'hotel' ? supabase.from('restaurant_daily_revenue').select('food_amount_usd, beverage_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to) : Promise.resolve({ data: [] })
    ])
    
    let salesData = s || []
    if (activeProduct === 'hotel' && restRev) {
      restRev.forEach(r => {
        const total = (Number(r.food_amount_usd) || 0) + (Number(r.beverage_amount_usd) || 0)
        if (total > 0) salesData.push({ amount_usd: total })
      })
    }
    const rev = salesData.reduce((s2, i) => s2 + Number(i.amount_usd), 0)
    const exp = (p || []).reduce((s2, i) => s2 + Number(i.amount_usd), 0)"""

content = content.replace(old_report_1, new_report_1)

# 4. Update the breakdown in generateReport
old_report_2 = """    const revMap = {}, expMap = {}
    ;(entries || []).forEach(e => {
      const acc = e.accounts
      if (!acc) return
      const net = Number(e.debit_usd) - Number(e.credit_usd)
      if (acc.type === 'Revenue') { revMap[acc.id] = revMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }; revMap[acc.id].amount += -net }
      else if (acc.type === 'Expenses') { expMap[acc.id] = expMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }; expMap[acc.id].amount += net }
    })"""

new_report_2 = """    const revMap = {}, expMap = {}
    ;(entries || []).forEach(e => {
      const acc = e.accounts
      if (!acc) return
      const net = Number(e.debit_usd) - Number(e.credit_usd)
      if (acc.type === 'Revenue') { revMap[acc.id] = revMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }; revMap[acc.id].amount += -net }
      else if (acc.type === 'Expenses') { expMap[acc.id] = expMap[acc.id] || { code: acc.code, name: acc.name, amount: 0 }; expMap[acc.id].amount += net }
    })
    
    if (activeProduct === 'hotel' && restRev && accs) {
      const acc4019 = accs.find(a => a.code === '4019')
      const acc4011 = accs.find(a => a.code === '4011')
      restRev.forEach(r => {
        const f = Number(r.food_amount_usd) || 0
        const b = Number(r.beverage_amount_usd) || 0
        if (f > 0 && acc4019) { revMap[acc4019.id] = revMap[acc4019.id] || { code: acc4019.code, name: acc4019.name, amount: 0 }; revMap[acc4019.id].amount += f }
        if (b > 0 && acc4011) { revMap[acc4011.id] = revMap[acc4011.id] || { code: acc4011.code, name: acc4011.name, amount: 0 }; revMap[acc4011.id].amount += b }
      })
    }"""

content = content.replace(old_report_2, new_report_2)


with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
