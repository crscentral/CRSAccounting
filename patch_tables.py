import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

# Generate the flattened arrays right before rendering the tables
flattened_arrays = """  const groupedEntriesMap = {}
  entries.forEach(r => {
    const key = r.account ? `${r.account.code} - ${r.account.name}` : 'Unknown'
    if (!groupedEntriesMap[key]) groupedEntriesMap[key] = { isGroupHeader: true, name: key, amount_usd: 0, paid_amount_usd: 0, transactions: [], account_id: r.account_id }
    groupedEntriesMap[key].amount_usd += Number(r.amount_usd)
    groupedEntriesMap[key].paid_amount_usd += Number(r.paid_amount_usd || 0)
    groupedEntriesMap[key].transactions.push(r)
  })
  const flattenedEntries = []
  Object.values(groupedEntriesMap).sort((a,b) => b.amount_usd - a.amount_usd).forEach(g => {
    flattenedEntries.push({ ...g, id: 'group_' + g.name })
    if (expandedEntries[g.name]) {
      g.transactions.forEach(t => flattenedEntries.push({ ...t, isGroupChild: true }))
    }
  })

  const groupedAmcMap = {}
  amcContracts.forEach(r => {
    const key = r.contract_name || 'Unknown'
    if (!groupedAmcMap[key]) groupedAmcMap[key] = { isGroupHeader: true, name: key, annual_amount_usd: 0, paid_amount_usd: 0, transactions: [] }
    groupedAmcMap[key].annual_amount_usd += Number(r.annual_amount_usd)
    groupedAmcMap[key].paid_amount_usd += Number(r.paid_amount_usd || 0)
    groupedAmcMap[key].transactions.push(r)
  })
  const flattenedAmc = []
  Object.values(groupedAmcMap).sort((a,b) => b.annual_amount_usd - a.annual_amount_usd).forEach(g => {
    flattenedAmc.push({ ...g, id: 'group_' + g.name })
    if (expandedAmc[g.name]) {
      g.transactions.forEach(t => flattenedAmc.push({ ...t, isGroupChild: true }))
    }
  })

  const groupedPIMap = {}
  purchaseInvoices.forEach(r => {
    const key = r.account ? `${r.account.code} - ${r.account.name}` : (r.supplier_name_freeform || 'Unknown')
    if (!groupedPIMap[key]) groupedPIMap[key] = { isGroupHeader: true, name: key, amount_usd: 0, paid: 0, transactions: [] }
    groupedPIMap[key].amount_usd += Number(r.amount_usd)
    groupedPIMap[key].paid += r.status === 'Paid' ? Number(r.amount_usd) : 0
    groupedPIMap[key].transactions.push(r)
  })
  const flattenedPI = []
  Object.values(groupedPIMap).sort((a,b) => b.amount_usd - a.amount_usd).forEach(g => {
    flattenedPI.push({ ...g, id: 'group_' + g.name })
    if (expandedPI[g.name]) {
      g.transactions.forEach(t => flattenedPI.push({ ...t, isGroupChild: true }))
    }
  })
"""

# Find where the UI starts returning (just before activeTab === 'daily')
target_render_start = "return ("
content = content.replace(target_render_start, flattened_arrays + "\n  return (", 1)

# Now replace the DataTable columns for entries
entries_table_target = """      <DataTable
        columns={[
          { key: 'expense_date', label: 'Date' },
          { key: 'invoice_number', label: 'Invoice #', render: r => r.invoice_number || '—' },
          { key: 'account', label: 'Expense Head', render: r => r.account ? `${r.account.code} - ${r.account.name}` : '—' },
          { key: 'amount_usd', label: 'Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.amount_usd)}</span> },
          { key: 'paid', label: 'Paid', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(r.paid_amount_usd || 0)}</span> },
          { key: 'pending', label: 'Pending', render: r => <span className="text-rose-600 font-medium">{cp.fmt(Number(r.amount_usd) - Number(r.paid_amount_usd || 0))}</span> }, 
          { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => <div className="flex gap-2">
      <button onClick={() => { setEditingRow(r); setExpenseModalOpen(true); }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
      <button onClick={() => handleDeleteEntry(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
    </div> }] : []),
        ]}
        rows={entries}"""

entries_table_replacement = """      <DataTable
        columns={[
          { key: 'expense_date', label: 'Date / Head', render: r => r.isGroupHeader ? <button className="font-bold text-navy-700 hover:text-navy-900 flex items-center gap-2" onClick={() => setExpandedEntries(p => ({...p, [r.name]: !p[r.name]}))}>{expandedEntries[r.name] ? '▼' : '▶'} {r.name}</button> : <span className="pl-6 text-slate-500">{r.expense_date}</span> },
          { key: 'invoice_number', label: 'Invoice #', render: r => r.isGroupHeader ? <span className="text-slate-400 text-xs">{r.transactions.length} items</span> : (r.invoice_number || '—') },
          { key: 'amount_usd', label: 'Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.amount_usd)}</span> },
          { key: 'paid', label: 'Paid', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(r.paid_amount_usd || 0)}</span> },
          { key: 'pending', label: 'Pending', render: r => <span className="text-rose-600 font-medium">{cp.fmt(Number(r.amount_usd) - Number(r.paid_amount_usd || 0))}</span> }, 
          { key: 'notes', label: 'Notes', render: r => r.isGroupHeader ? '—' : (r.notes || '—') },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => r.isGroupHeader ? null : <div className="flex gap-2">
      <button onClick={() => { setEditingRow(r); setExpenseModalOpen(true); }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
      <button onClick={() => handleDeleteEntry(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
    </div> }] : []),
        ]}
        rows={flattenedEntries}"""
content = content.replace(entries_table_target, entries_table_replacement)

# Replace AMC table
amc_table_target = """      <DataTable
        columns={[
          { key: 'contract_name', label: 'Contract' },
          { key: 'annual_amount_usd', label: 'Annual Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.annual_amount_usd)}</span> },
          { key: 'annual_paid', label: 'Paid (Yr)', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(r.paid_amount_usd || 0)}</span> },
          { key: 'annual_pending', label: 'Pending (Yr)', render: r => <span className="text-rose-600 font-medium">{cp.fmt(Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0))}</span> },
          { key: 'monthly', label: 'Monthly', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.annual_amount_usd / 12)}</span> },
          { key: 'monthly_paid', label: 'Paid (Mo)', render: r => <span className="text-emerald-600 font-medium">{cp.fmt((r.paid_amount_usd || 0) / 12)}</span> },
          { key: 'monthly_pending', label: 'Pending (Mo)', render: r => <span className="text-rose-600 font-medium">{cp.fmt((Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0)) / 12)}</span> }, 
          { key: 'start', label: 'Starts', render: r => `${MONTH_NAMES[r.start_month - 1]} ${r.start_year}` },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => <div className="flex gap-2">
      <button onClick={() => { setEditingRow(r); setAmcModalOpen(true); }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
      <button onClick={() => handleDeleteAmc(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
    </div> }] : []),
        ]}
        rows={amcContracts}"""

amc_table_replacement = """      <DataTable
        columns={[
          { key: 'contract_name', label: 'Contract', render: r => r.isGroupHeader ? <button className="font-bold text-navy-700 hover:text-navy-900 flex items-center gap-2" onClick={() => setExpandedAmc(p => ({...p, [r.name]: !p[r.name]}))}>{expandedAmc[r.name] ? '▼' : '▶'} {r.name} <span className="text-slate-400 text-xs ml-2 font-normal">({r.transactions.length})</span></button> : <span className="pl-6 text-slate-500">{r.contract_name}</span> },
          { key: 'annual_amount_usd', label: 'Annual Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.annual_amount_usd)}</span> },
          { key: 'annual_paid', label: 'Paid (Yr)', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(r.paid_amount_usd || 0)}</span> },
          { key: 'annual_pending', label: 'Pending (Yr)', render: r => <span className="text-rose-600 font-medium">{cp.fmt(Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0))}</span> },
          { key: 'monthly', label: 'Monthly', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.annual_amount_usd / 12)}</span> },
          { key: 'monthly_paid', label: 'Paid (Mo)', render: r => <span className="text-emerald-600 font-medium">{cp.fmt((r.paid_amount_usd || 0) / 12)}</span> },
          { key: 'monthly_pending', label: 'Pending (Mo)', render: r => <span className="text-rose-600 font-medium">{cp.fmt((Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0)) / 12)}</span> }, 
          { key: 'start', label: 'Starts', render: r => r.isGroupHeader ? '—' : `${MONTH_NAMES[r.start_month - 1]} ${r.start_year}` },
          ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => r.isGroupHeader ? null : <div className="flex gap-2">
      <button onClick={() => { setEditingRow(r); setAmcModalOpen(true); }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
      <button onClick={() => handleDeleteAmc(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
    </div> }] : []),
        ]}
        rows={flattenedAmc}"""
content = content.replace(amc_table_target, amc_table_replacement)

# Replace Purchase Invoices table
pi_table_target = """          <DataTable
            columns={[
              { key: 'date', label: 'Date', render: r => r.invoice_date },
              { key: 'invoice_no', label: 'Invoice #', render: r => r.invoice_number },
              { key: 'supplier', label: 'Supplier', render: r => r.contact?.name || r.supplier_name_freeform || 'Unknown' },
              { key: 'amount', label: 'Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.amount_usd)}</span> },
              { key: 'paid', label: 'Paid', render: r => { const paid = r.status === 'Paid' ? r.amount_usd : 0; return <span className="text-emerald-600 font-medium">{cp.fmt(paid)}</span> } },
              { key: 'pending', label: 'Pending', render: r => { const pending = r.status === 'Paid' ? 0 : r.amount_usd; return <span className="text-rose-600 font-medium">{cp.fmt(pending)}</span> } }, 
              { key: 'status', label: 'Status', render: r => <span className={`px-2 py-0.5 rounded text-xs font-medium ${r.status === 'Draft' ? 'bg-slate-100 text-slate-600' : r.status === 'Approved' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{r.status}</span> },
              ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => <div className="flex justify-end gap-2">
                <button onClick={() => { setEditingRow(r); setPurchaseModalOpen(true); }} className="text-slate-400 hover:text-navy-600 p-1"><Pencil size={15} /></button>
                <button onClick={() => handleDeletePI(r)} className="text-slate-400 hover:text-red-500 p-1"><Trash2 size={15} /></button>
              </div> }] : []),
            ]}
            rows={purchaseInvoices}"""

pi_table_replacement = """          <DataTable
            columns={[
              { key: 'date', label: 'Date / Head', render: r => r.isGroupHeader ? <button className="font-bold text-navy-700 hover:text-navy-900 flex items-center gap-2" onClick={() => setExpandedPI(p => ({...p, [r.name]: !p[r.name]}))}>{expandedPI[r.name] ? '▼' : '▶'} {r.name}</button> : <span className="pl-6 text-slate-500">{r.invoice_date}</span> },
              { key: 'invoice_no', label: 'Invoice #', render: r => r.isGroupHeader ? <span className="text-slate-400 text-xs">{r.transactions.length} items</span> : r.invoice_number },
              { key: 'supplier', label: 'Supplier', render: r => r.isGroupHeader ? '—' : (r.contact?.name || r.supplier_name_freeform || 'Unknown') },
              { key: 'amount', label: 'Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.amount_usd)}</span> },
              { key: 'paid', label: 'Paid', render: r => { const paid = r.isGroupHeader ? r.paid : (r.status === 'Paid' ? r.amount_usd : 0); return <span className="text-emerald-600 font-medium">{cp.fmt(paid)}</span> } },
              { key: 'pending', label: 'Pending', render: r => { const pending = r.isGroupHeader ? (r.amount_usd - r.paid) : (r.status === 'Paid' ? 0 : r.amount_usd); return <span className="text-rose-600 font-medium">{cp.fmt(pending)}</span> } }, 
              { key: 'status', label: 'Status', render: r => r.isGroupHeader ? '—' : <span className={`px-2 py-0.5 rounded text-xs font-medium ${r.status === 'Draft' ? 'bg-slate-100 text-slate-600' : r.status === 'Approved' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{r.status}</span> },
              ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => r.isGroupHeader ? null : <div className="flex justify-end gap-2">
                <button onClick={() => { setEditingRow(r); setPurchaseModalOpen(true); }} className="text-slate-400 hover:text-navy-600 p-1"><Pencil size={15} /></button>
                <button onClick={() => handleDeletePI(r)} className="text-slate-400 hover:text-red-500 p-1"><Trash2 size={15} /></button>
              </div> }] : []),
            ]}
            rows={flattenedPI}"""
content = content.replace(pi_table_target, pi_table_replacement)


with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)
