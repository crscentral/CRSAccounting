import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    code = f.read()

# I need to add editingRow state and pass it down.
# Let's replace the whole modal rendering block.
modal_render = """      {roomModalOpen && (
        <RoomRevenueFormModal companyId={activeCompany.id} product={activeProduct} onClose={() => setRoomModalOpen(false)} onSaved={loadAll} />
      )}
      {ancillaryModalOpen && (
        <AncillaryRevenueFormModal companyId={activeCompany.id} product={activeProduct} accounts={revenueAccounts} onClose={() => setAncillaryModalOpen(false)} onSaved={loadAll} />
      )}"""
new_modal_render = """      {roomModalOpen && (
        <RoomRevenueFormModal companyId={activeCompany.id} product={activeProduct} totalRooms={totalRooms} editingRow={editingRow} onClose={() => { setRoomModalOpen(false); setEditingRow(null); }} onSaved={loadAll} />
      )}
      {ancillaryModalOpen && (
        <AncillaryRevenueFormModal companyId={activeCompany.id} product={activeProduct} accounts={revenueAccounts} totalRooms={totalRooms} editingRow={editingRow} roomStats={roomStats} onClose={() => { setAncillaryModalOpen(false); setEditingRow(null); }} onSaved={loadAll} />
      )}"""
code = code.replace(modal_render, new_modal_render)

# Add editingRow state
code = code.replace(
    "const [roomModalOpen, setRoomModalOpen] = useState(false)\n  const [editingId, setEditingId] = useState(null)",
    "const [roomModalOpen, setRoomModalOpen] = useState(false)\n  const [editingRow, setEditingRow] = useState(null)"
)
code = code.replace(
    "const [roomModalOpen, setRoomModalOpen] = useState(false)",
    "const [roomModalOpen, setRoomModalOpen] = useState(false)\n  const [editingRow, setEditingRow] = useState(null)"
)

# Open edit functions
code = code.replace(
    """function openEditRoom(row) {
    setEditingId(row.id)
    setStatDate(row.stat_date)
    setRoomsOccupied(row.rooms_occupied)
    setCurrency(row.currency || 'USD')
    setRoomRevenue(row.room_revenue)
    setCollected(row.room_revenue_collected)
    setNotes(row.notes || '')
    setRoomModalOpen(true)
  }""",
    """function openEditRoom(row) {
    setEditingRow(row)
    setRoomModalOpen(true)
  }"""
)

code = code.replace(
    """function openEditAncillary(row) {
    setEditingId(row.id)
    setStatDate(row.entry_date)
    setAccountId(row.account_id)
    setCurrency(row.currency || 'USD')
    setRoomRevenue(row.amount) # reusing state
    setNotes(row.notes || '')
    setAncillaryModalOpen(true)
  }""",
    """function openEditAncillary(row) {
    setEditingRow(row)
    setAncillaryModalOpen(true)
  }"""
)

# Replace RoomRevenueFormModal signature and init
code = code.replace(
    "function RoomRevenueFormModal({ companyId, product, onClose, onSaved }) {",
    "function RoomRevenueFormModal({ companyId, product, totalRooms, editingRow, onClose, onSaved }) {"
)
code = code.replace(
    "const [statDate, setStatDate] = useState(new Date().toISOString().slice(0, 10))",
    "const [statDate, setStatDate] = useState(editingRow?.stat_date || new Date().toISOString().slice(0, 10))"
)
code = code.replace(
    "const [roomsOccupied, setRoomsOccupied] = useState('')",
    "const [roomsOccupied, setRoomsOccupied] = useState(editingRow?.rooms_occupied ?? '')"
)
code = code.replace(
    "const [currency, setCurrency] = useState('USD')",
    "const [currency, setCurrency] = useState(editingRow?.currency || 'USD')"
)
code = code.replace(
    "const [roomRevenue, setRoomRevenue] = useState('')",
    "const [roomRevenue, setRoomRevenue] = useState(editingRow?.room_revenue ?? '')"
)
code = code.replace(
    "const [collected, setCollected] = useState('')",
    "const [collected, setCollected] = useState(editingRow?.room_revenue_collected ?? '')"
)
code = code.replace(
    "const [notes, setNotes] = useState('')",
    "const [notes, setNotes] = useState(editingRow?.notes || '')"
)

# Replace RoomRevenueFormModal Upsert logic to handle id update if we aren't changing the date
# Wait, if stat_date is the conflict key, and we change stat_date, upsert might create a duplicate!
# Wait! In hotel_room_stats, there is NO unique constraint on `company_id, product, stat_date`.
# But they use `upsert(..., { onConflict: 'company_id,product,stat_date' })`!
# Let's just use `update().eq('id', editingRow.id)` if `editingRow` exists!
code = code.replace(
    """      const { error: err } = await supabase.from('hotel_room_stats').upsert({
        company_id: companyId, product, stat_date: statDate, rooms_occupied: Number(roomsOccupied) || 0,
        currency, fx_rate_locked: fxRate,
        room_revenue: Number(roomRevenue), room_revenue_collected: Number(collected) || 0,
        room_revenue_usd: Math.round(Number(roomRevenue) / fxRate * 100) / 100,
        room_revenue_collected_usd: Math.round((Number(collected) || 0) / fxRate * 100) / 100,
        notes: notes || null,
      }, { onConflict: 'company_id,product,stat_date' })""",
    """      const payload = {
        company_id: companyId, product, stat_date: statDate, rooms_occupied: Number(roomsOccupied) || 0,
        currency, fx_rate_locked: fxRate,
        room_revenue: Number(roomRevenue), room_revenue_collected: Number(collected) || 0,
        room_revenue_usd: Math.round(Number(roomRevenue) / fxRate * 100) / 100,
        room_revenue_collected_usd: Math.round((Number(collected) || 0) / fxRate * 100) / 100,
        notes: notes || null,
      }
      let err = null
      if (editingRow) {
        const { error } = await supabase.from('hotel_room_stats').update(payload).eq('id', editingRow.id)
        err = error
      } else {
        const { error } = await supabase.from('hotel_room_stats').upsert(payload, { onConflict: 'company_id,product,stat_date' })
        err = error
      }"""
)


# AncillaryRevenueFormModal
code = code.replace(
    "function AncillaryRevenueFormModal({ companyId, product, accounts, onClose, onSaved }) {",
    "function AncillaryRevenueFormModal({ companyId, product, accounts, totalRooms, editingRow, roomStats, onClose, onSaved }) {"
)
code = code.replace(
    "const [statDate, setStatDate] = useState(new Date().toISOString().slice(0, 10))",
    "const [statDate, setStatDate] = useState(editingRow?.entry_date || new Date().toISOString().slice(0, 10))"
)
# We have 2 instances of this, the first is in RoomRevenue (already replaced), the second in Ancillary.
# Wait, the replace string won't find it if it was already replaced! Let's do a more robust regex.

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(code)
