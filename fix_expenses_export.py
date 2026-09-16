import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    code = f.read()

# I need to find the `generateExpensesReport` function and modify it to include checkboxes and summary charts
old_export = """  async function generateExpensesReport(selections, format) {
    const range = resolveReportPeriod(selections.period, 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)
    const { data: exp } = await supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', range.from).lte('expense_date', range.to).order('expense_date', { ascending: false })
    const sections = [{
      heading: 'Expenses',
      columns: ['Date', 'Expense Head', 'Amount', 'Notes'],
      rows: (exp || []).map(r => [r.expense_date, r.account ? `${r.account.code} - ${r.account.name}` : '—', f(r.amount_usd), r.notes || '—']),
    }]
    const title = 'Hotel Expenses'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'hotel_expenses' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'hotel_expenses' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'hotel_expenses' })
  }"""

new_export = """  async function generateExpensesReport(selections, format) {
    const range = resolveReportPeriod(selections.period, 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)
    
    // We already have the current entries and amcContracts in state. 
    // The report generator might fetch a different date range, so let's use the fetched data.
    const { data: exp } = await supabase.from('hotel_expense_entries').select('*, account:accounts(code, name, subtype)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', range.from).lte('expense_date', range.to).order('expense_date', { ascending: false })
    
    // Determine selected heads
    const selectedHeads = selections.heads || []
    const includeAll = selectedHeads.length === 0
    const includeAmc = includeAll || selectedHeads.includes('AMC Contracts (Amortized)')
    
    // Calculate AMC amortized amount for this range
    const start = new Date(range.from)
    const end = new Date(range.to)
    const monthsInView = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1
    const amcMonthlyTotalUsd = amcContracts.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0)
    const amcTotalForView = amcMonthlyTotalUsd * monthsInView
    
    let totalView = 0
    let expenseRows = []
    
    (exp || []).forEach(r => {
      const head = r.account ? `${r.account.code} - ${r.account.name}` : 'Unknown'
      if (includeAll || selectedHeads.includes(head)) {
        expenseRows.push([r.expense_date, head, f(r.amount_usd), r.notes || '—'])
        totalView += Number(r.amount_usd)
      }
    })
    
    if (includeAmc && amcTotalForView > 0) {
      expenseRows.unshift([range.to, 'AMC Contracts (Amortized)', f(amcTotalForView), 'Auto-Amortized Monthly Portion'])
      totalView += amcTotalForView
    }

    const sections = [
      {
        heading: 'Summary',
        keyValuePairs: [
          ['Total Expenses in Period', f(totalView)],
          ['Number of Expense Heads', String(new Set(expenseRows.map(r => r[1])).size)]
        ]
      },
      {
        heading: 'Expense Detail',
        columns: ['Date', 'Expense Head', 'Amount', 'Notes'],
        rows: expenseRows
      }
    ]
    
    const title = 'Hotel Expenses Report'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    const logoUrl = activeCompany.logo_url
    
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'hotel_expenses', logoUrl })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'hotel_expenses' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'hotel_expenses' })
  }"""
code = code.replace(old_export, new_export)


# Update the ReportOptionsModal call
old_options = """      {reportModalOpen && (
        <ReportOptionsModal
          title="Expenses"
          fields={[
            { key: 'period', type: 'period' },
            { key: 'currency', type: 'currency' },
          ]}
          onGenerate={generateExpensesReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}"""
new_options = """      {reportModalOpen && (
        <ReportOptionsModal
          title="Expenses"
          fields={[
            { key: 'period', type: 'period' },
            { key: 'currency', type: 'currency' },
            { key: 'heads', type: 'checkboxGroup', label: 'Select Specific Expense Heads (Leave empty for All)', options: Object.keys(byHead) },
          ]}
          onGenerate={generateExpensesReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}"""
code = code.replace(old_options, new_options)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(code)
