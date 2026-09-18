import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

# Remove negative sign from variance and round numbers
# Current:
# <td className={`py-1.5 px-3 text-xs font-medium ${varLocal < 0 ? 'text-red-500' : varLocal > 0 ? 'text-green-600' : 'text-slate-400'}`}>{varLocal > 0 ? '+' : ''}{formatMoney(varLocal, row.currency || displayCurrency)}</td>
# <td className={`py-1.5 px-3 text-xs ${varUsd < 0 ? 'text-red-500' : varUsd > 0 ? 'text-green-600' : 'text-slate-400'}`}>{varUsd > 0 ? '+' : ''}{fmt(varUsd)}</td>

old_var_local = r"<td className=\{`py-1.5 px-3 text-xs font-medium \$\{varLocal < 0 \? 'text-red-500' : varLocal > 0 \? 'text-green-600' : 'text-slate-400'\}`\}>\{varLocal > 0 \? '\+' : ''\}\{formatMoney\(varLocal, row.currency \|\| displayCurrency\)\}</td>"
new_var_local = r"<td className={`py-1.5 px-3 text-xs font-medium ${varLocal < 0 ? 'text-red-500' : 'text-green-600'}`}>{formatMoney(Math.abs(Math.round(varLocal)), row.currency || displayCurrency).replace('.00', '')}</td>"
code = re.sub(old_var_local, new_var_local, code)

old_var_usd = r"<td className=\{`py-1.5 px-3 text-xs \$\{varUsd < 0 \? 'text-red-500' : varUsd > 0 \? 'text-green-600' : 'text-slate-400'\}`\}>\{varUsd > 0 \? '\+' : ''\}\{fmt\(varUsd\)\}</td>"
new_var_usd = r"<td className={`py-1.5 px-3 text-xs ${varUsd < 0 ? 'text-red-500' : 'text-green-600'}`}>{formatMoney(Math.abs(Math.round(varUsd)), 'USD').replace('.00', '')}</td>"
code = re.sub(old_var_usd, new_var_usd, code)

old_monthly_local = r"<td className=\"py-1.5 px-3 text-slate-500 text-xs font-medium\">\{formatMoney\(monthlyBudget, row.currency \|\| displayCurrency\)\}</td>"
new_monthly_local = r"<td className=\"py-1.5 px-3 text-slate-500 text-xs font-medium\">{formatMoney(Math.round(monthlyBudget), row.currency || displayCurrency).replace('.00', '')}</td>"
code = re.sub(old_monthly_local, new_monthly_local, code)

old_monthly_usd = r"<td className=\"py-1.5 px-3 text-slate-500 text-xs\">\{fmt\(monthlyUsd\)\}</td>"
new_monthly_usd = r"<td className=\"py-1.5 px-3 text-slate-500 text-xs\">{formatMoney(Math.round(monthlyUsd), 'USD').replace('.00', '')}</td>"
code = re.sub(old_monthly_usd, new_monthly_usd, code)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
