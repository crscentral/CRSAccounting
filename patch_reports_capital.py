import re

with open('src/pages/Reports.jsx', 'r') as f:
    content = f.read()

# We need to insert the Capital & Loans logic.
# The previous loadData has:
#    let combined = entries || []
#    
#    if (['hotel', 'restaurant'].includes(activeProduct)) { ... }
#
# We'll just insert the capital fetch right after let combined = entries || []

old_inject = """    let combined = entries || []
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {"""

new_inject = """    let combined = entries || []
    
    // CAPITAL & LOANS (Applies to all products)
    const eqContAcc = accs.find(a => (a.name.toLowerCase().includes('contribution') || a.name.toLowerCase().includes('equity')) && a.type === 'Equity')
    const eqDivAcc = accs.find(a => (a.name.toLowerCase().includes('dividend') || a.name.toLowerCase().includes('draw') || a.name.toLowerCase().includes('retained')) && a.type === 'Equity')
    const capCashAcc = accs.find(a => a.name.toLowerCase().includes('cash on hand') || a.name.toLowerCase().includes('cash'))
    
    const [{ data: oCont }, { data: oDiv }, { data: lTake }, { data: lRepay }] = await Promise.all([
      supabase.from('owner_contributions').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('owner_dividends').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('loans_taken').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('loan_principal_payments').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    ])
    
    ;(oCont || []).forEach(r => {
      if (Number(r.amount_usd) > 0) {
        if (eqContAcc) combined.push({ account_id: eqContAcc.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.payment_date, accounts: { type: eqContAcc.type } })
        if (capCashAcc) combined.push({ account_id: capCashAcc.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.payment_date, accounts: { type: capCashAcc.type } })
      }
    })
    
    ;(oDiv || []).forEach(r => {
      if (Number(r.amount_usd) > 0) {
        if (eqDivAcc) combined.push({ account_id: eqDivAcc.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.payment_date, accounts: { type: eqDivAcc.type } })
        if (capCashAcc) combined.push({ account_id: capCashAcc.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.payment_date, accounts: { type: capCashAcc.type } })
      }
    })
    
    ;(lTake || []).forEach(r => {
      if (Number(r.amount_usd) > 0) {
        const liabAcc = accs.find(a => a.id === r.loan_account_id)
        if (liabAcc) combined.push({ account_id: liabAcc.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.payment_date, accounts: { type: liabAcc.type } })
        const cashA = accs.find(a => a.id === r.cash_account_id) || capCashAcc
        if (cashA) combined.push({ account_id: cashA.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.payment_date, accounts: { type: cashA.type } })
      }
    })
    
    ;(lRepay || []).forEach(r => {
      if (Number(r.amount_usd) > 0) {
        const liabAcc = accs.find(a => a.id === r.loan_account_id)
        if (liabAcc) combined.push({ account_id: liabAcc.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.payment_date, accounts: { type: liabAcc.type } })
        const cashA = accs.find(a => a.id === r.cash_account_id) || capCashAcc
        if (cashA) combined.push({ account_id: cashA.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.payment_date, accounts: { type: cashA.type } })
      }
    })
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {"""

content = content.replace(old_inject, new_inject, 1)

old_inject2 = """    let combined = entries || []
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {"""

new_inject2 = """    let combined = entries || []
    
    // CAPITAL & LOANS
    const eqContAcc = accounts.find(a => (a.name.toLowerCase().includes('contribution') || a.name.toLowerCase().includes('equity')) && a.type === 'Equity')
    const eqDivAcc = accounts.find(a => (a.name.toLowerCase().includes('dividend') || a.name.toLowerCase().includes('draw') || a.name.toLowerCase().includes('retained')) && a.type === 'Equity')
    const capCashAcc = accounts.find(a => a.name.toLowerCase().includes('cash on hand') || a.name.toLowerCase().includes('cash'))
    
    const [{ data: oCont }, { data: oDiv }, { data: lTake }, { data: lRepay }] = await Promise.all([
      supabase.from('owner_contributions').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('owner_dividends').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('loans_taken').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
      supabase.from('loan_principal_payments').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    ])
    
    ;(oCont || []).forEach(r => {
      if (Number(r.amount_usd) > 0) {
        if (eqContAcc) combined.push({ account_id: eqContAcc.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.payment_date, accounts: { type: eqContAcc.type } })
        if (capCashAcc) combined.push({ account_id: capCashAcc.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.payment_date, accounts: { type: capCashAcc.type } })
      }
    })
    
    ;(oDiv || []).forEach(r => {
      if (Number(r.amount_usd) > 0) {
        if (eqDivAcc) combined.push({ account_id: eqDivAcc.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.payment_date, accounts: { type: eqDivAcc.type } })
        if (capCashAcc) combined.push({ account_id: capCashAcc.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.payment_date, accounts: { type: capCashAcc.type } })
      }
    })
    
    ;(lTake || []).forEach(r => {
      if (Number(r.amount_usd) > 0) {
        const liabAcc = accounts.find(a => a.id === r.loan_account_id)
        if (liabAcc) combined.push({ account_id: liabAcc.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.payment_date, accounts: { type: liabAcc.type } })
        const cashA = accounts.find(a => a.id === r.cash_account_id) || capCashAcc
        if (cashA) combined.push({ account_id: cashA.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.payment_date, accounts: { type: cashA.type } })
      }
    })
    
    ;(lRepay || []).forEach(r => {
      if (Number(r.amount_usd) > 0) {
        const liabAcc = accounts.find(a => a.id === r.loan_account_id)
        if (liabAcc) combined.push({ account_id: liabAcc.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.payment_date, accounts: { type: liabAcc.type } })
        const cashA = accounts.find(a => a.id === r.cash_account_id) || capCashAcc
        if (cashA) combined.push({ account_id: cashA.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.payment_date, accounts: { type: cashA.type } })
      }
    })
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {"""

content = content.replace(old_inject2, new_inject2, 1)

with open('src/pages/Reports.jsx', 'w') as f:
    f.write(content)

