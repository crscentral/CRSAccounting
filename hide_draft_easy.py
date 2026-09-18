import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

old_start = '      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mt-6">\n        <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">\n          <AlertCircle size={18} className="text-slate-400" /> Draft Expenses ({draftExpenses.length})\n        </h2>'

new_start = '      {activeProduct !== \'hotel\' && (\n      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mt-6">\n        <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">\n          <AlertCircle size={18} className="text-slate-400" /> Draft Expenses ({draftExpenses.length})\n        </h2>'

code = code.replace(old_start, new_start)

old_end = '          emptyMessage="No draft expenses."\n        />\n      </div>'
new_end = '          emptyMessage="No draft expenses."\n        />\n      </div>\n      )}'
code = code.replace(old_end, new_end)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
