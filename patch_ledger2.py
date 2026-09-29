with open('src/pages/Ledger.jsx', 'r') as f:
    content = f.read()

# Fix table render to not be running balance, and use -ve sign
old_running = """  let running = 0
  const withBalance = entries.map(e => {
    running += Number(e.debit_usd) - Number(e.credit_usd)
    return { ...e, balance: running }
  })"""

new_running = """  const withBalance = entries.map(e => {
    return { ...e, balance: Number(e.debit_usd) - Number(e.credit_usd) }
  })"""
content = content.replace(old_running, new_running)

old_render = "          { key: 'balance', label: `Balance (${cp.displayCurrency})`, render: r => r.balance < 0 ? `${cp.fmt(Math.abs(r.balance))} Cr` : (r.balance > 0 ? `${cp.fmt(r.balance)} Dr` : cp.fmt(0)) },"
new_render = "          { key: 'balance', label: `Balance (${cp.displayCurrency})`, render: r => r.balance < 0 ? `-${cp.fmt(Math.abs(r.balance))}` : cp.fmt(r.balance) },"
content = content.replace(old_render, new_render)

# Fix export render
old_export_running = """    let running = 0
    const rows = combined.map(e => {
      running += Number(e.debit_usd) - Number(e.credit_usd)
      const balStr = running < 0 ? `${fmt(Math.abs(running))} Cr` : (running > 0 ? `${fmt(running)} Dr` : fmt(0)); return [e.entry_date, e.description, e.currency, Number(e.debit_usd) ? fmt(e.debit_usd) : '—', Number(e.credit_usd) ? fmt(e.credit_usd) : '—', balStr]
    })"""

new_export_running = """    const rows = combined.map(e => {
      const lineBalance = Number(e.debit_usd) - Number(e.credit_usd)
      const balStr = lineBalance < 0 ? `-${fmt(Math.abs(lineBalance))}` : fmt(lineBalance); 
      return [e.entry_date, e.description, e.currency, Number(e.debit_usd) ? fmt(e.debit_usd) : '—', Number(e.credit_usd) ? fmt(e.credit_usd) : '—', balStr]
    })"""
content = content.replace(old_export_running, new_export_running)

with open('src/pages/Ledger.jsx', 'w') as f:
    f.write(content)

