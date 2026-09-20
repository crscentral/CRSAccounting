import sys

with open('src/pages/HotelBudget.jsx', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '{years.map(year => (' in line:
        # replace the next few lines
        lines[i+1] = ""
        lines[i+2] = ""
        lines[i+3] = "        activeProduct === 'hotel' && (<div key={year} className=\"bg-white rounded-xl border border-slate-200 overflow-x-auto mb-5\">\n"
        break

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.writelines(lines)
