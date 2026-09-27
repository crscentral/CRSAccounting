import re

with open('src/pages/RestaurantExpenses.jsx', 'r') as f:
    content = f.read()

# The file ends roughly here:
#       />
#     </div>
#   )
# }
old_end = """        rows={amcContracts}
        emptyMessage="No AMC contracts yet."
      />"""

new_end = old_end + """
        </>
      )}

      {activeTab === 'purchase' && (
        <>
          <div className="flex justify-between items-end mb-3 mt-8">
            <h3 className="font-semibold text-slate-700">Purchase Invoices</h3>
          </div>
          <DataTable
            columns={[
              { key: 'date', label: 'Date', render: r => r.invoice_date },
              { key: 'invoice_no', label: 'Invoice #', render: r => r.invoice_number },
              { key: 'supplier', label: 'Supplier', render: r => r.contact?.name || r.supplier_name_freeform || 'Unknown' },
              { key: 'amount', label: 'Amount', render: r => cp.fmt(r.amount_usd) },
              { key: 'status', label: 'Status', render: r => <span className={`px-2 py-0.5 rounded text-xs font-medium ${r.status === 'Draft' ? 'bg-slate-100 text-slate-600' : r.status === 'Approved' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{r.status}</span> },
              ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => <div className="flex justify-end gap-2">
                <button onClick={() => { setEditingRow(r); setPurchaseModalOpen(true); }} className="text-slate-400 hover:text-navy-600 p-1"><Pencil size={15} /></button>
                <button onClick={() => handleDeletePI(r)} className="text-slate-400 hover:text-red-500 p-1"><Trash2 size={15} /></button>
              </div> }] : []),
            ]}
            rows={purchaseInvoices}
            emptyMessage="No purchase invoices yet."
          />
        </>
      )}"""

content = content.replace(old_end, new_end)

with open('src/pages/RestaurantExpenses.jsx', 'w') as f:
    f.write(content)
