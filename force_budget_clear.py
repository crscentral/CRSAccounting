import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

# I will replace the exact block defining the <td> containing the save button
old_button_td = r'<td className="py-1.5 px-3 text-right">\s*<button onClick=\{\(\) => saveRow\(year, m.num\)\}.*?</button>\s*</td>'
new_button_td = """<td className="py-1.5 px-3 text-right">
                <div className="flex justify-end gap-2">
                  <button onClick={() => saveRow(year, m.num)} disabled={isSaving} className="text-navy-600 hover:text-navy-800 font-medium text-sm disabled:opacity-50">
                    {isSaving ? '...' : 'Save'}
                  </button>
                  <button onClick={() => clearRow(year, m.num)} disabled={isSaving} className="text-red-500 hover:text-red-700 font-medium text-sm disabled:opacity-50" title="Clear Entry">
                    Clear
                  </button>
                </div>
              </td>"""

code = re.sub(old_button_td, new_button_td, code, flags=re.DOTALL)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
