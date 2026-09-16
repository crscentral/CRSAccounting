import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    code = f.read()

# Make sure editing state exists
code = code.replace(
    "const [roomModalOpen, setRoomModalOpen] = useState(false)",
    "const [roomModalOpen, setRoomModalOpen] = useState(false)\n  const [editingId, setEditingId] = useState(null)"
)

# Fix openRoomRevenue to clear editingId
code = code.replace(
    "function openRoomRevenue() {",
    "function openRoomRevenue() {\n    setEditingId(null)"
)

# Open Edit Room function
code = code.replace(
    "async function handleDeleteRoom(row) {",
    """function openEditRoom(row) {
    setEditingId(row.id)
    setStatDate(row.stat_date)
    setRoomsOccupied(row.rooms_occupied)
    setCurrency(row.currency || 'USD')
    setRoomRevenue(row.room_revenue)
    setCollected(row.room_revenue_collected)
    setNotes(row.notes || '')
    setRoomModalOpen(true)
  }

  async function handleDeleteRoom(row) {"""
)

# Replace table edit button
code = code.replace(
    """<button onClick={() => handleDeleteRoom(r)} className="text-slate-400 hover:text-red-500"><Trash2 size={14}/></button>""",
    """<div className="flex gap-2">
      <button onClick={() => openEditRoom(r)} className="text-slate-400 hover:text-navy-600"><Pencil size={14}/></button>
      <button onClick={() => handleDeleteRoom(r)} className="text-slate-400 hover:text-red-500"><Trash2 size={14}/></button>
    </div>"""
)

# Same for Ancillary
code = code.replace(
    "function openAncillary() {",
    "function openAncillary() {\n    setEditingId(null)"
)
code = code.replace(
    "async function handleDeleteAncillary(row) {",
    """function openEditAncillary(row) {
    setEditingId(row.id)
    setStatDate(row.entry_date)
    setAccountId(row.account_id)
    setCurrency(row.currency || 'USD')
    setRoomRevenue(row.amount) # reusing state
    setNotes(row.notes || '')
    setAncillaryModalOpen(true)
  }

  async function handleDeleteAncillary(row) {"""
)
code = code.replace(
    """<button onClick={() => handleDeleteAncillary(r)} className="text-slate-400 hover:text-red-500"><Trash2 size={14}/></button>""",
    """<div className="flex gap-2">
      <button onClick={() => openEditAncillary(r)} className="text-slate-400 hover:text-navy-600"><Pencil size={14}/></button>
      <button onClick={() => handleDeleteAncillary(r)} className="text-slate-400 hover:text-red-500"><Trash2 size={14}/></button>
    </div>"""
)

# Realtime ADR / RevPAR text
modal_text = """          <Field label="Amount Collected">
            <input type="number" step="0.01" min="0" value={collected} onChange={e => setCollected(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="If different from Room Revenue" />
          </Field>
        </div>"""
new_modal_text = """          <Field label="Amount Collected">
            <input type="number" step="0.01" min="0" value={collected} onChange={e => setCollected(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="If different from Room Revenue" />
          </Field>
        </div>
        
        <div className="bg-slate-50 border border-slate-100 rounded-lg p-3 text-sm flex items-center justify-around text-slate-600">
          <div>ADR: <strong>{roomsOccupied > 0 && roomRevenue > 0 ? (roomRevenue / roomsOccupied).toFixed(2) : '0.00'}</strong></div>
          <div>RevPAR: <strong>{totalRooms > 0 && roomRevenue > 0 ? (roomRevenue / totalRooms).toFixed(2) : '0.00'}</strong></div>
        </div>"""
code = code.replace(modal_text, new_modal_text)


modal_text_anc = """          <Field label="Amount *">
            <input type="number" step="0.01" min="0" required value={roomRevenue} onChange={e => setRoomRevenue(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>"""
new_modal_text_anc = """          <Field label="Amount *">
            <input type="number" step="0.01" min="0" required value={roomRevenue} onChange={e => setRoomRevenue(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </Field>
        </div>
        
        <div className="bg-slate-50 border border-slate-100 rounded-lg p-3 text-sm flex items-center justify-around text-slate-600">
          <div>Avg per Room Sold: <strong>{totalRooms > 0 && roomRevenue > 0 ? (roomRevenue / (roomStats.find(r => r.stat_date === statDate)?.rooms_occupied || 1)).toFixed(2) : '0.00'}</strong></div>
          <div>Avg per Available Room: <strong>{totalRooms > 0 && roomRevenue > 0 ? (roomRevenue / totalRooms).toFixed(2) : '0.00'}</strong></div>
        </div>"""
code = code.replace(modal_text_anc, new_modal_text_anc)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(code)
