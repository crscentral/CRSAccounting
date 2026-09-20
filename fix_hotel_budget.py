import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# 1. HIDE the Top Table
old_top_table_start = """        <div key={year} className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-5">
          <div className="min-w-max w-full">
            <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{year} - Room Revenue with ADR & Occ% vs Actual</div>"""
new_top_table_start = """        {activeProduct === 'hotel' && (
        <div key={year} className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-5">
          <div className="min-w-max w-full">
            <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{year} - Room Revenue with ADR & Occ% vs Actual</div>"""
content = content.replace(old_top_table_start, new_top_table_start)

# The end of the top table
old_top_table_end = """              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-10">
          <div className="min-w-max w-full">
            <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{startYear} - Other Revenue vs Actuals</div>"""
new_top_table_end = """              </tbody>
            </table>
          </div>
        </div>
        )}

        <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-10">
          <div className="min-w-max w-full">
            <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{activeProduct === 'restaurant' ? `${startYear} - F&B Revenue & Actual` : `${startYear} - Other Revenue vs Actuals`}</div>"""
content = content.replace(old_top_table_end, new_top_table_end)

# 2. HIDE Seat Inventory
old_inventory_start = """      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6">
        <h3 className="font-semibold text-slate-800 mb-2">{activeProduct === "restaurant" ? "Seat Inventory" : "Room Inventory"}</h3>"""
new_inventory_start = """      {activeProduct === 'hotel' && (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6">
        <h3 className="font-semibold text-slate-800 mb-2">{activeProduct === "restaurant" ? "Seat Inventory" : "Room Inventory"}</h3>"""
content = content.replace(old_inventory_start, new_inventory_start)

old_inventory_end = """          <button disabled={savingRooms} onClick={saveTotalRooms} className="bg-navy-600 hover:bg-navy-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2">
            <Save size={16} /> Save
          </button>
        </div>
      </div>

      <div className="mb-4">
        <div className="flex items-center gap-3">"""
new_inventory_end = """          <button disabled={savingRooms} onClick={saveTotalRooms} className="bg-navy-600 hover:bg-navy-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2">
            <Save size={16} /> Save
          </button>
        </div>
      </div>
      )}

      <div className="mb-4">
        <div className="flex items-center gap-3">"""
content = content.replace(old_inventory_end, new_inventory_end)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
