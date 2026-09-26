with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

old_exp = """    // Expenses Made = Expense entries + amortized AMC (assuming paid for simplicity)
    const start = new Date(cp.range.from)
    const end = new Date(cp.range.to)
    const monthsInView = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1
    const amcTotal = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    expensesMade = hotelExpenseEntries.reduce((s, e) => s + Number(e.amount_usd), 0) + amcTotal
  } else {"""

new_exp = """    const start = new Date(cp.range.from)
    const end = new Date(cp.range.to)
    const monthsInView = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1
    const amcTotal = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    
    // Add AMC amortized to Total Expenses (Accrued) since it doesn't hit the ledger
    totalExpenses += amcTotal
    
    // Expenses Made = Actual cash out (hotel expense entries). AMC cash out is not modeled in the date range cleanly, so we only count direct expense entries.
    expensesMade = hotelExpenseEntries.reduce((s, e) => s + Number(e.amount_usd), 0)
  } else {"""

content = content.replace(old_exp, new_exp)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)
