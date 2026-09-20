import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "{activeProduct === 'hotel' && (<div className=\"bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6\">\n      <div className=\"bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6\">",
    "{activeProduct === 'hotel' && (<div className=\"bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6\">"
)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
