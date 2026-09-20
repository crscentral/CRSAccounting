import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    content = f.read()

# I need to construct the DataTables for the 3 sections.
# I already have a DataTable for `roomStats`, `restRevenue`, and `ancillary`

# The `ancillary` DataTable needs to be re-usable.
# I'll create a variable `ancillaryColumns` and then just pass it in to multiple DataTables.
old_dt = """        columns={[
          { key: 'entry_date', label: 'Date' },
          { key: 'account', label: 'Revenue Head', render: r => r.account ? `${r.account.code} - ${r.account.name}` : '—' },
          { key: 'amount_usd', label: 'Amount', render: r => cp.fmt(r.amount_usd) },
          { key: 'collected_usd', label: 'Collected', render: r => cp.fmt(r.collected_usd || 0) },
          { key: 'pending_usd', label: 'Pending Collection', render: r => <span className="text-red-500 font-medium">{cp.fmt((r.amount_usd || 0) - (r.collected_usd || 0))}</span> },
          { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => (
            <div className="flex justify-end gap-1">
              <button disabled={isLocked} onClick={() => { setEditingRow(r); setAncillaryModalOpen(true) }} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={15} /></button>
              <button disabled={isLocked} onClick={() => handleDeleteAncillary(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30"><Trash2 size={15} /></button>
            </div>
          ) }] : []),
        ]}"""

new_col = """  const ancillaryCols = [
    { key: 'entry_date', label: 'Date' },
    { key: 'account', label: 'Revenue Head', render: r => r.account ? `${r.account.code} - ${r.account.name}` : '—' },
    { key: 'amount_usd', label: 'Amount', render: r => cp.fmt(r.amount_usd) },
    { key: 'collected_usd', label: 'Collected', render: r => cp.fmt(r.collected_usd || 0) },
    { key: 'pending_usd', label: 'Pending Collection', render: r => <span className="text-red-500 font-medium">{cp.fmt((r.amount_usd || 0) - (r.collected_usd || 0))}</span> },
    { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
    ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => (
      <div className="flex justify-end gap-1">
        <button disabled={isLocked} onClick={() => { setEditingRow(r); setAncillaryModalOpen(true) }} className="text-slate-400 hover:text-navy-600 p-1 disabled:opacity-30"><Pencil size={15} /></button>
        <button disabled={isLocked} onClick={() => handleDeleteAncillary(r)} className="text-slate-400 hover:text-red-500 p-1 disabled:opacity-30"><Trash2 size={15} /></button>
      </div>
    ) }] : []),
  ]"""

# I need to insert `ancillaryCols` before the return statement.
content = content.replace("  if (!activeCompany) return null", new_col + "\n\n  if (!activeCompany) return null")

# Now I rewrite the UI layout.
# Let's find the `h3` tags.
# Old: <h3 className="font-semibold text-slate-700 mb-3">Room Revenue</h3>
# Old: <h3 className="font-semibold text-slate-700 mb-3 mt-8">F&B Revenue</h3>
# Old: <div className="flex items-center justify-between mb-3 mt-8"> \n <h3 className="font-semibold text-slate-700">Other Revenue (Extra Bed, Early Check-in, Late Check-out, Breakfast, Transportation, SPA, etc.)</h3>

# For Room Revenue Section:
content = content.replace(
"""        rows={roomStats}
        emptyMessage="No room revenue entries in this range."
      />""",
"""        rows={roomStats}
        emptyMessage="No room revenue entries in this range."
      />
      {ancRoom.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-slate-600 mb-2">Room Revenue Postings</h4>
          <DataTable columns={ancillaryCols} data={ancRoom} emptyState="No postings." />
        </div>
      )}"""
)

# For F&B Revenue Section:
content = content.replace(
"""            data={restRevenue}
            emptyState="No F&B revenue entries in this range."
          />
        </>
      )}""",
"""            data={restRevenue}
            emptyState="No F&B revenue entries in this range."
          />
          {ancFB.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-slate-600 mb-2">F&B Revenue Postings</h4>
              <DataTable columns={ancillaryCols} data={ancFB} emptyState="No postings." />
            </div>
          )}
        </>
      )}"""
)

# For Other Revenue Section:
content = content.replace(
"""<h3 className="font-semibold text-slate-700">Other Revenue (Extra Bed, Early Check-in, Late Check-out, Breakfast, Transportation, SPA, etc.)</h3>""",
"""<h3 className="font-semibold text-slate-700">Other Revenue</h3>"""
)

content = content.replace(old_dt, "columns={ancillaryCols}")
content = content.replace("data={ancillary}", "data={ancOther}")

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(content)
