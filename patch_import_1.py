import re

with open('src/pages/HistoricalImport.jsx', 'r') as f:
    code = f.read()

# Replace downloadHotelTemplate
old_download = """  function downloadHotelTemplate() {
    const wb = XLSX.utils.book_new()
    const actualsSheet = XLSX.utils.aoa_to_sheet([
      ['Date (YYYY-MM-DD)', 'Rooms Occupied', 'Room Revenue', 'Amount Collected', 'Currency'],
      ['2025-04-01', 42, 5600, 5600, 'USD'],
    ])
    XLSX.utils.book_append_sheet(wb, actualsSheet, 'Room Revenue Actuals')
    const budgetSheet = XLSX.utils.aoa_to_sheet([
      ['Year', 'Month (1-12)', 'Budgeted Occupancy %', 'Budgeted ADR', 'Budgeted Room Revenue', 'Currency'],
      [2025, 4, 75, 130, 117000, 'USD'],
    ])
    XLSX.utils.book_append_sheet(wb, budgetSheet, 'Room Revenue Budget')
    XLSX.writeFile(wb, `hotel_5yr_import_template.xlsx`)
  }"""

new_download = """  function downloadHotelTemplate() {
    const wb = XLSX.utils.book_new()
    const guestInvoicesSheet = XLSX.utils.aoa_to_sheet([
      ['Date (YYYY-MM-DD)', 'Room #', 'Guest Name', 'Check-in', 'Check-out', 'Room Rate', 'Nights', 'Other Rev Account Code (Optional)', 'Other Rev Amount', 'Currency', 'Collected Amount'],
      ['2025-04-01', '101', 'John Doe', '2025-03-30', '2025-04-01', 150, 2, '4016', 20, 'USD', 320],
    ])
    XLSX.utils.book_append_sheet(wb, guestInvoicesSheet, 'Guest Invoices')

    const actualsSheet = XLSX.utils.aoa_to_sheet([
      ['Date (YYYY-MM-DD)', 'Manual Rooms Occupied', 'Manual Room Revenue', 'Amount Collected', 'Currency'],
      ['2025-04-01', 42, 5600, 5600, 'USD'],
    ])
    XLSX.utils.book_append_sheet(wb, actualsSheet, 'Daily Revenue Manual')
    
    const expensesSheet = XLSX.utils.aoa_to_sheet([
      ['Date (YYYY-MM-DD)', 'Expense Account Code', 'Amount', 'Currency', 'Notes'],
      ['2025-04-01', '7100', 500, 'USD', 'Lobby supplies'],
    ])
    XLSX.utils.book_append_sheet(wb, expensesSheet, 'Expenses')

    const budgetSheet = XLSX.utils.aoa_to_sheet([
      ['Year', 'Month (1-12)', 'Budgeted Occupancy %', 'Budgeted ADR', 'Budgeted Daily Rev', 'Currency'],
      [2025, 4, 75, 130, 9750, 'USD'],
    ])
    XLSX.utils.book_append_sheet(wb, budgetSheet, 'Room Revenue Budget')
    
    XLSX.writeFile(wb, `hotel_import_template.xlsx`)
  }"""
code = code.replace(old_download, new_download)

with open('src/pages/HistoricalImport.jsx', 'w') as f:
    f.write(code)
