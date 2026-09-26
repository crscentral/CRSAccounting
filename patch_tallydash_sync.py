import re

with open('src/pages/TallyMode/TallyDashboardEmbed.jsx', 'r') as f:
    content = f.read()

old_effect = """  useEffect(() => {
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

new_effect = """  useEffect(() => {
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

content = content.replace(old_effect, new_effect)

with open('src/pages/TallyMode/TallyDashboardEmbed.jsx', 'w') as f:
    f.write(content)
