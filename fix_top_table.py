import sys

with open('src/pages/HotelBudget.jsx', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '{year} - Room Revenue with ADR & Occ% vs Actual' in line:
        # The div before it is at i-2
        lines[i-2] = "        {activeProduct === 'hotel' && (<div key={year} className=\"bg-white rounded-xl border border-slate-200 overflow-x-auto mb-5\">\n"
        break

for i, line in enumerate(lines):
    if '{startYear} - Other Revenue vs Actuals' in line:
        # The end of the top table is before this
        lines[i-3] = "        </div>)}\n"
        lines[i] = "            <div className=\"px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm\">{activeProduct === 'restaurant' ? `${startYear} - F&B Revenue & Actual` : `${startYear} - Other Revenue vs Actuals`}</div>\n"
        break

for i, line in enumerate(lines):
    if '{activeProduct === "restaurant" ? "Seat Inventory" : "Room Inventory"}' in line:
        lines[i-2] = "      {activeProduct === 'hotel' && (<div className=\"bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6\">\n"
        break

for i, line in enumerate(lines):
    if '<Save size={16} /> Save' in line:
        # the end of the inventory box
        lines[i+3] = "      </div>)}\n"
        break

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.writelines(lines)
