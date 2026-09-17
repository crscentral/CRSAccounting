import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

# Fix headers
old_thead = """            <thead>
              <tr className="text-left border-b border-slate-100 text-slate-400">
                <th className="py-2 px-3 font-medium">Month</th>
                <th className="py-2 px-3 font-medium">Occupancy %</th>
                <th className="py-2 px-3 font-medium">ADR</th>
                <th className="py-2 px-3 font-medium">Rooms Occ.</th>
                <th className="py-2 px-3 font-medium">Budgeted Daily Rev.</th>
                <th className="py-2 px-3 font-medium">Monthly Budget</th>
                <th className="py-2 px-3 font-medium">Actual</th>
                <th className="py-2 px-3 font-medium"></th>
              </tr>
            </thead>"""

new_thead = """            <thead>
              <tr className="text-left border-b border-slate-100 text-slate-400">
                <th className="py-2 px-3 font-medium">Month</th>
                <th className="py-2 px-3 font-medium">Occupancy %</th>
                <th className="py-2 px-3 font-medium">ADR</th>
                <th className="py-2 px-3 font-medium">Rooms Occ.</th>
                <th className="py-2 px-3 font-medium">Daily Budget</th>
                <th className="py-2 px-3 font-medium">USD Equiv.</th>
                <th className="py-2 px-3 font-medium">Monthly Budget</th>
                <th className="py-2 px-3 font-medium">Actual</th>
                <th className="py-2 px-3 font-medium"></th>
              </tr>
            </thead>"""
code = code.replace(old_thead, new_thead)

# Fix row
old_row = """  </div>
</td>
                    <td className="py-1.5 px-3 text-slate-500">{fmt(monthlyBudget)}</td>
                    <td className="py-1.5 px-3 text-slate-500">{fmt(actualUsd)}</td>"""

new_row = """  </div>
</td>
                    <td className="py-1.5 px-3 text-slate-500 text-xs">{(row.currency || displayCurrency) === 'USD' ? formatMoney(row.revenue || 0, 'USD') : (row.revenue_usd ? formatMoney(row.revenue_usd, 'USD') : <span className="text-slate-300 italic text-[10px]">On save</span>)}</td>
                    <td className="py-1.5 px-3 text-slate-500">{fmt(monthlyBudget)}</td>
                    <td className="py-1.5 px-3 text-slate-500">{fmt(actualUsd)}</td>"""
code = code.replace(old_row, new_row)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
