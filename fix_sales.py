with open('src/pages/SalesInvoices.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "{ key: 'invoice_date', label: 'Date' }",
    "{ key: 'invoice_date', label: 'Date', render: r => <span className=\"whitespace-nowrap\">{formatDate(r.invoice_date)}</span> }"
)

content = content.replace(
    "{ key: 'receipt_date', label: 'Date' }",
    "{ key: 'receipt_date', label: 'Date', render: r => <span className=\"whitespace-nowrap\">{formatDate(r.receipt_date)}</span> }"
)

with open('src/pages/SalesInvoices.jsx', 'w') as f:
    f.write(content)
