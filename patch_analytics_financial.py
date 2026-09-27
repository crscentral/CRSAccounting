import re

for filename in ['src/pages/Analytics.jsx', 'src/pages/FinancialPerformance.jsx']:
    with open(filename, 'r') as f:
        content = f.read()

    if filename == 'src/pages/Analytics.jsx':
        # Analytics has two places where it calculates expenses for hotel/restaurant
        # 1. loadData (line 58ish)
        old_expenses1 = """      const amcTotal = hamcSel.reduce((s2, r) => s2 + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
      expenses = heeSel.reduce((s2, e) => s2 + Number(e.amount_usd), 0) + amcTotal"""
        new_expenses1 = """      const amcTotal = hamcSel.reduce((s2, r) => s2 + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
      expenses = heeSel.reduce((s2, e) => s2 + Number(e.amount_usd), 0) + amcTotal + pSel.reduce((s2, i) => s2 + Number(i.amount_usd || 0), 0)"""
        content = content.replace(old_expenses1, new_expenses1)

    if filename == 'src/pages/FinancialPerformance.jsx':
        old_expenses2 = """      const amcTotal = hamcSel.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
      totalExpenses = heeSel.reduce((s, e) => s + Number(e.amount_usd), 0) + amcTotal"""
        new_expenses2 = """      const amcTotal = hamcSel.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
      totalExpenses = heeSel.reduce((s, e) => s + Number(e.amount_usd), 0) + amcTotal + pSel.reduce((s, i) => s + Number(i.amount_usd || 0), 0)"""
        content = content.replace(old_expenses2, new_expenses2)
        
        # FinancialPerformance uses `allHee` for monthly loop. Does it use `allP`?
        old_monthly2 = """    const allMonths = {}
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      allHgi.forEach(i => { const k = (i.invoice_date || '').slice(0, 7); allMonths[k] = allMonths[k] || { Rev: 0, Exp: 0 }; allMonths[k].Rev += Number(i.invoice_amount_usd || 0) })
      allHrs.forEach(i => { const k = (i.stat_date || '').slice(0, 7); allMonths[k] = allMonths[k] || { Rev: 0, Exp: 0 }; allMonths[k].Rev += Number(i.room_revenue_usd || 0) })
      allHre.forEach(i => { const k = (i.entry_date || '').slice(0, 7); allMonths[k] = allMonths[k] || { Rev: 0, Exp: 0 }; allMonths[k].Rev += Number(i.amount_usd || 0) })
      allRdr.forEach(i => { const k = (i.revenue_date || '').slice(0, 7); allMonths[k] = allMonths[k] || { Rev: 0, Exp: 0 }; allMonths[k].Rev += Number(i.total_amount_usd || 0) })
      
      allHee.forEach(i => { const k = (i.expense_date || '').slice(0, 7); allMonths[k] = allMonths[k] || { Rev: 0, Exp: 0 }; allMonths[k].Exp += Number(i.amount_usd || 0) })"""
      
        new_monthly2 = """    const allMonths = {}
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      allHgi.forEach(i => { const k = (i.invoice_date || '').slice(0, 7); allMonths[k] = allMonths[k] || { Rev: 0, Exp: 0 }; allMonths[k].Rev += Number(i.invoice_amount_usd || 0) })
      allHrs.forEach(i => { const k = (i.stat_date || '').slice(0, 7); allMonths[k] = allMonths[k] || { Rev: 0, Exp: 0 }; allMonths[k].Rev += Number(i.room_revenue_usd || 0) })
      allHre.forEach(i => { const k = (i.entry_date || '').slice(0, 7); allMonths[k] = allMonths[k] || { Rev: 0, Exp: 0 }; allMonths[k].Rev += Number(i.amount_usd || 0) })
      allRdr.forEach(i => { const k = (i.revenue_date || '').slice(0, 7); allMonths[k] = allMonths[k] || { Rev: 0, Exp: 0 }; allMonths[k].Rev += Number(i.total_amount_usd || 0) })
      
      allHee.forEach(i => { const k = (i.expense_date || '').slice(0, 7); allMonths[k] = allMonths[k] || { Rev: 0, Exp: 0 }; allMonths[k].Exp += Number(i.amount_usd || 0) })
      allP.forEach(i => { const k = (i.invoice_date || '').slice(0, 7); allMonths[k] = allMonths[k] || { Rev: 0, Exp: 0 }; allMonths[k].Exp += Number(i.amount_usd || 0) })"""
        
        content = content.replace(old_monthly2, new_monthly2)


    with open(filename, 'w') as f:
        f.write(content)
