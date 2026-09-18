import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

old_report = """  async function generateBudgetReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    const sy = Number(selections.startYear || startYear)
    const years = [sy, sy + 1, sy + 2, sy + 3, sy + 4]
    const tableRows = []
    years.forEach(y => MONTH_NAMES.forEach((m, i) => {
      const key = `${y}-${i + 1}`
      const row = rows[key]
      const actualUsd = actuals[key] || 0
      if (row) tableRows.push([`${m} ${y}`, `${row.occ}%`, f(convertFromUsd(row.adr, 'USD', { USD: 1 })), f(Number(row.revenue) || 0), f(actualUsd), f((Number(row.revenue) || 0) - actualUsd)])
    }))
    const sections = [{ heading: 'Room Revenue Budget', columns: ['Month', 'Budgeted Occ %', 'Budgeted ADR', 'Budgeted Revenue', 'Actual Revenue', 'Variance'], rows: tableRows }]
    const title = 'Room Revenue Budget'
    const subtitle = `${activeCompany.name} • ${startYear}–${startYear + 4} • ${selections.currency}`
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'room_revenue_budget' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'room_revenue_budget' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'room_revenue_budget' })
  }"""

new_report = """  async function generateBudgetReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    const sy = Number(selections.startYear || startYear)
    const years = [sy, sy + 1, sy + 2, sy + 3, sy + 4]
    const tableRows = []
    years.forEach(y => MONTH_NAMES.forEach((m, i) => {
      const key = `${y}-${i + 1}`
      const row = rows[key]
      const actualUsd = actuals[key] || 0
      if (row) {
        const days = daysInMonth(y, i + 1)
        const monthlyRevUsd = (row.revenue_usd || 0) * days
        const roomsOcc = Math.round(totalRooms * (Number(row.occ) || 0) / 100)
        const adrUsd = roomsOcc > 0 ? (row.revenue_usd / roomsOcc) : 0
        tableRows.push([
          `${m} ${y}`, 
          `${row.occ}%`, 
          f(adrUsd), 
          f(monthlyRevUsd), 
          f(actualUsd), 
          f(monthlyRevUsd - actualUsd)
        ])
      }
    }))
    const sections = [{ heading: 'Room Revenue Budget', columns: ['Month', 'Budgeted Occ %', 'Budgeted ADR', 'Budgeted Monthly Revenue', 'Actual Revenue', 'Variance'], rows: tableRows }]
    const title = 'Room Revenue Budget'
    const subtitle = `${activeCompany.name} • ${startYear}–${startYear + 4} • ${selections.currency}`
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'room_revenue_budget' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'room_revenue_budget' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'room_revenue_budget' })
  }"""
code = code.replace(old_report, new_report)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
