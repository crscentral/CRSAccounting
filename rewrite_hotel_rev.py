import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    code = f.read()

# 1. Add lock state
old_states = """  const [modalOpen, setModalOpen] = useState(false)
  const [editingRow, setEditingRow] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)"""

new_states = """  const [roomModalOpen, setRoomModalOpen] = useState(false)
  const [ancillaryModalOpen, setAncillaryModalOpen] = useState(false)
  const [newHeadModalOpen, setNewHeadModalOpen] = useState(false)
  const [editingRow, setEditingRow] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)
  const [isLocked, setIsLocked] = useState(localStorage.getItem(`daily_rev_lock_${activeCompany?.id}`) === 'true')"""
# Wait, let's just do a clean replace using regex or find/replace on known strings.

code = re.sub(r'const \[roomModalOpen, setRoomModalOpen\] = useState\(false\)\n  const \[ancillaryModalOpen, setAncillaryModalOpen\] = useState\(false\)\n  const \[newHeadModalOpen, setNewHeadModalOpen\] = useState\(false\)\n  const \[editingRow, setEditingRow\] = useState\(null\)\n  const \[reportModalOpen, setReportModalOpen\] = useState\(false\)', new_states, code)

# 2. Add lock button to header actions
old_header_actions = """        actions={
          <div className="flex gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin', 'accountant']) && (
              <>
                <button onClick={() => { setEditingRow(null); setRoomModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 text-white text-sm font-medium px-3 py-2 rounded-lg hover:bg-navy-700">
                  <Plus size={16} /> Room Revenue
                </button>
                <button onClick={() => { setEditingRow(null); setAncillaryModalOpen(true) }} className="flex items-center gap-1.5 bg-white border border-slate-300 text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:bg-slate-50">
                  <Plus size={16} /> Other Revenue
                </button>
              </>
            )}
          </div>
        }"""

new_header_actions = """        actions={
          <div className="flex gap-2 items-center">
            {can(['owner', 'admin']) && (
              <button onClick={() => {
                const newVal = !isLocked
                setIsLocked(newVal)
                localStorage.setItem(`daily_rev_lock_${activeCompany?.id}`, String(newVal))
              }} className={`flex items-center gap-1.5 border text-sm font-medium px-3 py-2 rounded-lg transition-colors ${isLocked ? 'border-amber-300 bg-amber-50 text-amber-700 hover:bg-amber-100' : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'}`}>
                {isLocked ? '🔒 Unlock Page' : '🔓 Lock Page'}
              </button>
            )}
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin', 'accountant']) && (
              <>
                <button disabled={isLocked} onClick={() => { setEditingRow(null); setRoomModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 text-white text-sm font-medium px-3 py-2 rounded-lg hover:bg-navy-700 disabled:opacity-50 disabled:cursor-not-allowed">
                  <Plus size={16} /> Room Revenue
                </button>
                <button disabled={isLocked} onClick={() => { setEditingRow(null); setAncillaryModalOpen(true) }} className="flex items-center gap-1.5 bg-white border border-slate-300 text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed">
                  <Plus size={16} /> Other Revenue
                </button>
              </>
            )}
          </div>
        }"""
code = code.replace(old_header_actions, new_header_actions)

# 3. Add lock message and rewrite room revenue table
old_room_section = """      <h3 className="font-semibold text-slate-700 mb-3">Room Revenue</h3>
      <DataTable
        columns={[
          { key: 'stat_date', label: 'Date' },
          { key: 'rooms_occupied', label: 'Rooms Occupied' },
          { key: 'room_revenue_usd', label: 'Room Revenue', render: r => cp.fmt(r.room_revenue_usd) },
          { key: 'room_revenue_collected_usd', label: 'Collected', render: r => cp.fmt(r.room_revenue_collected_usd) },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => <button onClick={() => handleDeleteRoom(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button> }] : []),
        ]}
        rows={roomStats}
        emptyMessage="No room revenue entries in this range."
      />"""

new_room_section = """      {isLocked && (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 text-sm px-4 py-3 rounded-lg mb-6 flex items-center gap-2">
          <strong>🔒 Page Locked:</strong> Manual posting is disabled. Revenue is fed automatically from the Guest Invoices page. Click 'Unlock Page' above if you need to add manual walk-in entries.
        </div>
      )}
      <h3 className="font-semibold text-slate-700 mb-3">Room Revenue</h3>
      <DataTable
        columns={[
          { key: 'stat_date', label: 'Date' },
          { key: 'rooms_occ', label: 'Rooms Occ.', render: r => <div>{r.rooms_occupied}<div className="text-[10px] text-slate-400">({r.manual_rooms_occupied||0} man. + {r.invoiced_rooms_occupied||0} inv.)</div></div> },
          { key: 'room_revenue', label: 'Total Room Rev', render: r => <div><span className="font-semibold">{cp.fmt(r.room_revenue_usd)}</span><div className="text-[10px] text-slate-500">({cp.fmt(r.manual_room_revenue_usd||0)} man. + {cp.fmt(r.invoiced_room_revenue_usd||0)} inv.)</div></div> },
          { key: 'room_revenue_collected', label: 'Collected', render: r => <div><span className="font-semibold">{cp.fmt(r.room_revenue_collected_usd)}</span><div className="text-[10px] text-slate-500">({cp.fmt(r.manual_room_revenue_collected_usd||0)} man. + {cp.fmt(r.invoiced_room_revenue_usd||0)} inv.)</div></div> },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => (
            <div className="flex justify-end gap-1">
              <button disabled={isLocked} onClick={() => { setEditingRow(r); setRoomModalOpen(true) }} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={15} /></button>
              <button disabled={isLocked} onClick={() => handleDeleteRoom(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30"><Trash2 size={15} /></button>
            </div>
          ) }] : []),
        ]}
        rows={roomStats}
        emptyMessage="No room revenue entries in this range."
      />"""
code = code.replace(old_room_section, new_room_section)


old_ancillary_table = """      <DataTable
        columns={[
          { key: 'entry_date', label: 'Date' },
          { key: 'account', label: 'Revenue Head', render: r => r.account ? `${r.account.code} - ${r.account.name}` : '—' },
          { key: 'amount_usd', label: 'Amount', render: r => cp.fmt(r.amount_usd) },
          { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => <button onClick={() => handleDeleteAncillary(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button> }] : []),
        ]}
        rows={ancillary}
        emptyMessage="No other revenue entries in this range."
      />"""

new_ancillary_table = """      <DataTable
        columns={[
          { key: 'entry_date', label: 'Date' },
          { key: 'account', label: 'Revenue Head', render: r => r.account ? `${r.account.code} - ${r.account.name}` : '—' },
          { key: 'amount_usd', label: 'Amount', render: r => cp.fmt(r.amount_usd) },
          { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => (
            <div className="flex justify-end gap-1">
              <button disabled={isLocked} onClick={() => { setEditingRow(r); setAncillaryModalOpen(true) }} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={15} /></button>
              <button disabled={isLocked} onClick={() => handleDeleteAncillary(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30"><Trash2 size={15} /></button>
            </div>
          ) }] : []),
        ]}
        rows={ancillary}
        emptyMessage="No other revenue entries in this range."
      />"""
code = code.replace(old_ancillary_table, new_ancillary_table)


# Rewrite RoomRevenueFormModal completely
# using regex to just replace the whole function
old_modal_regex = r'function RoomRevenueFormModal\(\{\s*companyId,\s*product,\s*totalRooms,\s*editingRow,\s*onClose,\s*onSaved\s*\}\) \{.*?\n\}'
new_modal_code = """function RoomRevenueFormModal({ companyId, product, totalRooms, editingRow, onClose, onSaved }) {
  const [statDate, setStatDate] = useState(editingRow?.stat_date || new Date().toISOString().slice(0, 10))
  const [roomsOccupied, setRoomsOccupied] = useState(editingRow?.manual_rooms_occupied ?? '')
  const [currency, setCurrency] = useState(editingRow?.currency || 'USD')
  const [roomRevenue, setRoomRevenue] = useState(editingRow?.manual_room_revenue ?? '')
  const [collected, setCollected] = useState(editingRow?.manual_room_revenue_collected ?? '')
  const [notes, setNotes] = useState(editingRow?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!statDate || Number(roomRevenue) < 0) { setError('Date and Room Revenue are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, stat_date: statDate, 
        manual_rooms_occupied: Number(roomsOccupied) || 0,
        currency, fx_rate_locked: fxRate,
        manual_room_revenue: Number(roomRevenue), 
        manual_room_revenue_collected: Number(collected) || 0,
        manual_room_revenue_usd: Math.round(Number(roomRevenue) / fxRate * 100) / 100,
        manual_room_revenue_collected_usd: Math.round((Number(collected) || 0) / fxRate * 100) / 100,
        notes: notes || null
      }
      
      let err = null
      if (editingRow) {
        const { error } = await supabase.from('hotel_room_stats').update(payload).eq('id', editingRow.id)
        err = error
      } else {
        const { error } = await supabase.from('hotel_room_stats').upsert(payload, { onConflict: 'company_id,product,stat_date' })
        err = error
      }
      if (err) throw err
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title={editingRow ? "Edit Manual Room Revenue" : "New Manual Room Revenue"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Field label="Date *">
            <input type="date" required value={statDate} onChange={e => setStatDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Manual Rooms Occupied *">
            <input type="number" min="0" required value={roomsOccupied} onChange={e => setRoomsOccupied(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <Field label="Currency">
          <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
            {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Manual Room Revenue *">
            <input type="number" step="0.01" min="0" required value={roomRevenue} onChange={e => setRoomRevenue(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
          <Field label="Manual Amount Collected">
            <input type="number" step="0.01" min="0" value={collected} onChange={e => setCollected(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <div className="text-xs text-slate-500 bg-slate-50 p-2 rounded border border-slate-200 mt-2">
          <strong>Additive Architecture:</strong> This form only manages <em>manual</em> (walk-in) revenue. The database will automatically add this manual revenue to your generated Guest Invoices to calculate the total Daily Revenue!
        </div>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </Modal>
  )
}
"""

code = re.sub(old_modal_regex, new_modal_code, code, flags=re.DOTALL)


# Rewrite AncillaryRevenueFormModal
old_anc_regex = r'function AncillaryRevenueFormModal\(\{\s*companyId,\s*product,\s*accounts,\s*totalRooms,\s*editingRow,\s*roomStats,\s*onClose,\s*onSaved\s*\}\) \{.*?\n\}'
new_anc_code = """function AncillaryRevenueFormModal({ companyId, product, accounts, totalRooms, editingRow, roomStats, onClose, onSaved }) {
  const [entryDate, setEntryDate] = useState(editingRow?.entry_date || new Date().toISOString().slice(0, 10))
  const [accountId, setAccountId] = useState(editingRow?.account_id || accounts[0]?.id || '')
  const [currency, setCurrency] = useState(editingRow?.currency || 'USD')
  const [amount, setAmount] = useState(editingRow?.amount ?? '')
  const [notes, setNotes] = useState(editingRow?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!accountId || Number(amount) <= 0) { setError('Revenue head and a positive amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, entry_date: entryDate, account_id: accountId,
        amount: Number(amount), currency, fx_rate_locked: fxRate, amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null,
      }
      let err = null
      if (editingRow) {
        const { error } = await supabase.from('hotel_revenue_entries').update(payload).eq('id', editingRow.id)
        err = error
      } else {
        const { error } = await supabase.from('hotel_revenue_entries').insert(payload)
        err = error
      }
      if (err) throw err
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title={editingRow ? "Edit Other Revenue" : "Other Revenue Entry"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Date *">
          <input type="date" required value={entryDate} onChange={e => setEntryDate(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        <Field label="Revenue Head *">
          <select required value={accountId} onChange={e => setAccountId(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
            <option value="">Select…</option>
            {accounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Currency">
            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
          </Field>
          <Field label="Amount *">
            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        <Field label="Notes">
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        {error && <p className="text-xs text-red-600">{error}</p>}
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
          <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">{saving ? 'Saving…' : 'Save'}</button>
        </div>
      </form>
    </Modal>
  )
}
"""
code = re.sub(old_anc_regex, new_anc_code, code, flags=re.DOTALL)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(code)
