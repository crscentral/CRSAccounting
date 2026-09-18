import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# The block is:
#       <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mt-6">
#         <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
#           <AlertCircle size={18} className="text-slate-400" /> Draft Expenses ({draftExpenses.length})
#         </h2>
#         <DataTable
#           columns={[...]}
#           data={draftExpenses}
#           emptyMessage="No draft expenses."
#         />
#       </div>

old_block = r"""      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mt-6">
        <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
          <AlertCircle size=\{18\} className="text-slate-400" /> Draft Expenses \(\{draftExpenses\.length\}\)
        </h2>
        <DataTable
          columns=\{\[
            \{ key: 'invoice_number', label: 'Invoice #' \},
            \{ key: 'supplier', label: 'Supplier', render: r => r\.contact\?\.name \|\| r\.supplier_name_freeform \|\| '—' \},
            \{ key: 'invoice_date', label: 'Date' \},
            \{ key: 'amount_usd', label: 'Amount \(USD\)', render: r => cp\.fmt\(r\.amount_usd\) \},
            \{ key: 'status', label: 'Status', render: r => <span className="inline-flex items-center px-2 py-0\.5 rounded text-xs font-medium bg-slate-100 text-slate-700">Draft</span> \}
          \]\}
          data=\{draftExpenses\}
          emptyMessage="No draft expenses\."
        />
      </div>"""

new_block = """      {activeProduct !== 'hotel' && (
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mt-6">
        <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
          <AlertCircle size={18} className="text-slate-400" /> Draft Expenses ({draftExpenses.length})
        </h2>
        <DataTable
          columns={[
            { key: 'invoice_number', label: 'Invoice #' },
            { key: 'supplier', label: 'Supplier', render: r => r.contact?.name || r.supplier_name_freeform || '—' },
            { key: 'invoice_date', label: 'Date' },
            { key: 'amount_usd', label: 'Amount (USD)', render: r => cp.fmt(r.amount_usd) },
            { key: 'status', label: 'Status', render: r => <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700">Draft</span> }
          ]}
          data={draftExpenses}
          emptyMessage="No draft expenses."
        />
      </div>
      )}"""

code = re.sub(old_block, new_block, code)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
