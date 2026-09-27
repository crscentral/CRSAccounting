import re

for filename in ['src/pages/RestaurantExpenses.jsx', 'src/pages/HotelExpenses.jsx']:
    with open(filename, 'r') as f:
        content = f.read()

    # 1. Add state variable
    content = content.replace(
        "const [notes, setNotes] = useState(editingRow?.notes || '')",
        "const [notes, setNotes] = useState(editingRow?.notes || '')\n  const [invoiceNumber, setInvoiceNumber] = useState(editingRow?.invoice_number || '')"
    )

    # 2. Add to payload
    content = content.replace(
        "const payload = { company_id: companyId, product, expense_date: date, account_id: accountId, amount, currency, fx_rate_locked: finalFxRate, amount_usd: amountUsd, notes }",
        "const payload = { company_id: companyId, product, expense_date: date, account_id: accountId, amount, currency, fx_rate_locked: finalFxRate, amount_usd: amountUsd, notes, invoice_number: invoiceNumber || null }"
    )

    # 3. Add to UI
    new_field = """        <Field label="Invoice Number">
          <input value={invoiceNumber} onChange={e => setInvoiceNumber(e.target.value)} placeholder="Optional" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </Field>
        <Field label="Notes">"""

    content = content.replace('<Field label="Notes">', new_field)
    
    # 4. Add Invoice Number column to Data Grid
    old_grid = """          <DataTable
            columns={[
              { key: 'date', label: 'Date', render: r => r.expense_date },
              { key: 'account', label: 'Expense Head', render: r => r.account?.name || '-' },
              { key: 'amount', label: 'Amount', render: r => <span className="font-medium">{cp.fmt(r.amount_usd)}</span> },
              { key: 'notes', label: 'Notes', render: r => r.notes || '-' },
              ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => <div className="flex justify-end gap-2">"""
              
    new_grid = """          <DataTable
            columns={[
              { key: 'date', label: 'Date', render: r => r.expense_date },
              { key: 'invoice_number', label: 'Invoice #', render: r => r.invoice_number || '-' },
              { key: 'account', label: 'Expense Head', render: r => r.account?.name || '-' },
              { key: 'amount', label: 'Amount', render: r => <span className="font-medium">{cp.fmt(r.amount_usd)}</span> },
              { key: 'notes', label: 'Notes', render: r => <span className="truncate max-w-[200px] inline-block" title={r.notes}>{r.notes || '-'}</span> },
              ...(can(['owner', 'admin', 'accountant']) ? [{ key: 'actions', label: '', render: r => <div className="flex justify-end gap-2">"""

    content = content.replace(old_grid, new_grid)

    with open(filename, 'w') as f:
        f.write(content)
