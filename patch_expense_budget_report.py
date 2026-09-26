import re

with open('src/pages/HotelExpenseBudget.jsx', 'r') as f:
    content = f.read()

# Replace the report modal fields
old_modal = """      {reportModalOpen && (
        <ReportOptionsModal
          onClose={() => setReportModalOpen(false)}
          onGenerate={generateReport}
          title={activeProduct === "restaurant" ? "F&B Expense Budget" : "Expenses Budget"}
          fields={[
            { type: 'currency', key: 'currency', default: displayCurrency }
          ]}
        />
      )}"""

new_modal = """      {reportModalOpen && (
        <ReportOptionsModal
          onClose={() => setReportModalOpen(false)}
          onGenerate={generateReport}
          title={activeProduct === "restaurant" ? "F&B Expense Budget" : "Expenses Budget"}
          fields={[
            { type: 'currency', key: 'currency', default: displayCurrency },
            { 
              type: 'select', 
              key: 'period', 
              label: 'Select Period', 
              default: String(selectedYear),
              options: [
                { value: 'all', label: 'All Available Years' },
                ...Array.from({ length: 8 }, (_, i) => { const y = new Date().getFullYear() - 2 + i; return { value: String(y), label: `${y} (Full Year)` } }),
                ...Array.from({ length: 12 }, (_, i) => { return { value: `${selectedYear}-${i + 1}`, label: `${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i]} ${selectedYear}` } })
              ]
            }
          ]}
        />
      )}"""
content = content.replace(old_modal, new_modal)

# Rewrite generateReport to fetch data dynamically if needed!
old_gen = """  // Reports
  async function generateReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (rates[selections.currency] || 1)
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    
    const sections = []
    
    // 1. Annual Summary
    const summaryRows = []
    for (const m of monthlySummary.months) {
      summaryRows.push([
        m.name,
        f(m.budget),
        f(m.actual),
        f(m.variance)
      ])
    }
    summaryRows.push([
      'Total',
      f(monthlySummary.totalBudget),
      f(monthlySummary.totalActual),
      f(monthlySummary.totalVariance)
    ])
    
    sections.push({
      title: `${selectedYear} Annual Summary`,
      headers: ['Month', 'Budget', 'Actual', 'Variance'],
      rows: summaryRows
    })
    
    // 2. Selected Month Detailed Budget
    const monthName = MONTH_NAMES[selectedMonth - 1]
    const detailRows = []
    for (const a of accounts) {
      const key = `${a.code}-${selectedMonth}`
      const row = budgets[key] || { amount: 0, currency: displayCurrency, amount_usd: 0 }
      const monthlyUsd = Number(row.amount_usd) || 0
      const actualUsd = actuals[key] || 0
      
      const cur = row.currency || displayCurrency
      const rr = cur === 'USD' ? 1 : (rates[cur] || rate)
      const actualLocal = cur === 'USD' ? actualUsd : (actualUsd * rr)
      
      const varLocal = actualLocal - (Number(row.amount) || 0)
      const varUsd = actualUsd - monthlyUsd
      
      detailRows.push([
        `${a.code} - ${a.name}`,
        formatMoney(Number(row.amount) || 0, cur),
        f(monthlyUsd),
        formatMoney(actualLocal, cur),
        f(actualUsd),
        formatMoney(varLocal, cur),
        f(varUsd)
      ])
    }
    
    sections.push({
      title: `${monthName} ${selectedYear} Detailed Budget`,
      headers: ['Account', 'Budget (Local)', 'Budget (USD)', 'Actual (Local)', 'Actual (USD)', 'Variance (Local)', 'Variance (USD)'],
      rows: detailRows
    })
    
    const title = activeProduct === "restaurant" ? "F&B Expense Budget" : "Expenses Budget"
    const subtitle = `${activeCompany.name} • ${selectedYear} • ${selections.currency}`
    
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'expense_budget' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'expense_budget' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'expense_budget' })
  }"""

new_gen = """  // Reports
  async function generateReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (rates[selections.currency] || 1)
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    
    const p = selections.period || String(selectedYear)
    let periodKeys = []
    
    if (p === 'all') {
      const allYears = Array.from({ length: 8 }, (_, i) => new Date().getFullYear() - 2 + i)
      allYears.forEach(y => MONTH_NAMES.forEach((_, i) => periodKeys.push(`${y}-${i + 1}`)))
    } else if (p.includes('-')) {
      periodKeys.push(p)
    } else {
      MONTH_NAMES.forEach((_, i) => periodKeys.push(`${p}-${i + 1}`))
    }
    
    // We must fetch the data for the requested periods to be accurate if it spans multiple years
    // For simplicity, fetch all available years in one go for the report
    const { data: reportBudgets } = await supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    const { data: reportActuals } = await supabase.from('hotel_expense_entries').select('expense_date, account:accounts(code), amount_usd').eq('company_id', activeCompany.id).eq('product', activeProduct)
    
    const reportBudgetsMap = {}
    ;(reportBudgets || []).forEach(b => {
      reportBudgetsMap[`${b.account_code}-${b.budget_year}-${b.budget_month}`] = b
    })
    
    const reportActualsMap = {}
    ;(reportActuals || []).forEach(e => {
      if (e.account && e.expense_date) {
        const [y, m] = e.expense_date.split('-')
        const k = `${e.account.code}-${y}-${Number(m)}`
        reportActualsMap[k] = (reportActualsMap[k] || 0) + Number(e.amount_usd)
      }
    })

    const sections = []
    
    if (p.includes('-') && !p.includes('all')) {
      // Single month detailed view
      const [y, mStr] = p.split('-')
      const mIdx = Number(mStr)
      const monthName = MONTH_NAMES[mIdx - 1]
      const detailRows = []
      
      for (const a of accounts) {
        const bk = `${a.code}-${y}-${mIdx}`
        const row = reportBudgetsMap[bk] || { amount: 0, currency: selections.currency, amount_usd: 0 }
        const monthlyUsd = Number(row.amount_usd) || 0
        const actualUsd = reportActualsMap[bk] || 0
        
        detailRows.push([
          `${a.code} - ${a.name}`,
          formatMoney(Number(row.amount) || 0, row.currency || selections.currency),
          f(monthlyUsd),
          f(actualUsd),
          f(actualUsd - monthlyUsd)
        ])
      }
      
      sections.push({
        title: `${monthName} ${y} Detailed Budget`,
        headers: ['Account', 'Budget (Local)', 'Budget (USD)', 'Actual (USD)', 'Variance (USD)'],
        rows: detailRows
      })
    } else {
      // Annual or All Years Summary
      const summaryRows = []
      
      // Group by period key
      periodKeys.forEach(pk => {
        const [y, mStr] = pk.split('-')
        const mIdx = Number(mStr)
        
        let mBudget = 0
        let mActual = 0
        for (const a of accounts) {
          const bk = `${a.code}-${y}-${mIdx}`
          if (reportBudgetsMap[bk]) mBudget += Number(reportBudgetsMap[bk].amount_usd) || 0
          if (reportActualsMap[bk]) mActual += Number(reportActualsMap[bk]) || 0
        }
        
        summaryRows.push([
          `${MONTH_NAMES[mIdx - 1]} ${y}`,
          f(mBudget),
          f(mActual),
          f(mActual - mBudget)
        ])
      })
      
      sections.push({
        title: p === 'all' ? `All Years Summary` : `${p} Annual Summary`,
        headers: ['Period', 'Budget', 'Actual', 'Variance'],
        rows: summaryRows
      })
    }
    
    const title = activeProduct === "restaurant" ? "F&B Expense Budget" : "Expenses Budget"
    const subtitle = `${activeCompany.name} • ${p} • ${selections.currency}`
    
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'expense_budget' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'expense_budget' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'expense_budget' })
  }"""
content = content.replace(old_gen, new_gen)

with open('src/pages/HotelExpenseBudget.jsx', 'w') as f:
    f.write(content)
