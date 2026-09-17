import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

old_rowmap = "rowMap[`${b.budget_year}-${b.budget_month}`] = { occ: b.budgeted_occupancy_pct, adr: b.budgeted_adr, revenue: b.budgeted_room_revenue, currency: b.currency }"
new_rowmap = "rowMap[`${b.budget_year}-${b.budget_month}`] = { occ: b.budgeted_occupancy_pct, adr: b.budgeted_adr, revenue: b.budgeted_room_revenue, currency: b.currency, revenue_usd: b.budgeted_room_revenue_usd }"
code = code.replace(old_rowmap, new_rowmap)

old_th = """                <th className="py-2 px-3 text-left font-semibold text-slate-500 w-64">Budgeted Revenue</th>
                <th className="py-2 px-3 text-left font-semibold text-slate-500">Daily Budget</th>"""

new_th = """                <th className="py-2 px-3 text-left font-semibold text-slate-500 w-64">Budgeted Revenue</th>
                <th className="py-2 px-3 text-left font-semibold text-slate-500">USD Equiv.</th>
                <th className="py-2 px-3 text-left font-semibold text-slate-500">Daily Budget</th>"""
code = code.replace(old_th, new_th)

old_td = """                    <td className="py-1.5 px-3">
  <div className="flex gap-1">
    <select value={row.currency || displayCurrency} onChange={e => updateRow(year, month, 'currency', e.target.value)} className="w-16 border border-slate-200 rounded px-1 py-1 text-xs bg-slate-50 text-slate-500 font-medium cursor-pointer focus:outline-none focus:border-navy-400">
      {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
    </select>
    <input type="number" step="0.01" value={row.revenue || ''} onChange={e => updateRow(year, month, 'revenue', e.target.value)} className="w-28 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="Revenue" />
  </div>
</td>
                    <td className="py-1.5 px-3 text-slate-500">{formatMoney(dailyBudget, row.currency || displayCurrency)}</td>"""

new_td = """                    <td className="py-1.5 px-3">
  <div className="flex gap-1">
    <select value={row.currency || displayCurrency} onChange={e => updateRow(year, month, 'currency', e.target.value)} className="w-16 border border-slate-200 rounded px-1 py-1 text-xs bg-slate-50 text-slate-500 font-medium cursor-pointer focus:outline-none focus:border-navy-400">
      {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
    </select>
    <input type="number" step="0.01" value={row.revenue || ''} onChange={e => updateRow(year, month, 'revenue', e.target.value)} className="w-28 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="Revenue" />
  </div>
</td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs">{(row.currency || displayCurrency) === 'USD' ? formatMoney(row.revenue || 0, 'USD') : (row.revenue_usd ? formatMoney(row.revenue_usd, 'USD') : <span className="text-slate-300 italic text-[10px]">On save</span>)}</td>
                    <td className="py-1.5 px-3 text-slate-500">{formatMoney(dailyBudget, row.currency || displayCurrency)}</td>"""
code = code.replace(old_td, new_td)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
