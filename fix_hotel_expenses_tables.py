import re

def patch():
    with open('src/pages/HotelExpenses.jsx', 'r') as f:
        content = f.read()

    # Define the derived arrays
    old_entriesTotalUsd = "const entriesTotalUsd = entries.reduce((s, r) => s + Number(r.amount_usd), 0)"
    new_entriesTotalUsd = """const entriesTotalUsd = entries.reduce((s, r) => s + Number(r.amount_usd), 0)
  const hotelEntries = entries.filter(e => e.product === 'hotel')
  const restEntries = entries.filter(e => e.product === 'restaurant')
  const hotelAmc = amcContracts.filter(a => a.product === 'hotel')
  const restAmc = amcContracts.filter(a => a.product === 'restaurant')
  const hotelPI = purchaseInvoices.filter(p => p.product === 'hotel')
  const restPI = purchaseInvoices.filter(p => p.product === 'restaurant')
  
  const hotelEntriesTotal = hotelEntries.reduce((s, r) => s + Number(r.amount_usd), 0)
  const restEntriesTotal = restEntries.reduce((s, r) => s + Number(r.amount_usd), 0)"""
    content = content.replace(old_entriesTotalUsd, new_entriesTotalUsd)

    # Now replace the daily tab rendering
    # We want to replace the first Daily Expense Entries header
    old_daily_header = """      {activeTab === 'daily' && (
        <>
          <div className="flex justify-between items-end mb-3">
            <div>
              <h3 className="font-semibold text-slate-700 flex items-center gap-3">
                <span>Daily Expense Entries</span>
            {can(['owner', 'admin', 'accountant']) && (
              <button onClick={() => setNewHeadModalOpen(true)} className="text-xs text-navy-600 hover:text-navy-800 font-medium">+ Add Expense Head</button>
            )}
          </h3>
        </div>
        <div className="text-sm text-slate-500 font-medium">
          Total Heads: {new Set(entries.map(e => e.account_id)).size} &bull; Total Amount: {cp.fmt(entriesTotalUsd)}
        </div>
      </div>
      <DataTable
        columns={[
          { key: 'expense_date', label: 'Date' },
          { key: 'invoice_number', label: 'Invoice #', render: r => r.invoice_number || '—' },
          { key: 'account', label: 'Expense Head', render: r => r.account ? `${r.account.code} - ${r.account.name}` : '—' },
          { key: 'amount_usd', label: 'Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.amount_usd)}</span> },
          { key: 'paid_amount', label: 'Paid', render: r => <span className="font-medium text-emerald-600">{cp.fmt(r.paid_amount_usd || 0)}</span> },
          { key: 'pending_amount', label: 'Pending', render: r => <span className="font-medium text-red-500">{cp.fmt(Number(r.amount_usd) - Number(r.paid_amount_usd || 0))}</span> },
          { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
          ...(can(['owner', 'admin', 'accountant']) ? [{
            key: 'actions', label: '', render: r => (
              <div className="flex justify-end gap-2 text-slate-400">
                <button onClick={() => { setEditingExp(r); setExpModalOpen(true) }} className="hover:text-navy-600"><Edit3 size={15} /></button>
                <button onClick={() => handleDeleteEntry(r)} className="hover:text-red-600"><Trash2 size={15} /></button>
              </div>
            )
          }] : []),
        ]}
        rows={entries}
        emptyMessage="No expense entries in this range."
      />

      <h3 className="font-semibold text-slate-700 mb-3 mt-6">AMC Contracts (auto-split across 12 months)</h3>
      <DataTable
        columns={[
          { key: 'contract_name', label: 'Contract' },
          { key: 'annual_amount_usd', label: 'Annual Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.annual_amount_usd)}</span> },
          { key: 'annual_paid', label: 'Paid (Yr)', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(r.paid_amount_usd || 0)}</span> },
          { key: 'annual_pending', label: 'Pending (Yr)', render: r => <span className="text-red-500 font-medium">{cp.fmt(Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0))}</span> },
          { key: 'monthly_amount_usd', label: 'Monthly', render: r => <span className="font-medium text-slate-700">{cp.fmt(Number(r.annual_amount_usd)/12)}</span> },
          { key: 'monthly_paid', label: 'Paid (Mo)', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(Number(r.paid_amount_usd || 0)/12)}</span> },
          { key: 'monthly_pending', label: 'Pending (Mo)', render: r => <span className="text-red-500 font-medium">{cp.fmt((Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0))/12)}</span> },
          { key: 'start_date', label: 'Starts', render: r => { const d = new Date(r.start_date); return `${d.toLocaleString('default', {month:'long'})} ${d.getFullYear()}` } },
          ...(can(['owner', 'admin', 'accountant']) ? [{
            key: 'actions', label: '', render: r => (
              <div className="flex justify-end gap-2 text-slate-400">
                <button onClick={() => { setEditingAmc(r); setAmcModalOpen(true) }} className="hover:text-navy-600"><Edit3 size={15} /></button>
                <button onClick={() => handleDeleteAmc(r)} className="hover:text-red-600"><Trash2 size={15} /></button>
              </div>
            )
          }] : []),
        ]}
        rows={amcContracts}
        emptyMessage="No AMC contracts created."
      />
    </>
  )}"""

    # We want to use a generalized column definition to avoid massive code duplication
    
    # Let's extract the column arrays from the code to make it cleaner.
    # Actually it's fine to just replace `rows={entries}` with `rows={hotelEntries}` and then duplicate the JSX for Restaurant.
    # To be safe with regex/replace, I'll build the replacement string precisely based on the old_daily_header string structure.
    
    new_daily_header = old_daily_header.replace(
        "<span>Daily Expense Entries</span>", "<span>Hotel Daily Expense Entries</span>"
    ).replace(
        "Total Heads: {new Set(entries.map(e => e.account_id)).size} &bull; Total Amount: {cp.fmt(entriesTotalUsd)}",
        "Total Heads: {new Set(hotelEntries.map(e => e.account_id)).size} &bull; Total Amount: {cp.fmt(hotelEntriesTotal)}"
    ).replace(
        "rows={entries}", "rows={hotelEntries}"
    ).replace(
        """<h3 className="font-semibold text-slate-700 mb-3 mt-6">AMC Contracts (auto-split across 12 months)</h3>""",
        """<h3 className="font-semibold text-slate-700 mb-3 mt-6">Hotel AMC Contracts (auto-split across 12 months)</h3>"""
    ).replace(
        "rows={amcContracts}", "rows={hotelAmc}"
    )
    
    # Now append the restaurant sections
    restaurant_section = """
      {(restEntries.length > 0 || restAmc.length > 0) && (
        <div className="mt-10 pt-8 border-t border-slate-200">
          <div className="flex justify-between items-end mb-3">
            <div>
              <h3 className="font-semibold text-slate-700 flex items-center gap-3">
                <span>Restaurant Daily Expense Entries</span>
              </h3>
            </div>
            <div className="text-sm text-slate-500 font-medium">
              Total Heads: {new Set(restEntries.map(e => e.account_id)).size} &bull; Total Amount: {cp.fmt(restEntriesTotal)}
            </div>
          </div>
          <DataTable
            columns={[
              { key: 'expense_date', label: 'Date' },
              { key: 'invoice_number', label: 'Invoice #', render: r => r.invoice_number || '—' },
              { key: 'account', label: 'Expense Head', render: r => r.account ? `${r.account.code} - ${r.account.name}` : '—' },
              { key: 'amount_usd', label: 'Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.amount_usd)}</span> },
              { key: 'paid_amount', label: 'Paid', render: r => <span className="font-medium text-emerald-600">{cp.fmt(r.paid_amount_usd || 0)}</span> },
              { key: 'pending_amount', label: 'Pending', render: r => <span className="font-medium text-red-500">{cp.fmt(Number(r.amount_usd) - Number(r.paid_amount_usd || 0))}</span> },
              { key: 'notes', label: 'Notes', render: r => r.notes || '—' },
              ...(can(['owner', 'admin', 'accountant']) ? [{
                key: 'actions', label: '', render: r => (
                  <div className="flex justify-end gap-2 text-slate-400">
                    <button onClick={() => { setEditingExp(r); setExpModalOpen(true) }} className="hover:text-navy-600"><Edit3 size={15} /></button>
                    <button onClick={() => handleDeleteEntry(r)} className="hover:text-red-600"><Trash2 size={15} /></button>
                  </div>
                )
              }] : []),
            ]}
            rows={restEntries}
            emptyMessage="No restaurant expense entries in this range."
          />

          <h3 className="font-semibold text-slate-700 mb-3 mt-6">Restaurant AMC Contracts (auto-split across 12 months)</h3>
          <DataTable
            columns={[
              { key: 'contract_name', label: 'Contract' },
              { key: 'annual_amount_usd', label: 'Annual Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.annual_amount_usd)}</span> },
              { key: 'annual_paid', label: 'Paid (Yr)', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(r.paid_amount_usd || 0)}</span> },
              { key: 'annual_pending', label: 'Pending (Yr)', render: r => <span className="text-red-500 font-medium">{cp.fmt(Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0))}</span> },
              { key: 'monthly_amount_usd', label: 'Monthly', render: r => <span className="font-medium text-slate-700">{cp.fmt(Number(r.annual_amount_usd)/12)}</span> },
              { key: 'monthly_paid', label: 'Paid (Mo)', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(Number(r.paid_amount_usd || 0)/12)}</span> },
              { key: 'monthly_pending', label: 'Pending (Mo)', render: r => <span className="text-red-500 font-medium">{cp.fmt((Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0))/12)}</span> },
              { key: 'start_date', label: 'Starts', render: r => { const d = new Date(r.start_date); return `${d.toLocaleString('default', {month:'long'})} ${d.getFullYear()}` } },
              ...(can(['owner', 'admin', 'accountant']) ? [{
                key: 'actions', label: '', render: r => (
                  <div className="flex justify-end gap-2 text-slate-400">
                    <button onClick={() => { setEditingAmc(r); setAmcModalOpen(true) }} className="hover:text-navy-600"><Edit3 size={15} /></button>
                    <button onClick={() => handleDeleteAmc(r)} className="hover:text-red-600"><Trash2 size={15} /></button>
                  </div>
                )
              }] : []),
            ]}
            rows={restAmc}
            emptyMessage="No restaurant AMC contracts created."
          />
        </div>
      )}
    </>
  )}"""

    # Do the same for purchase tab
    old_purchase_tab = """      {activeTab === 'purchase' && (
        <div className="mt-4">
          <h3 className="font-semibold text-slate-700 mb-3">Purchase Invoices</h3>
          <DataTable
            columns={[
              { key: 'invoice_date', label: 'Date' },
              { key: 'invoice_number', label: 'Invoice #' },
              { key: 'supplier', label: 'Supplier', render: r => r.contact ? r.contact.name : '—' },
              { key: 'amount_usd', label: 'Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.amount_usd)}</span> },
              { key: 'paid_amount', label: 'Paid', render: r => <span className="font-medium text-emerald-600">{cp.fmt(r.status === 'Paid' ? r.amount_usd : 0)}</span> },
              { key: 'pending_amount', label: 'Pending', render: r => <span className="font-medium text-red-500">{cp.fmt(r.status === 'Paid' ? 0 : r.amount_usd)}</span> },
              { key: 'status', label: 'Status', render: r => (
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${r.status === 'Paid' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                  {r.status}
                </span>
              )},
              ...(can(['owner', 'admin', 'accountant']) ? [{
                key: 'actions', label: '', render: r => (
                  <div className="flex justify-end gap-2 text-slate-400">
                    <button onClick={() => { setEditingPI(r); setPIModalOpen(true) }} className="hover:text-navy-600"><Edit3 size={15} /></button>
                    <button onClick={() => handleDeletePI(r)} className="hover:text-red-600"><Trash2 size={15} /></button>
                  </div>
                )
              }] : []),
            ]}
            rows={purchaseInvoices}
            emptyMessage="No purchase invoices in this range."
          />
        </div>
      )}"""
      
    new_purchase_tab = old_purchase_tab.replace(
        "rows={purchaseInvoices}", "rows={hotelPI}"
    ).replace(
        """<h3 className="font-semibold text-slate-700 mb-3">Purchase Invoices</h3>""",
        """<h3 className="font-semibold text-slate-700 mb-3">Hotel Purchase Invoices</h3>"""
    )
    
    rest_purchase_section = """
        {restPI.length > 0 && (
          <div className="mt-10 pt-8 border-t border-slate-200">
            <h3 className="font-semibold text-slate-700 mb-3">Restaurant Purchase Invoices</h3>
            <DataTable
              columns={[
                { key: 'invoice_date', label: 'Date' },
                { key: 'invoice_number', label: 'Invoice #' },
                { key: 'supplier', label: 'Supplier', render: r => r.contact ? r.contact.name : '—' },
                { key: 'amount_usd', label: 'Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.amount_usd)}</span> },
                { key: 'paid_amount', label: 'Paid', render: r => <span className="font-medium text-emerald-600">{cp.fmt(r.status === 'Paid' ? r.amount_usd : 0)}</span> },
                { key: 'pending_amount', label: 'Pending', render: r => <span className="font-medium text-red-500">{cp.fmt(r.status === 'Paid' ? 0 : r.amount_usd)}</span> },
                { key: 'status', label: 'Status', render: r => (
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${r.status === 'Paid' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                    {r.status}
                  </span>
                )},
                ...(can(['owner', 'admin', 'accountant']) ? [{
                  key: 'actions', label: '', render: r => (
                    <div className="flex justify-end gap-2 text-slate-400">
                      <button onClick={() => { setEditingPI(r); setPIModalOpen(true) }} className="hover:text-navy-600"><Edit3 size={15} /></button>
                      <button onClick={() => handleDeletePI(r)} className="hover:text-red-600"><Trash2 size={15} /></button>
                    </div>
                  )
                }] : []),
              ]}
              rows={restPI}
              emptyMessage="No restaurant purchase invoices in this range."
            />
          </div>
        )}"""
        
    new_purchase_tab = new_purchase_tab.replace("</div>\n      )}", rest_purchase_section + "\n        </div>\n      )}")

    if old_daily_header in content:
        content = content.replace(old_daily_header, new_daily_header + restaurant_section)
    else:
        print("Could not find old_daily_header")
        
    if old_purchase_tab in content:
        content = content.replace(old_purchase_tab, new_purchase_tab)
    else:
        print("Could not find old_purchase_tab")

    with open('src/pages/HotelExpenses.jsx', 'w') as f:
        f.write(content)
        print("Patched HotelExpenses.jsx Tables")

patch()
