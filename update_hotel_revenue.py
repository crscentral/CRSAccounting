import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    code = f.read()

# Add lock state to HotelRevenue component
old_state = """  const [modalOpen, setModalOpen] = useState(false)
  const [editingRow, setEditingRow] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)"""

new_state = """  const [modalOpen, setModalOpen] = useState(false)
  const [editingRow, setEditingRow] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)
  const [isLocked, setIsLocked] = useState(localStorage.getItem(`daily_rev_lock_${activeCompany?.id}`) === 'true')"""
code = code.replace(old_state, new_state)

# Add Lock toggle to header actions
old_header = """        actions={
          <div className="flex gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            <button onClick={() => { setEditingRow(null); setModalType('room'); setModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 text-white text-sm font-medium px-3 py-2 rounded-lg hover:bg-navy-700">
              <Plus size={16} /> Room Revenue
            </button>
            <button onClick={() => { setEditingRow(null); setModalType('other'); setModalOpen(true) }} className="flex items-center gap-1.5 bg-white border border-slate-300 text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:bg-slate-50">
              <Plus size={16} /> Other Revenue
            </button>
          </div>
        }"""
new_header = """        actions={
          <div className="flex gap-2 items-center">
            <button onClick={() => {
              const newVal = !isLocked
              setIsLocked(newVal)
              localStorage.setItem(`daily_rev_lock_${activeCompany?.id}`, String(newVal))
            }} className={`flex items-center gap-1.5 border text-sm font-medium px-3 py-2 rounded-lg transition-colors ${isLocked ? 'border-amber-300 bg-amber-50 text-amber-700 hover:bg-amber-100' : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'}`}>
              {isLocked ? '🔒 Unlock Page' : '🔓 Lock Page'}
            </button>
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            <button onClick={() => { setEditingRow(null); setModalType('room'); setModalOpen(true) }} disabled={isLocked} className="flex items-center gap-1.5 bg-navy-600 text-white text-sm font-medium px-3 py-2 rounded-lg hover:bg-navy-700 disabled:opacity-50 disabled:cursor-not-allowed">
              <Plus size={16} /> Room Revenue
            </button>
            <button onClick={() => { setEditingRow(null); setModalType('other'); setModalOpen(true) }} disabled={isLocked} className="flex items-center gap-1.5 bg-white border border-slate-300 text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed">
              <Plus size={16} /> Other Revenue
            </button>
          </div>
        }"""
code = code.replace(old_header, new_header)

# Add lock message above tables
old_table_section = """      <h3 className="text-base font-semibold text-slate-800 mb-3">Room Revenue</h3>"""
new_table_section = """      {isLocked && (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 text-sm px-4 py-3 rounded-lg mb-6 flex items-center gap-2">
          <strong>🔒 Page Locked:</strong> Manual posting is disabled. Revenue is fed automatically from the Guest Invoices page. Click 'Unlock Page' above if you need to add manual walk-in entries.
        </div>
      )}
      <h3 className="text-base font-semibold text-slate-800 mb-3">Room Revenue</h3>"""
code = code.replace(old_table_section, new_table_section)

# Update DataTable columns for Room Revenue
old_columns = """      <DataTable
        columns={[
          { key: 'stat_date', label: 'Date' },
          { key: 'rooms_occupied', label: 'Rooms Occupied' },
          { key: 'room_revenue', label: 'Room Revenue', render: r => cp.fmt(r.room_revenue_usd) },
          { key: 'room_revenue_collected', label: 'Collected', render: r => cp.fmt(r.room_revenue_collected_usd) },
          {
            key: 'actions', label: '', render: r => (
              <button onClick={() => handleDeleteRoomStat(r)} className="text-slate-400 hover:text-red-500 p-1"><Trash2 size={16} /></button>
            )
          }
        ]}
        rows={roomStats}
      />"""

new_columns = """      <DataTable
        columns={[
          { key: 'stat_date', label: 'Date' },
          { key: 'rooms_occ', label: 'Rooms Occ.', render: r => <div>{r.rooms_occupied}<div className="text-[10px] text-slate-400">({r.manual_rooms_occupied||0} man. + {r.invoiced_rooms_occupied||0} inv.)</div></div> },
          { key: 'room_revenue', label: 'Total Room Rev', render: r => <div><span className="font-semibold">{cp.fmt(r.room_revenue_usd)}</span><div className="text-[10px] text-slate-500">({cp.fmt(r.manual_room_revenue_usd||0)} man. + {cp.fmt(r.invoiced_room_revenue_usd||0)} inv.)</div></div> },
          { key: 'room_revenue_collected', label: 'Collected', render: r => <div><span className="font-semibold">{cp.fmt(r.room_revenue_collected_usd)}</span><div className="text-[10px] text-slate-500">({cp.fmt(r.manual_room_revenue_collected_usd||0)} man. + {cp.fmt(r.invoiced_room_revenue_usd||0)} inv.)</div></div> },
          {
            key: 'actions', label: '', render: r => (
              <div className="flex justify-end gap-1">
                <button disabled={isLocked} onClick={() => { setEditingRow(r); setModalType('room'); setModalOpen(true) }} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={16} /></button>
                <button disabled={isLocked} onClick={() => handleDeleteRoomStat(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30"><Trash2 size={16} /></button>
              </div>
            )
          }
        ]}
        rows={roomStats}
      />"""
code = code.replace(old_columns, new_columns)

# Make same Pencil edit button for Other Revenue table
old_other = """<button onClick={() => handleDeleteOtherStat(r)} className="text-slate-400 hover:text-red-500 p-1"><Trash2 size={16} /></button>"""
new_other = """<div className="flex justify-end gap-1">
                <button disabled={isLocked} onClick={() => { setEditingRow(r); setModalType('other'); setModalOpen(true) }} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={16} /></button>
                <button disabled={isLocked} onClick={() => handleDeleteOtherStat(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30"><Trash2 size={16} /></button>
              </div>"""
code = code.replace(old_other, new_other)


# Update RoomRevenueFormModal state and submit logic
old_form = """function RoomRevenueFormModal({ companyId, product, totalRooms, editingRow, onClose, onSaved }) {
  const [statDate, setStatDate] = useState(editingRow?.stat_date || new Date().toISOString().slice(0, 10))
  const [roomsOccupied, setRoomsOccupied] = useState(editingRow?.rooms_occupied ?? '')
  const [currency, setCurrency] = useState(editingRow?.currency || 'USD')
  const [roomRevenue, setRoomRevenue] = useState(editingRow?.room_revenue ?? '')
  const [collected, setCollected] = useState(editingRow?.room_revenue_collected ?? '')
  const [notes, setNotes] = useState(editingRow?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!statDate || Number(roomRevenue) <= 0) { setError('Date and Room Revenue are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, stat_date: statDate, rooms_occupied: Number(roomsOccupied) || 0,
        currency, fx_rate_locked: fxRate,
        room_revenue: Number(roomRevenue), room_revenue_collected: Number(collected) || 0,
        room_revenue_usd: Math.round(Number(roomRevenue) / fxRate * 100) / 100,
        room_revenue_collected_usd: Math.round((Number(collected) || 0) / fxRate * 100) / 100,
        notes: notes || null
      }
      if (editingRow) {
        const { error: err } = await supabase.from('hotel_room_stats').update(payload).eq('id', editingRow.id)
        if (err) throw err
      } else {
        const { error: err } = await supabase.from('hotel_room_stats').upsert(payload, { onConflict: 'company_id,product,stat_date' })
        if (err) throw err
      }
      onSaved(); onClose()
    } catch (err) {"""

new_form = """function RoomRevenueFormModal({ companyId, product, totalRooms, editingRow, onClose, onSaved }) {
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
      // Note: room_revenue and rooms_occupied totals are computed automatically by the Postgres BEFORE trigger using these manual values + invoiced values!
      
      if (editingRow) {
        const { error: err } = await supabase.from('hotel_room_stats').update(payload).eq('id', editingRow.id)
        if (err) throw err
      } else {
        const { error: err } = await supabase.from('hotel_room_stats').upsert(payload, { onConflict: 'company_id,product,stat_date' })
        if (err) throw err
      }
      onSaved(); onClose()
    } catch (err) {"""
code = code.replace(old_form, new_form)

# Add Pencil to lucide-react import
code = code.replace("Plus, Trash2", "Plus, Trash2, Pencil")

# Fix modal field labels to clearly say Manual
old_fields = """        <div className="grid grid-cols-2 gap-4">
          <Field label="Currency" type="select" value={currency} onChange={setCurrency} options={CURRENCY_LIST.map(c => ({ value: c.code, label: `${c.code} - ${c.name}` }))} />
          <Field label="Total Room Revenue (including invoices)" type="number" min="0" step="0.01" value={roomRevenue} onChange={setRoomRevenue} />
        </div>
        <div className="text-xs text-slate-500 bg-slate-50 p-2 rounded border border-slate-200 mt-2">
          <strong>Note:</strong> Guest Invoices automatically add to this total. Editing this value overrides the grand total for the day.
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Amount Collected" type="number" min="0" step="0.01" value={collected} onChange={setCollected} />
        </div>"""

new_fields = """        <div className="grid grid-cols-2 gap-4">
          <Field label="Currency" type="select" value={currency} onChange={setCurrency} options={CURRENCY_LIST.map(c => ({ value: c.code, label: `${c.code} - ${c.name}` }))} />
          <Field label="Manual Room Revenue" type="number" min="0" step="0.01" value={roomRevenue} onChange={setRoomRevenue} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Manual Amount Collected" type="number" min="0" step="0.01" value={collected} onChange={setCollected} />
        </div>
        <div className="text-xs text-slate-500 bg-slate-50 p-2 rounded border border-slate-200 mt-2">
          <strong>Additive Architecture:</strong> This form only manages <em>manual</em> (walk-in) revenue. The database will automatically add this manual revenue to your generated Guest Invoices to calculate the total Daily Revenue!
        </div>"""
code = code.replace(old_fields, new_fields)


# Finally, for OtherRevenueFormModal
old_other_form = """function OtherRevenueFormModal({ companyId, product, editingRow, onClose, onSaved }) {"""
new_other_form = """function OtherRevenueFormModal({ companyId, product, editingRow, onClose, onSaved }) {
  // If editingRow is set, we need to populate state. Wait, the old code didn't use editingRow.
  const [entryId] = useState(editingRow?.id || null)"""
code = code.replace(old_other_form, new_other_form)

old_other_submit = """      if (editingRow) {
        // ... (wait, old code didn't support editingRow)
      }"""
# Wait, let's just do a clean replace on OtherRevenueFormModal
old_other_modal = """function OtherRevenueFormModal({ companyId, product, editingRow, onClose, onSaved }) {
  const [entryDate, setEntryDate] = useState(new Date().toISOString().slice(0, 10))
  const [accountId, setAccountId] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [amount, setAmount] = useState('')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [accounts, setAccounts] = useState([])

  useEffect(() => {
    supabase.from('accounts').select('*').eq('company_id', companyId).eq('product', product).eq('type', 'Revenue').neq('code', '4010').order('code')
      .then(({ data }) => setAccounts(data || []))
  }, [companyId, product])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!entryDate || !accountId || Number(amount) <= 0) { setError('Date, Revenue Head, and Amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, entry_date: entryDate, account_id: accountId,
        currency, fx_rate_locked: fxRate, amount: Number(amount), amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null
      }
      const { error: err } = await supabase.from('hotel_revenue_entries').insert(payload)
      if (err) throw err
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
      setSaving(false)
    }
  }"""

new_other_modal = """function OtherRevenueFormModal({ companyId, product, editingRow, onClose, onSaved }) {
  const [entryDate, setEntryDate] = useState(editingRow?.entry_date || new Date().toISOString().slice(0, 10))
  const [accountId, setAccountId] = useState(editingRow?.account_id || '')
  const [currency, setCurrency] = useState(editingRow?.currency || 'USD')
  const [amount, setAmount] = useState(editingRow?.amount ?? '')
  const [notes, setNotes] = useState(editingRow?.notes || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [accounts, setAccounts] = useState([])

  useEffect(() => {
    supabase.from('accounts').select('*').eq('company_id', companyId).eq('product', product).eq('type', 'Revenue').neq('code', '4010').order('code')
      .then(({ data }) => setAccounts(data || []))
  }, [companyId, product])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!entryDate || !accountId || Number(amount) <= 0) { setError('Date, Revenue Head, and Amount are required.'); return }
    setSaving(true)
    try {
      const fxRate = currency === 'USD' ? 1 : (await getLatestRate(currency)) || 1
      const payload = {
        company_id: companyId, product, entry_date: entryDate, account_id: accountId,
        currency, fx_rate_locked: fxRate, amount: Number(amount), amount_usd: Math.round(Number(amount) / fxRate * 100) / 100,
        notes: notes || null
      }
      if (editingRow) {
        const { error: err } = await supabase.from('hotel_revenue_entries').update(payload).eq('id', editingRow.id)
        if (err) throw err
      } else {
        const { error: err } = await supabase.from('hotel_revenue_entries').insert(payload)
        if (err) throw err
      }
      onSaved(); onClose()
    } catch (err) {
      setError(err.message)
      setSaving(false)
    }
  }"""
code = code.replace(old_other_modal, new_other_modal)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(code)
