import re

with open('src/pages/SalesInvoices.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "import SalesInvoiceFormModal from '../components/SalesInvoiceFormModal'",
    "import SalesInvoiceFormModal from '../components/SalesInvoiceFormModal'\nimport PaymentReceiptFormModal from '../components/PaymentReceiptFormModal'"
)

# Add state
content = content.replace(
    "const [editingInvoice, setEditingInvoice] = useState(null)",
    "const [editingInvoice, setEditingInvoice] = useState(null)\n  const [receiptModalOpen, setReceiptModalOpen] = useState(false)\n  const [editingReceipt, setEditingReceipt] = useState(null)"
)

# Replace the New Invoice button logic
old_button = """            {can(['owner', 'admin', 'accountant']) && (
              <button onClick={() => { setEditingInvoice(null); setModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
                <Plus size={16} /> New Invoice
              </button>
            )}"""

new_button = """            {can(['owner', 'admin', 'accountant']) && (
              tab === 'invoices' ? (
                <button onClick={() => { setEditingInvoice(null); setModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
                  <Plus size={16} /> New Invoice
                </button>
              ) : (
                <button onClick={() => { setEditingReceipt(null); setReceiptModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
                  <Plus size={16} /> New Receipt
                </button>
              )
            )}"""

content = content.replace(old_button, new_button)

# Add receipt actions to receipt table
old_receipt_actions = """          columns={[
            { key: 'invoice', label: 'Invoice #', render: r => r.invoice?.invoice_number || '—' },
            { key: 'receipt_date', label: 'Date', render: r => <span className="whitespace-nowrap">{formatDate(r.receipt_date)}</span> },
            { key: 'amount', label: 'Amount', render: r => `${r.amount.toLocaleString()} ${r.currency}` },
            { key: 'amount_usd', label: 'Amount (USD)', render: r => cp.fmt(r.amount_usd) },
          ]}"""

new_receipt_actions = """          columns={[
            { key: 'receipt_number', label: 'Receipt #', render: r => r.receipt_number || '—' },
            { key: 'invoice', label: 'Invoice #', render: r => r.invoice?.invoice_number || '—' },
            { key: 'receipt_date', label: 'Date', render: r => <span className="whitespace-nowrap">{formatDate(r.receipt_date)}</span> },
            { key: 'customer', label: 'Customer', render: r => r.customer_name_freeform || r.contact?.name || '—' },
            { key: 'amount', label: 'Amount', render: r => `${r.amount.toLocaleString()} ${r.currency}` },
            { key: 'amount_usd', label: 'Amount (USD)', render: r => cp.fmt(r.amount_usd) },
            {
              key: 'actions', label: '', render: r => (
                <div className="flex gap-2 justify-end md:justify-start">
                  {can(['owner', 'admin', 'accountant']) && (
                    <>
                      <button onClick={() => { setEditingReceipt(r); setReceiptModalOpen(true) }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
                      <button onClick={() => handleReceiptDelete(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
                    </>
                  )}
                </div>
              )
            }
          ]}"""

content = content.replace(old_receipt_actions, new_receipt_actions)

# Add handleReceiptDelete function before the return statement of SalesInvoices
delete_func = """
  async function handleReceiptDelete(r) {
    if (!confirm('Delete this receipt?')) return
    const { error } = await supabase.from('payment_receipts').delete().eq('id', r.id)
    if (error) alert(error.message)
    else loadData()
  }
"""
content = content.replace(
  "  if (!activeCompany) return null",
  delete_func + "\n  if (!activeCompany) return null"
)

# Add PaymentReceiptFormModal at the end of SalesInvoices return
content = content.replace(
    "</SalesInvoiceFormModal>",
    "</SalesInvoiceFormModal>\n\n      <PaymentReceiptFormModal\n        open={receiptModalOpen}\n        onClose={() => setReceiptModalOpen(false)}\n        companyId={activeCompany.id}\n        product={activeProduct}\n        initialData={editingReceipt}\n        onSuccess={loadData}\n        invoices={invoices}\n      />"
)

with open('src/pages/SalesInvoices.jsx', 'w') as f:
    f.write(content)
