import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# 1. Hide Seat Inventory
old_inventory_start = '      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">'
new_inventory_start = "      {activeProduct === 'hotel' && (<div className=\"bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6\">"
content = content.replace(old_inventory_start, new_inventory_start)

old_inventory_end = """          )}
        </div>
      </div>

      {thisMonthRow && ("""
new_inventory_end = """          )}
        </div>
      </div>)}

      {thisMonthRow && ("""
content = content.replace(old_inventory_end, new_inventory_end)

# 2. Hide Top Table
old_top_table_start = """      {years.map(year => (
        <div key={year} className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-5">"""
new_top_table_start = """      {years.map(year => activeProduct === 'hotel' ? (
        <div key={year} className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-5">"""
content = content.replace(old_top_table_start, new_top_table_start)

old_top_table_end = """          </table>
          </div>
        </div>
      ))}"""
new_top_table_end = """          </table>
          </div>
        </div>
      ) : null)}"""
content = content.replace(old_top_table_end, new_top_table_end)

# 3. Rename Middle Table
old_middle_table_title = '<div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{startYear} - Other Revenue vs Actuals</div>'
new_middle_table_title = "<div className=\"px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm\">{activeProduct === 'restaurant' ? `${startYear} - F&B Revenue & Actual` : `${startYear} - Other Revenue vs Actuals`}</div>"
content = content.replace(old_middle_table_title, new_middle_table_title)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
