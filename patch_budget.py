import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

# Add clearRow function
old_save = """  async function saveRow(year, month) {
    const key = `${year}-${month}`
    const row = rows[key]"""

new_save = """  async function clearRow(year, month) {
    if (!confirm('Clear budget entry for this month?')) return
    const key = `${year}-${month}`
    setSaving(s => ({ ...s, [key]: true }))
    await supabase.from('hotel_room_revenue_budget').delete().eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', year).eq('budget_month', month)
    setRows(r => { const next = { ...r }; delete next[key]; return next })
    setSaving(s => ({ ...s, [key]: false }))
  }

  async function saveRow(year, month) {
    const key = `${year}-${month}`
    const row = rows[key]"""
code = code.replace(old_save, new_save)


# Update the render logic for the table rows
old_table_row = """          const row = rows[`${year}-${m.num}`] || { occ: 0, adr: 0, revenue: 0, currency: displayCurrency, revenue_usd: 0 }
          const days = daysInMonth(year, m.num)
          const roomsOcc = Math.round(totalRooms * (Number(row.occ) || 0) / 100)
          const monthlyBudget = (Number(row.revenue) || 0) * days
          const isSaving = saving[`${year}-${m.num}`]
          return (
            <tr key={m.num} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
              <td className="py-1.5 px-3 font-medium text-slate-700">{m.name}</td>
              <td className="py-1.5 px-3"><input type="number" min="0" max="100" step="0.01" value={row.occ === 0 ? '' : row.occ} onChange={(e) => updateRow(year, m.num, 'occ', e.target.value)} placeholder="%" className="w-16 border border-slate-300 rounded text-sm px-2 py-1" /></td>
              <td className="py-1.5 px-3"><input type="number" min="0" step="0.01" value={row.adr === 0 ? '' : row.adr} onChange={(e) => updateRow(year, m.num, 'adr', e.target.value)} placeholder="ADR" className="w-20 border border-slate-300 rounded text-sm px-2 py-1" /></td>
              <td className="py-1.5 px-3 text-slate-500">{roomsOcc}</td>
              <td className="py-1.5 px-3">
                <div className="flex items-center gap-1">
                  <select value={row.currency || displayCurrency} onChange={(e) => updateRow(year, m.num, 'currency', e.target.value)} className="w-16 border border-slate-300 rounded text-sm px-1 py-1 bg-slate-50">
                    {CURRENCY_LIST.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
                  </select>
                  <input type="number" min="0" step="0.01" value={row.revenue === 0 ? '' : row.revenue} onChange={(e) => updateRow(year, m.num, 'revenue', e.target.value)} placeholder="Revenue" className="w-24 border border-slate-300 rounded text-sm px-2 py-1" />
                </div>
              </td>
              <td className="py-1.5 px-3 text-slate-500">{fmt(row.revenue_usd || 0)}</td>
              <td className="py-1.5 px-3 text-slate-500">{fmt(monthlyBudget)}</td>
              <td className="py-1.5 px-3 text-slate-500">{fmt(actuals[`${year}-${m.num}`] || 0)}</td>
              <td className="py-1.5 px-3 text-right">
                <button onClick={() => saveRow(year, m.num)} disabled={isSaving} className="text-navy-600 hover:text-navy-800 font-medium text-sm disabled:opacity-50">
                  {isSaving ? '...' : 'Save'}
                </button>
              </td>
            </tr>"""

new_table_row = """          const row = rows[`${year}-${m.num}`] || { occ: 0, adr: 0, revenue: 0, currency: displayCurrency, revenue_usd: 0 }
          const days = daysInMonth(year, m.num)
          const roomsOcc = Math.round(totalRooms * (Number(row.occ) || 0) / 100)
          const monthlyBudget = (Number(row.revenue) || 0) * days
          const isSaving = saving[`${year}-${m.num}`]
          return (
            <tr key={m.num} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
              <td className="py-1.5 px-3 font-medium text-slate-700">{m.name}</td>
              <td className="py-1.5 px-3"><input type="number" min="0" max="100" step="0.01" value={row.occ === 0 ? '' : row.occ} onChange={(e) => updateRow(year, m.num, 'occ', e.target.value)} placeholder="%" className="w-16 border border-slate-300 rounded text-sm px-2 py-1" /></td>
              <td className="py-1.5 px-3"><input type="number" min="0" step="0.01" value={row.adr === 0 ? '' : row.adr} onChange={(e) => updateRow(year, m.num, 'adr', e.target.value)} placeholder="ADR" className="w-20 border border-slate-300 rounded text-sm px-2 py-1" /></td>
              <td className="py-1.5 px-3 text-slate-500">{roomsOcc}</td>
              <td className="py-1.5 px-3">
                <div className="flex items-center gap-1">
                  <select value={row.currency || displayCurrency} onChange={(e) => updateRow(year, m.num, 'currency', e.target.value)} className="w-16 border border-slate-300 rounded text-sm px-1 py-1 bg-slate-50">
                    {CURRENCY_LIST.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
                  </select>
                  <input type="number" min="0" step="0.01" value={row.revenue === 0 ? '' : row.revenue} onChange={(e) => updateRow(year, m.num, 'revenue', e.target.value)} placeholder="Revenue" className="w-24 border border-slate-300 rounded text-sm px-2 py-1" />
                </div>
              </td>
              <td className="py-1.5 px-3 text-slate-500">{fmt(row.revenue_usd || 0)}</td>
              <td className="py-1.5 px-3 text-slate-500">{formatMoney(monthlyBudget, row.currency || displayCurrency)}</td>
              <td className="py-1.5 px-3 text-slate-500">{fmt(actuals[`${year}-${m.num}`] || 0)}</td>
              <td className="py-1.5 px-3 text-right">
                <div className="flex justify-end gap-2">
                  <button onClick={() => saveRow(year, m.num)} disabled={isSaving} className="text-navy-600 hover:text-navy-800 font-medium text-sm disabled:opacity-50">
                    {isSaving ? '...' : 'Save'}
                  </button>
                  <button onClick={() => clearRow(year, m.num)} disabled={isSaving} className="text-red-500 hover:text-red-700 font-medium text-sm disabled:opacity-50" title="Clear Entry">
                    Clear
                  </button>
                </div>
              </td>
            </tr>"""
code = code.replace(old_table_row, new_table_row)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
