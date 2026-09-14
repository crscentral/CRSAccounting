import re
with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# 1. Update Outstanding Invoices
outstanding = """        <DataTable
          columns={[
            { key: 'invoice_number', label: 'Invoice #' },
            { key: 'customer', label: 'Customer', render: r => r.contact?.name || '—' },
            { key: 'due_date', label: 'Due Date' },
            { key: 'balance_due', label: 'Balance Due', render: r => `${Number(r.balance_due).toLocaleString()} ${r.currency}` },
            { key: 'balance_usd', label: `Balance (${cp.displayCurrency})`, render: r => cp.fmt((Number(r.balance_due) / (Number(r.amount) || 1)) * Number(r.amount_usd)) },
            { key: 'status', label: 'Status' },
          ]}
          rows={draftInvoices}
          emptyMessage="No outstanding invoices — nice work."
        />"""

code = re.sub(
    r"        <DataTable\n          columns=\{\[\n            \{ key: 'invoice_number', label: 'Invoice #' \},\n            \{ key: 'customer', label: 'Customer', render: r => r\.contact\?\.name \|\| '—' \},\n            \{ key: 'due_date', label: 'Due Date' \},\n            \{ key: 'balance_due', label: 'Balance Due', render: r => cp\.fmt\(\(Number\(r\.balance_due\) / \(Number\(r\.amount\) \|\| 1\)\) \* Number\(r\.amount_usd\)\) \},\n            \{ key: 'status', label: 'Status' \},\n          \]\}\n          rows=\{draftInvoices\}\n          emptyMessage=\"No outstanding invoices — nice work\.\"\n        />",
    outstanding,
    code,
    flags=re.DOTALL
)

# 2. Update Draft Expenses
draft = """        <DataTable
          columns={[
            { key: 'invoice_number', label: 'Invoice #' },
            { key: 'supplier', label: 'Supplier', render: r => r.contact?.name || r.supplier_name_freeform || '—' },
            { key: 'invoice_date', label: 'Date' },
            { key: 'amount', label: 'Amount', render: r => `${Number(r.amount).toLocaleString()} ${r.currency}` },
            { key: 'amount_usd', label: `Amount (${cp.displayCurrency})`, render: r => cp.fmt(r.amount_usd) },
          ]}
          rows={draftExpenses}
          emptyMessage="No draft expenses."
        />"""

code = re.sub(
    r"        <DataTable\n          columns=\{\[\n            \{ key: 'invoice_number', label: 'Invoice #' \},\n            \{ key: 'supplier', label: 'Supplier', render: r => r\.contact\?\.name \|\| r\.supplier_name_freeform \|\| '—' \},\n            \{ key: 'invoice_date', label: 'Date' \},\n            \{ key: 'amount_usd', label: 'Amount', render: r => cp\.fmt\(r\.amount_usd\) \},\n          \]\}\n          rows=\{draftExpenses\}\n          emptyMessage=\"No draft expenses\.\"\n        />",
    draft,
    code,
    flags=re.DOTALL
)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
