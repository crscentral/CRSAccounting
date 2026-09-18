import re

with open('src/pages/HotelGuestInvoices.jsx', 'r') as f:
    code = f.read()

old_jsx = """        <div className="grid grid-cols-2 gap-3">
          <Field label="Invoice Final Amount *">
            <input type="number" step="0.01" min="0" required value={invoiceAmount} onChange={e => setInvoiceAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Amount Collected">
            <input type="number" step="0.01" min="0" value={collectedAmount} onChange={e => setCollectedAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>"""

new_jsx = """        <div className="grid grid-cols-2 gap-3 border-t border-slate-200 pt-3 mt-1">
          <Field label="Room Rate">
            <input type="number" step="0.01" min="0" value={roomRate} onChange={e => setRoomRate(e.target.value)} placeholder="Per night" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Nights">
            <input type="number" min="0" value={nights} onChange={e => setNights(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2 mt-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-700">Other Revenue (Ancillary)</label>
            <button type="button" onClick={() => setLineItems([...lineItems, { account_id: '', amount: '' }])} className="text-xs text-navy-600 font-medium hover:text-navy-800 flex items-center gap-1">
              <Plus size={14}/> Add Item
            </button>
          </div>
          {lineItems.map((li, i) => (
            <div key={i} className="flex gap-2 items-center">
              <select value={li.account_id} onChange={e => { const nu = [...lineItems]; nu[i].account_id = e.target.value; setLineItems(nu) }} className="flex-1 border border-slate-300 rounded py-1 px-2 text-sm">
                <option value="">Select Revenue Head...</option>
                {revenueAccounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
              </select>
              <input type="number" step="0.01" min="0" placeholder="Amount" value={li.amount} onChange={e => { const nu = [...lineItems]; nu[i].amount = e.target.value; setLineItems(nu) }} className="w-24 border border-slate-300 rounded py-1 px-2 text-sm" />
              <button type="button" onClick={() => setLineItems(lineItems.filter((_, idx) => idx !== i))} className="text-slate-400 hover:text-red-500"><Trash2 size={16}/></button>
            </div>
          ))}
          {lineItems.length === 0 && <div className="text-xs text-slate-400 italic">No extra charges.</div>}
        </div>

        <div className="grid grid-cols-2 gap-3 border-t border-slate-200 pt-3">
          <div className="flex flex-col">
            <span className="text-xs font-medium text-slate-700 mb-1">Invoice Final Amount *</span>
            <div className="w-full border border-slate-200 bg-slate-50 rounded-lg px-3 py-2 text-sm font-semibold text-slate-800">
              {Number(invoiceAmount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
          </div>
          <Field label="Amount Collected">
            <input type="number" step="0.01" min="0" value={collectedAmount} onChange={e => setCollectedAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>"""
code = code.replace(old_jsx, new_jsx)

with open('src/pages/HotelGuestInvoices.jsx', 'w') as f:
    f.write(code)
