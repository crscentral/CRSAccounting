import re

# Fix Dashboard.jsx
with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

code = code.replace("export default const renderCustomLegend", "const renderCustomLegend")
with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)

# Fix HotelBudget.jsx
with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

code = code.replace(r'className=\"py-1.5 px-3 text-slate-500 text-xs font-medium\"', 'className="py-1.5 px-3 text-slate-500 text-xs font-medium"')
code = code.replace(r'className=\"py-1.5 px-3 text-slate-500 text-xs\"', 'className="py-1.5 px-3 text-slate-500 text-xs"')

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
