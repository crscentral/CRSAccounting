with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

old_actions = """          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => (
            <div className="flex justify-end gap-1">
              <button disabled={isLocked} onClick={() => { setEditingRow(r); setRoomModalOpen(true) }} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={15} /></button>
              <button disabled={isLocked || (r.notes || '').startsWith('Invoice ')} onClick={() => handleDeleteRoom(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30" title={(r.notes || '').startsWith('Invoice ') ? "Delete from Guest Invoices page" : "Delete"}><Trash2 size={15} /></button>
            </div>
          ) }] : []),"""

new_actions = """          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => {
            const hasManual = (r.manual_rooms_occupied || 0) > 0 || (r.manual_room_revenue_usd || 0) > 0;
            return (
            <div className="flex justify-end gap-1">
              {hasManual && <button disabled={isLocked} onClick={() => { setEditingRow(r); setRoomModalOpen(true) }} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={15} /></button>}
              {hasManual && <button disabled={isLocked} onClick={() => handleDeleteRoom(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30" title="Delete Manual Entry"><Trash2 size={15} /></button>}
            </div>
          )} }] : []),"""

content = content.replace(old_actions, new_actions)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)
