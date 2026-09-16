import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

# I need to add currency to the rows parsing logic when loading.
load_logic_old = """    const parsed = {}
    budgetRows.forEach(r => {
      parsed[`${r.budget_year}-${r.budget_month}`] = {
        occ: r.budgeted_occupancy_pct,
        adr: r.budgeted_adr,
        revenue: r.budgeted_room_revenue,
      }
    })"""
load_logic_new = """    const parsed = {}
    budgetRows.forEach(r => {
      parsed[`${r.budget_year}-${r.budget_month}`] = {
        occ: r.budgeted_occupancy_pct,
        adr: r.budgeted_adr,
        revenue: r.budgeted_room_revenue,
        currency: r.currency || 'USD',
      }
    })"""
code = code.replace(load_logic_old, load_logic_new)

# Modify updateRow to not trigger the math calculation if the field is 'currency'
update_old = """  function updateRow(year, month, field, val) {
    setRows(prev => {
      const key = `${year}-${month}`
      const curr = { ...(prev[key] || { occ: '', adr: '', revenue: '' }) }
      curr[field] = val
      
      const v = Number(val) || 0"""
update_new = """  function updateRow(year, month, field, val) {
    setRows(prev => {
      const key = `${year}-${month}`
      const curr = { ...(prev[key] || { occ: '', adr: '', revenue: '', currency: displayCurrency }) }
      curr[field] = val
      
      if (field === 'currency') return { ...prev, [key]: curr }
      
      const v = Number(val) || 0"""
code = code.replace(update_old, update_new)

# Add the currency dropdown next to the budgeted revenue input
input_old = """<td className="py-1.5 px-3"><input type="number" step="0.01" value={row.revenue || ''} onChange={e => updateRow(year, month, 'revenue', e.target.value)} className="w-28 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="Revenue" /></td>"""
input_new = """<td className="py-1.5 px-3">
  <div className="flex gap-1">
    <select value={row.currency || displayCurrency} onChange={e => updateRow(year, month, 'currency', e.target.value)} className="w-16 border border-slate-200 rounded px-1 py-1 text-xs bg-slate-50 text-slate-500 font-medium cursor-pointer focus:outline-none focus:border-navy-400">
      <option value="USD">USD</option>
      <option value="EUR">EUR</option>
      <option value="GBP">GBP</option>
      <option value="INR">INR</option>
      <option value="AUD">AUD</option>
      <option value="CAD">CAD</option>
      <option value="SGD">SGD</option>
      <option value="AED">AED</option>
      <option value="THB">THB</option>
      <option value="MYR">MYR</option>
    </select>
    <input type="number" step="0.01" value={row.revenue || ''} onChange={e => updateRow(year, month, 'revenue', e.target.value)} className="w-28 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="Revenue" />
  </div>
</td>"""
code = code.replace(input_old, input_new)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
