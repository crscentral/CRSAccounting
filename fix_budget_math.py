import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

# Update updateRow triangulation to use DAILY revenue
old_triangulation = """      const roomNights = totalRooms * days
      if (field === 'occ' || field === 'adr') {
        if (roomNights > 0 && Number(next.occ) > 0 && Number(next.adr) > 0) {
          next.revenue = Math.round(roomNights * (Number(next.occ) / 100) * Number(next.adr) * 100) / 100
        }
      } else if (field === 'revenue') {
        if (roomNights > 0 && Number(next.occ) > 0) {
          next.adr = Math.round((Number(next.revenue) / (roomNights * (Number(next.occ) / 100))) * 100) / 100
        } else if (roomNights > 0 && Number(next.adr) > 0) {
          next.occ = Math.round((Number(next.revenue) / Number(next.adr) / roomNights) * 100 * 100) / 100
        }
      }"""

new_triangulation = """      if (field === 'occ' || field === 'adr') {
        if (totalRooms > 0 && Number(next.occ) > 0 && Number(next.adr) > 0) {
          next.revenue = Math.round(totalRooms * (Number(next.occ) / 100) * Number(next.adr) * 100) / 100
        }
      } else if (field === 'revenue') {
        if (totalRooms > 0 && Number(next.occ) > 0) {
          next.adr = Math.round((Number(next.revenue) / (totalRooms * (Number(next.occ) / 100))) * 100) / 100
        } else if (totalRooms > 0 && Number(next.adr) > 0) {
          next.occ = Math.round((Number(next.revenue) / Number(next.adr) / totalRooms) * 100 * 100) / 100
        }
      }"""
code = code.replace(old_triangulation, new_triangulation)

# Update column headers and rendering
old_th = """                <th className="py-2 px-3 text-left font-semibold text-slate-500 w-64">Budgeted Revenue</th>
                <th className="py-2 px-3 text-left font-semibold text-slate-500">USD Equiv.</th>
                <th className="py-2 px-3 text-left font-semibold text-slate-500">Daily Budget</th>"""

new_th = """                <th className="py-2 px-3 text-left font-semibold text-slate-500 w-64">Budgeted Daily Rev.</th>
                <th className="py-2 px-3 text-left font-semibold text-slate-500">USD Equiv.</th>
                <th className="py-2 px-3 text-left font-semibold text-slate-500">Monthly Budget</th>"""
code = code.replace(old_th, new_th)

old_td = """<td className="py-1.5 px-3 text-slate-500 text-xs">{(row.currency || displayCurrency) === 'USD' ? formatMoney(row.revenue || 0, 'USD') : (row.revenue_usd ? formatMoney(row.revenue_usd, 'USD') : <span className="text-slate-300 italic text-[10px]">On save</span>)}</td>
                    <td className="py-1.5 px-3 text-slate-500">{formatMoney(dailyBudget, row.currency || displayCurrency)}</td>"""

new_td = """<td className="py-1.5 px-3 text-slate-500 text-xs">{(row.currency || displayCurrency) === 'USD' ? formatMoney(row.revenue || 0, 'USD') : (row.revenue_usd ? formatMoney(row.revenue_usd, 'USD') : <span className="text-slate-300 italic text-[10px]">On save</span>)}</td>
                    <td className="py-1.5 px-3 text-slate-500">{formatMoney((Number(row.revenue) || 0) * days, row.currency || displayCurrency)}</td>"""
code = code.replace(old_td, new_td)

# Wait, `const dailyBudget = (Number(row.revenue) || 0) / days` is calculated in the render map.
# I should just remove it to avoid confusion or keep it and ignore it. I replaced it above with `* days`.
# Let's remove `const dailyBudget` line to be clean.
old_const = "const dailyBudget = (Number(row.revenue) || 0) / days"
new_const = "const monthlyBudget = (Number(row.revenue) || 0) * days"
code = code.replace(old_const, new_const)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
