import re

with open('src/pages/HotelGuestInvoices.jsx', 'r') as f:
    code = f.read()

old_ui = """        <div className="grid grid-cols-2 gap-4">
          <Field label="Check-in Date" type="date" value={checkinDate} onChange={setCheckinDate} />
          <Field label="Check-out Date" type="date" value={checkoutDate} onChange={setCheckoutDate} />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <Field label="Currency" type="select" value={currency} onChange={setCurrency} options={CURRENCY_LIST.map(c => ({ value: c.code, label: `${c.code} - ${c.name}` }))} />
          <Field label="Invoice Amount" type="number" min="0" step="0.01" value={invoiceAmount} onChange={setInvoiceAmount} />
          <Field label="Collected Amount" type="number" min="0" step="0.01" value={collectedAmount} onChange={setCollectedAmount} />
        </div>"""

new_ui = """        <div className="grid grid-cols-2 gap-4">
          <Field label="Check-in Date" type="date" value={checkinDate} onChange={setCheckinDate} />
          <Field label="Check-out Date" type="date" value={checkoutDate} onChange={setCheckoutDate} />
        </div>
        
        <div className="border border-slate-200 rounded-lg p-4 bg-slate-50 space-y-4">
          <h4 className="text-sm font-semibold text-slate-800">Invoice Items</h4>
          
          <div className="grid grid-cols-2 gap-4">
            <Field label="Room Rate" type="number" min="0" step="0.01" value={roomRate} onChange={setRoomRate} />
            <Field label="Nights" type="number" min="0" step="1" value={nights} onChange={setNights} />
          </div>
          <div className="text-sm text-slate-600 mb-2">Room Revenue: <strong className="text-slate-800">{formatMoney(roomRevenue, currency)}</strong></div>
          
          <div className="space-y-2 mt-4">
            <label className="block text-xs font-medium text-slate-600 mb-1">Other Revenue Heads</label>
            {lineItems.map((li, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <select value={li.account_id} onChange={e => { const n = [...lineItems]; n[idx].account_id = e.target.value; setLineItems(n) }} className="flex-1 border border-slate-300 rounded-lg px-2 py-1.5 text-sm bg-white" required>
                  <option value="">Select Revenue Head...</option>
                  {revenueAccounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
                </select>
                <input type="number" min="0" step="0.01" value={li.amount} onChange={e => { const n = [...lineItems]; n[idx].amount = e.target.value; setLineItems(n) }} placeholder="Amount" className="w-24 border border-slate-300 rounded-lg px-2 py-1.5 text-sm" required />
                <input type="text" value={li.notes} onChange={e => { const n = [...lineItems]; n[idx].notes = e.target.value; setLineItems(n) }} placeholder="Notes (optional)" className="w-32 border border-slate-300 rounded-lg px-2 py-1.5 text-sm" />
                <button type="button" onClick={() => setLineItems(lineItems.filter((_, i) => i !== idx))} className="text-red-500 hover:text-red-700 p-1"><Trash2 size={16} /></button>
              </div>
            ))}
            <button type="button" onClick={() => setLineItems([...lineItems, { account_id: '', amount: '', notes: '' }])} className="text-xs font-medium text-navy-600 hover:text-navy-700 flex items-center gap-1 mt-1">
              <Plus size={14} /> Add Revenue Head
            </button>
          </div>
          
          <div className="pt-3 border-t border-slate-200 flex justify-between items-center">
            <span className="text-sm font-semibold text-slate-700">Total Invoice Amount:</span>
            <span className="text-lg font-bold text-navy-700">{formatMoney(invoiceAmount, currency)}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mt-2">
          <Field label="Currency" type="select" value={currency} onChange={setCurrency} options={CURRENCY_LIST.map(c => ({ value: c.code, label: `${c.code} - ${c.name}` }))} />
          <Field label="Collected Amount" type="number" min="0" step="0.01" value={collectedAmount} onChange={setCollectedAmount} />
        </div>"""
code = code.replace(old_ui, new_ui)

with open('src/pages/HotelGuestInvoices.jsx', 'w') as f:
    f.write(code)
