with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

# 1. Disable Edit/Delete for Invoice entries
old_room_actions = """        <button disabled={isLocked} onClick={() => openEditRoom(r)} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={15} /></button>
        <button disabled={isLocked} onClick={() => handleDeleteRoom(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30"><Trash2 size={15} /></button>"""

new_room_actions = """        <button disabled={isLocked || (r.notes || '').startsWith('Invoice ')} onClick={() => openEditRoom(r)} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={15} /></button>
        <button disabled={isLocked || (r.notes || '').startsWith('Invoice ')} onClick={() => handleDeleteRoom(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30"><Trash2 size={15} /></button>"""
content = content.replace(old_room_actions, new_room_actions)

old_ancillary_actions = """        <button disabled={isLocked} onClick={() => { setEditingRow(r); setAncillaryModalOpen(true) }} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={15} /></button>
        <button disabled={isLocked} onClick={() => handleDeleteAncillary(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30"><Trash2 size={15} /></button>"""

new_ancillary_actions = """        <button disabled={isLocked || (r.notes || '').startsWith('Invoice ')} onClick={() => { setEditingRow(r); setAncillaryModalOpen(true) }} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={15} /></button>
        <button disabled={isLocked || (r.notes || '').startsWith('Invoice ')} onClick={() => handleDeleteAncillary(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30"><Trash2 size={15} /></button>"""
content = content.replace(old_ancillary_actions, new_ancillary_actions)

# Wait, there's another place: room actions might not exist in the same way, let's just do a regex replace
import re
content = re.sub(
    r'<button disabled=\{isLocked\} onClick=\{([^}]+)\} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size=\{15\} \/><\/button>',
    r'<button disabled={isLocked || (r.notes || \'\').startsWith(\'Invoice \')} onClick={\1} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30" title={(r.notes || \'\').startsWith(\'Invoice \') ? "Edit from Guest Invoices page" : "Edit"}><Pencil size={15} /></button>',
    content
)
content = re.sub(
    r'<button disabled=\{isLocked\} onClick=\{([^}]+)\} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30"><Trash2 size=\{15\} \/><\/button>',
    r'<button disabled={isLocked || (r.notes || \'\').startsWith(\'Invoice \')} onClick={\1} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30" title={(r.notes || \'\').startsWith(\'Invoice \') ? "Delete from Guest Invoices page" : "Delete"}><Trash2 size={15} /></button>',
    content
)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)
