import re

with open('src/pages/TallyMode/TallyDashboardEmbed.jsx', 'r') as f:
    content = f.read()

# Make it exactly like Dashboard.jsx
old_effect = """  useEffect(() => {
    if (activeCompany) {
      Promise.all([
        supabase.from('ledger_entries').select('debit_usd, credit_usd, accounts!inner(type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
        !['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('sales_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] }),
        !['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('purchase_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] })
      ]).then(([ { data: entries }, { data: sales }, { data: purchases } ]) => {
        let rev = 0, exp = 0, ast = 0, liab = 0, eq = 0
        
        if (entries) {
          entries.forEach(e => {
            const dr = Number(e.debit_usd) || 0
            const cr = Number(e.credit_usd) || 0
            const type = e.accounts?.type
            
            if (type === 'Asset') ast += (dr - cr)
            if (type === 'Liability') liab += (cr - dr)
            if (type === 'Equity') eq += (cr - dr)
            
            // For hotel/restaurant, read rev/exp from ledger
            if (['hotel', 'restaurant'].includes(activeProduct)) {
              if (type === 'Revenue') rev += (cr - dr)
              if (type === 'Expense') exp += (dr - cr)
            }
          })
        }

        // For basic, read rev/exp from invoices
        if (!['hotel', 'restaurant'].includes(activeProduct)) {
          rev = (sales || []).reduce((sum, i) => sum + (Number(i.amount_usd) || 0), 0)
          exp = (purchases || []).reduce((sum, i) => sum + (Number(i.amount_usd) || 0), 0)
        }
        
        setData({ revenue: rev, expenses: exp, assets: ast, liabilities: liab, equity: eq })
      })
    }
  }, [activeCompany, activeProduct, cp.range.from, cp.range.to])"""

new_effect = """  useEffect(() => {
    if (activeCompany) {
      Promise.all([
        supabase.from('accounts').select('id, type').eq('company_id', activeCompany.id).eq('product', activeProduct),
        supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
        !['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('sales_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] }),
        !['hotel', 'restaurant'].includes(activeProduct) ? supabase.from('purchase_invoices').select('amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to) : Promise.resolve({ data: [] })
      ]).then(([ { data: accounts }, { data: entries }, { data: sales }, { data: purchases } ]) => {
        let rev = 0, exp = 0, ast = 0, liab = 0, eq = 0
        
        const balances = {}
        if (entries) {
          entries.forEach(e => {
            balances[e.account_id] = (balances[e.account_id] || 0) + Number(e.debit_usd) - Number(e.credit_usd)
          })
        }
        
        const sumAccs = (type) => (accounts || []).filter(a => a.type === type).reduce((s, a) => s + (balances[a.id] || 0), 0)

        ast = sumAccs('Asset')
        liab = -sumAccs('Liability') // show as positive if credit
        eq = -sumAccs('Equity') // show as positive if credit
        
        if (['hotel', 'restaurant'].includes(activeProduct)) {
          rev = -sumAccs('Revenue')
          exp = sumAccs('Expenses')
        } else {
          rev = (sales || []).reduce((sum, i) => sum + (Number(i.amount_usd) || 0), 0)
          exp = (purchases || []).reduce((sum, i) => sum + (Number(i.amount_usd) || 0), 0)
        }
        
        setData({ revenue: rev, expenses: exp, assets: ast, liabilities: liab, equity: eq })
      })
    }
  }, [activeCompany, activeProduct, cp.range.from, cp.range.to])"""

# Since old_effect is from `patch_tallydash_sync.py` which WAS NEVER COMMITTED, 
# wait! I need to replace the ACTUAL old effect in `TallyDashboardEmbed.jsx`.

with open('src/pages/TallyMode/TallyDashboardEmbed.jsx', 'r') as f2:
    actual_content = f2.read()

actual_old = """  useEffect(() => {
    if (activeCompany) {
      supabase.from('ledger_entries')
        .select('debit_usd, credit_usd, accounts!inner(type)')
        .eq('company_id', activeCompany.id)
        .eq('product', activeProduct)
        .gte('entry_date', cp.range.from)
        .lte('entry_date', cp.range.to)
        .then(({ data: entries }) => {
          if (!entries) return
          let rev = 0, exp = 0, ast = 0, liab = 0, eq = 0
          
          entries.forEach(e => {
            const dr = Number(e.debit_usd) || 0
            const cr = Number(e.credit_usd) || 0
            const type = e.accounts?.type
            
            if (type === 'Revenue') rev += (cr - dr)
            if (type === 'Expense') exp += (dr - cr)
            if (type === 'Asset') ast += (dr - cr)
            if (type === 'Liability') liab += (cr - dr)
            if (type === 'Equity') eq += (cr - dr)
          })
          
          setData({ revenue: rev, expenses: exp, assets: ast, liabilities: liab, equity: eq })
        })
    }
  }, [activeCompany, activeProduct, cp.range.from, cp.range.to])"""

actual_content = actual_content.replace(actual_old, new_effect)

with open('src/pages/TallyMode/TallyDashboardEmbed.jsx', 'w') as f3:
    f3.write(actual_content)

