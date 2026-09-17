import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    code = f.read()

old_room_rev_ui = """        <div className="grid grid-cols-2 gap-4">
          <Field label="Currency" type="select" value={currency} onChange={setCurrency} options={CURRENCY_LIST.map(c => ({ value: c.code, label: `${c.code} - ${c.name}` }))} />
          <Field label="Total Room Revenue" type="number" min="0" step="0.01" value={roomRevenue} onChange={setRoomRevenue} />
        </div>"""

new_room_rev_ui = """        <div className="grid grid-cols-2 gap-4">
          <Field label="Currency" type="select" value={currency} onChange={setCurrency} options={CURRENCY_LIST.map(c => ({ value: c.code, label: `${c.code} - ${c.name}` }))} />
          <Field label="Total Room Revenue (including invoices)" type="number" min="0" step="0.01" value={roomRevenue} onChange={setRoomRevenue} />
        </div>
        <div className="text-xs text-slate-500 bg-slate-50 p-2 rounded border border-slate-200 mt-2">
          <strong>Note:</strong> Guest Invoices automatically add to this total. Editing this value overrides the grand total for the day.
        </div>"""
code = code.replace(old_room_rev_ui, new_room_rev_ui)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(code)
