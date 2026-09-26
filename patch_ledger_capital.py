import re

with open('src/pages/Ledger.jsx', 'r') as f:
    content = f.read()

old_load = """    let combined = data || []
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {"""

new_load = """    let combined = data || []
    
    // CAPITAL & LOANS (Applies to all modes)
    const selectedAccount = accounts.find(a => a.id === accountId)
    if (selectedAccount) {
      const isEqCont = (selectedAccount.name.toLowerCase().includes('contribution') || selectedAccount.name.toLowerCase().includes('equity')) && selectedAccount.type === 'Equity'
      const isEqDiv = (selectedAccount.name.toLowerCase().includes('dividend') || selectedAccount.name.toLowerCase().includes('draw') || selectedAccount.name.toLowerCase().includes('retained')) && selectedAccount.type === 'Equity'
      const isCash = selectedAccount.name.toLowerCase().includes('cash on hand') || selectedAccount.name.toLowerCase().includes('cash')
      
      const [{ data: oCont }, { data: oDiv }, { data: lTake }, { data: lRepay }] = await Promise.all([
        supabase.from('owner_contributions').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to),
        supabase.from('owner_dividends').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to),
        supabase.from('loans_taken').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to),
        supabase.from('loan_principal_payments').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', cp.range.from).lte('payment_date', cp.range.to)
      ])
      
      ;(oCont || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (isEqCont) combined.push({ id: `oc-eq-${r.id}`, entry_date: r.payment_date, description: `Owner Contribution: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
          if (isCash) combined.push({ id: `oc-c-${r.id}`, entry_date: r.payment_date, description: `Owner Contribution: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
        }
      })
      
      ;(oDiv || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (isEqDiv) combined.push({ id: `od-eq-${r.id}`, entry_date: r.payment_date, description: `Owner Dividend: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
          if (isCash) combined.push({ id: `od-c-${r.id}`, entry_date: r.payment_date, description: `Owner Dividend: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
        }
      })
      
      ;(lTake || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (selectedAccount.id === r.loan_account_id) combined.push({ id: `lt-l-${r.id}`, entry_date: r.payment_date, description: `Loan Taken: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
          if ((r.cash_account_id && selectedAccount.id === r.cash_account_id) || (!r.cash_account_id && isCash)) combined.push({ id: `lt-c-${r.id}`, entry_date: r.payment_date, description: `Loan Taken: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
        }
      })
      
      ;(lRepay || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (selectedAccount.id === r.loan_account_id) combined.push({ id: `lr-l-${r.id}`, entry_date: r.payment_date, description: `Loan Repayment: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
          if ((r.cash_account_id && selectedAccount.id === r.cash_account_id) || (!r.cash_account_id && isCash)) combined.push({ id: `lr-c-${r.id}`, entry_date: r.payment_date, description: `Loan Repayment: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
        }
      })
      
      combined.sort((a, b) => a.entry_date.localeCompare(b.entry_date))
    }
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {"""

content = content.replace(old_load, new_load, 1)


old_gen = """    let combined = data || []
    
    if (['hotel', 'restaurant'].includes(activeProduct) && account) {"""

new_gen = """    let combined = data || []
    
    // CAPITAL & LOANS
    if (account) {
      const isEqCont = (account.name.toLowerCase().includes('contribution') || account.name.toLowerCase().includes('equity')) && account.type === 'Equity'
      const isEqDiv = (account.name.toLowerCase().includes('dividend') || account.name.toLowerCase().includes('draw') || account.name.toLowerCase().includes('retained')) && account.type === 'Equity'
      const isCash = account.name.toLowerCase().includes('cash on hand') || account.name.toLowerCase().includes('cash')
      
      const [{ data: oCont }, { data: oDiv }, { data: lTake }, { data: lRepay }] = await Promise.all([
        supabase.from('owner_contributions').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to),
        supabase.from('owner_dividends').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to),
        supabase.from('loans_taken').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to),
        supabase.from('loan_principal_payments').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('payment_date', range.from).lte('payment_date', range.to)
      ])
      
      ;(oCont || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (isEqCont) combined.push({ id: `oc-eq-${r.id}`, entry_date: r.payment_date, description: `Owner Contribution: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
          if (isCash) combined.push({ id: `oc-c-${r.id}`, entry_date: r.payment_date, description: `Owner Contribution: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
        }
      })
      
      ;(oDiv || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (isEqDiv) combined.push({ id: `od-eq-${r.id}`, entry_date: r.payment_date, description: `Owner Dividend: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
          if (isCash) combined.push({ id: `od-c-${r.id}`, entry_date: r.payment_date, description: `Owner Dividend: ${r.owner_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
        }
      })
      
      ;(lTake || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (account.id === r.loan_account_id) combined.push({ id: `lt-l-${r.id}`, entry_date: r.payment_date, description: `Loan Taken: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
          if ((r.cash_account_id && account.id === r.cash_account_id) || (!r.cash_account_id && isCash)) combined.push({ id: `lt-c-${r.id}`, entry_date: r.payment_date, description: `Loan Taken: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
        }
      })
      
      ;(lRepay || []).forEach(r => {
        if (Number(r.amount_usd) > 0) {
          if (account.id === r.loan_account_id) combined.push({ id: `lr-l-${r.id}`, entry_date: r.payment_date, description: `Loan Repayment: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
          if ((r.cash_account_id && account.id === r.cash_account_id) || (!r.cash_account_id && isCash)) combined.push({ id: `lr-c-${r.id}`, entry_date: r.payment_date, description: `Loan Repayment: ${r.lender_name}`, currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
        }
      })
      
      combined.sort((a, b) => a.entry_date.localeCompare(b.entry_date))
    }
    
    if (['hotel', 'restaurant'].includes(activeProduct) && account) {"""

content = content.replace(old_gen, new_gen, 1)

with open('src/pages/Ledger.jsx', 'w') as f:
    f.write(content)
