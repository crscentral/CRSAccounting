import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

# Replace hardcoded options in row dropdown
old_row_select = """    <select value={row.currency || displayCurrency} onChange={e => updateRow(year, month, 'currency', e.target.value)} className="w-16 border border-slate-200 rounded px-1 py-1 text-xs bg-slate-50 text-slate-500 font-medium cursor-pointer focus:outline-none focus:border-navy-400">
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
    </select>"""

new_row_select = """    <select value={row.currency || displayCurrency} onChange={e => updateRow(year, month, 'currency', e.target.value)} className="w-16 border border-slate-200 rounded px-1 py-1 text-xs bg-slate-50 text-slate-500 font-medium cursor-pointer focus:outline-none focus:border-navy-400">
      {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
    </select>"""
code = code.replace(old_row_select, new_row_select)

# Replace limited CURRENCY_LIST in top dropdown
old_top_select = """<select value={displayCurrency} onChange={e => setDisplayCurrency(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>"""

new_top_select = """<select value={displayCurrency} onChange={e => setDisplayCurrency(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code} - {c.name}</option>)}
            </select>"""
code = code.replace(old_top_select, new_top_select)

# Ensure CURRENCIES is imported
if "CURRENCIES" not in code or "import" not in code:
    print("WARNING: Need to check imports")

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
