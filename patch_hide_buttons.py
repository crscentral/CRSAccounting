with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

# Replace rendering logic to hide buttons instead of just disabling them for ancillary
old_anc_actions = """    ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => (
      <div className="flex justify-end gap-1">
        <button disabled={isLocked || (r.notes || '').startsWith('Invoice ')} onClick={() => { setEditingRow(r); setAncillaryModalOpen(true) }} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={15} /></button>
        <button disabled={isLocked || (r.notes || '').startsWith('Invoice ')} onClick={() => handleDeleteAncillary(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30"><Trash2 size={15} /></button>
      </div>
    ) }] : []),"""

new_anc_actions = """    ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => {
      const isInvoice = (r.notes || '').startsWith('Invoice ');
      return (
      <div className="flex justify-end gap-1">
        {!isInvoice && <button disabled={isLocked} onClick={() => { setEditingRow(r); setAncillaryModalOpen(true) }} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={15} /></button>}
        {!isInvoice && <button disabled={isLocked} onClick={() => handleDeleteAncillary(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30"><Trash2 size={15} /></button>}
      </div>
    )} }] : []),"""

content = content.replace(old_anc_actions, new_anc_actions)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)
