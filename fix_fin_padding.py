with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    code = f.read()

# Fix the P&L table
old_pl_table = '<table className="w-full text-sm">'
new_pl_table = '<table className="w-full text-sm min-w-[500px]">'
# apply only to the first occurrence
code = code.replace(old_pl_table, new_pl_table, 1)

old_pl_th = """              <tr className="text-left border-b border-slate-100 text-slate-400">
                <th className="py-2 font-medium">Item</th>
                <th className="py-2 font-medium">Current Period</th>
                <th className="py-2 font-medium">Amount %</th>
              </tr>"""
new_pl_th = """              <tr className="text-left border-b border-slate-100 text-slate-400">
                <th className="py-2 pr-4 font-medium whitespace-nowrap">Item</th>
                <th className="py-2 px-4 font-medium whitespace-nowrap">Current Period</th>
                <th className="py-2 pl-4 font-medium whitespace-nowrap">Amount %</th>
              </tr>"""
code = code.replace(old_pl_th, new_pl_th)

old_pl_tr1 = '<tr className="border-b border-slate-50"><td className="py-2.5 font-semibold">Total Revenue</td><td className="py-2.5">{cp.fmt(revenue)}</td><td className="py-2.5 text-slate-400">100.0%</td></tr>'
new_pl_tr1 = '<tr className="border-b border-slate-50"><td className="py-2.5 pr-4 font-semibold whitespace-nowrap">Total Revenue</td><td className="py-2.5 px-4">{cp.fmt(revenue)}</td><td className="py-2.5 pl-4 text-slate-400">100.0%</td></tr>'
code = code.replace(old_pl_tr1, new_pl_tr1)

old_pl_tr2 = '<tr className="border-b border-slate-50"><td className="py-2.5">Total Expenses</td><td className="py-2.5">−{cp.fmt(expenses)}</td><td className="py-2.5 text-slate-400">{revenue ? ((expenses / revenue) * 100).toFixed(1) : 0}%</td></tr>'
new_pl_tr2 = '<tr className="border-b border-slate-50"><td className="py-2.5 pr-4 whitespace-nowrap">Total Expenses</td><td className="py-2.5 px-4">−{cp.fmt(expenses)}</td><td className="py-2.5 pl-4 text-slate-400">{revenue ? ((expenses / revenue) * 100).toFixed(1) : 0}%</td></tr>'
code = code.replace(old_pl_tr2, new_pl_tr2)

old_pl_tr3 = '<tr className="bg-emerald-50"><td className="py-2.5 font-bold text-emerald-700">Gross Operating Profit (GOP)</td><td className="py-2.5 font-bold text-emerald-700">{cp.fmt(profit)}</td><td className="py-2.5 font-bold text-emerald-700">{margin.toFixed(1)}%</td></tr>'
new_pl_tr3 = '<tr className="bg-emerald-50"><td className="py-2.5 pr-4 font-bold text-emerald-700 whitespace-nowrap">Gross Operating Profit (GOP)</td><td className="py-2.5 px-4 font-bold text-emerald-700">{cp.fmt(profit)}</td><td className="py-2.5 pl-4 font-bold text-emerald-700">{margin.toFixed(1)}%</td></tr>'
code = code.replace(old_pl_tr3, new_pl_tr3)


# Fix the Revenue/Expenses by Account table
old_re_table = '<table className="w-full text-sm">'
new_re_table = '<table className="w-full text-sm min-w-[500px]">'
code = code.replace(old_re_table, new_re_table)

old_re_th = """              <tr className="text-left border-b border-slate-100 text-slate-400">
                <th className="py-2 font-medium whitespace-nowrap">Code</th>
                <th className="py-2 font-medium whitespace-nowrap">Account</th>
                <th className="py-2 font-medium text-right whitespace-nowrap">Amount</th>
                <th className="py-2 font-medium text-right whitespace-nowrap">% of Total</th>
              </tr>"""
new_re_th = """              <tr className="text-left border-b border-slate-100 text-slate-400">
                <th className="py-2 pr-4 font-medium whitespace-nowrap w-24">Code</th>
                <th className="py-2 px-4 font-medium whitespace-nowrap">Account</th>
                <th className="py-2 px-4 font-medium text-right whitespace-nowrap">Amount</th>
                <th className="py-2 pl-4 font-medium text-right whitespace-nowrap">% of Total</th>
              </tr>"""
code = code.replace(old_re_th, new_re_th)

old_re_td = """                  <tr key={a.code} className="border-b border-slate-50">
                    <td className="py-2.5">{a.code}</td>
                    <td className="py-2.5">{a.name}</td>
                    <td className="py-2.5 text-right">{cp.fmt(a.amount)}</td>
                    <td className="py-2.5 text-right text-slate-400">{total ? ((a.amount / total) * 100).toFixed(1) : 0}%</td>
                  </tr>"""
new_re_td = """                  <tr key={a.code} className="border-b border-slate-50">
                    <td className="py-2.5 pr-4 text-slate-500">{a.code}</td>
                    <td className="py-2.5 px-4 font-medium whitespace-nowrap">{a.name}</td>
                    <td className="py-2.5 px-4 text-right">{cp.fmt(a.amount)}</td>
                    <td className="py-2.5 pl-4 text-right text-slate-400">{total ? ((a.amount / total) * 100).toFixed(1) : 0}%</td>
                  </tr>"""
code = code.replace(old_re_td, new_re_td)

old_re_total = """              <tr className="bg-rose-50 font-bold text-rose-700">
                <td colSpan={2} className="py-3">Total {tab === 'revenue' ? 'Revenue' : 'Expenses'}</td>
                <td className="py-3 text-right">{cp.fmt(tab === 'revenue' ? revenue : expenses)}</td>
                <td className="py-3 text-right">100.0%</td>
              </tr>"""
new_re_total = """              <tr className="bg-rose-50 font-bold text-rose-700">
                <td colSpan={2} className="py-3 pr-4 whitespace-nowrap">Total {tab === 'revenue' ? 'Revenue' : 'Expenses'}</td>
                <td className="py-3 px-4 text-right">{cp.fmt(tab === 'revenue' ? revenue : expenses)}</td>
                <td className="py-3 pl-4 text-right">100.0%</td>
              </tr>"""
code = code.replace(old_re_total, new_re_total)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(code)
