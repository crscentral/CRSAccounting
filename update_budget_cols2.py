import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

old_thead = r'<thead.*?</thead>'
new_thead = """<thead className="bg-navy-800 text-white text-xs text-left">
              <tr>
                <th className="py-2 px-3 font-semibold rounded-tl-lg">Month</th>
                <th className="py-2 px-3 font-semibold">Occupancy %</th>
                <th className="py-2 px-3 font-semibold">ADR</th>
                <th className="py-2 px-3 font-semibold">Rooms Occ.</th>
                <th className="py-2 px-3 font-semibold">Daily Budget</th>
                <th className="py-2 px-3 font-semibold">Daily (USD)</th>
                <th className="py-2 px-3 font-semibold">Monthly Budget</th>
                <th className="py-2 px-3 font-semibold">Monthly (USD)</th>
                <th className="py-2 px-3 font-semibold">Actual</th>
                <th className="py-2 px-3 font-semibold">Actual (USD)</th>
                <th className="py-2 px-3 font-semibold">Variance</th>
                <th className="py-2 px-3 font-semibold">Variance (USD)</th>
                <th className="py-2 px-3 font-semibold rounded-tr-lg"></th>
              </tr>
            </thead>"""

code = re.sub(old_thead, new_thead, code, flags=re.DOTALL)


old_tbody = r'<tbody>.*?</tbody>'
new_tbody = """<tbody>
              {MONTH_NAMES.map((m, i) => {
                const month = i + 1
                const key = `${year}-${month}`
                const row = rows[key] || { occ: 0, adr: 0, revenue: 0, currency: displayCurrency, revenue_usd: 0 }
                const days = daysInMonth(year, month)
                
                const roomsOcc = totalRooms > 0 ? Math.round((Number(row.occ) / 100) * totalRooms) : 0
                const dailyRev = Number(row.revenue) || 0
                const dailyUsd = Number(row.revenue_usd) || 0
                
                const monthlyBudget = dailyRev * days
                const monthlyUsd = dailyUsd * days
                
                const actualUsd = actuals[key] || 0
                const actualLocal = convertFromUsd(actualUsd, row.currency || displayCurrency, { [row.currency || displayCurrency]: rate })
                
                const varUsd = actualUsd - monthlyUsd
                const varLocal = actualLocal - monthlyBudget

                return (
                  <tr key={month} className="border-b border-slate-50 last:border-0 hover:bg-slate-50 transition-colors">
                    <td className="py-1.5 px-3 font-medium text-slate-700 text-sm">{m}</td>
                    <td className="py-1.5 px-3">
                      <input type="number" min="0" max="100" step="0.01" value={row.occ || ''} onChange={e => updateRow(year, month, 'occ', e.target.value)} className="w-16 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="%" />
                    </td>
                    <td className="py-1.5 px-3">
                      <input type="number" min="0" step="0.01" value={row.adr || ''} onChange={e => updateRow(year, month, 'adr', e.target.value)} className="w-20 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="ADR" />
                    </td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs">{roomsOcc}</td>
                    <td className="py-1.5 px-3">
                      <div className="flex items-center gap-1">
                        <select value={row.currency || displayCurrency} onChange={e => updateRow(year, month, 'currency', e.target.value)} className="w-16 border border-slate-200 rounded px-1 py-1 text-[10px] bg-slate-50">
                          {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
                        </select>
                        <input type="number" step="0.01" value={row.revenue || ''} onChange={e => updateRow(year, month, 'revenue', e.target.value)} className="w-24 border border-slate-200 rounded px-2 py-1 text-xs" placeholder="Revenue" />
                      </div>
                    </td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs">{(row.currency || displayCurrency) === 'USD' ? formatMoney(row.revenue || 0, 'USD') : (row.revenue_usd ? formatMoney(row.revenue_usd, 'USD') : <span className="text-slate-300 italic text-[10px]">On save</span>)}</td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs font-medium">{formatMoney(monthlyBudget, row.currency || displayCurrency)}</td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs">{fmt(monthlyUsd)}</td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs font-medium">{formatMoney(actualLocal, row.currency || displayCurrency)}</td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs">{fmt(actualUsd)}</td>
                    <td className={`py-1.5 px-3 text-xs font-medium ${varLocal < 0 ? 'text-red-500' : varLocal > 0 ? 'text-green-600' : 'text-slate-400'}`}>{varLocal > 0 ? '+' : ''}{formatMoney(varLocal, row.currency || displayCurrency)}</td>
                    <td className={`py-1.5 px-3 text-xs ${varUsd < 0 ? 'text-red-500' : varUsd > 0 ? 'text-green-600' : 'text-slate-400'}`}>{varUsd > 0 ? '+' : ''}{fmt(varUsd)}</td>
                    <td className="py-1.5 px-3">
                      {can(['owner', 'admin', 'accountant']) && (
                        <div className="flex gap-2 justify-end items-center">
                          <button onClick={() => saveRow(year, month)} disabled={saving[key]} className="text-navy-600 hover:text-navy-800 text-xs font-medium disabled:opacity-50">{saving[key] ? 'Saving…' : 'Save'}</button>
                          <button onClick={() => clearRow(year, month)} disabled={saving[key]} className="text-red-500 hover:text-red-700 text-xs font-medium disabled:opacity-50">Clear</button>
                        </div>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>"""
code = re.sub(old_tbody, new_tbody, code, flags=re.DOTALL)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
