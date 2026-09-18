import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

old_button = r'<button onClick=\{\(\) => saveRow\(year, month\)\}.*?</button>'
new_button = """<div className="flex gap-2 justify-end items-center">
                          <button onClick={() => saveRow(year, month)} disabled={saving[key]} className="text-navy-600 hover:text-navy-800 text-xs font-medium disabled:opacity-50">{saving[key] ? 'Saving…' : 'Save'}</button>
                          <button onClick={() => clearRow(year, month)} disabled={saving[key]} className="text-red-500 hover:text-red-700 text-xs font-medium disabled:opacity-50">Clear</button>
                        </div>"""

code = re.sub(old_button, new_button, code, flags=re.DOTALL)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
