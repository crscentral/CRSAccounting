with open('src/pages/SalesInvoices.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "{ key: 'due_date', label: 'Due' }",
    "{ key: 'due_date', label: 'Due', render: r => <span className=\"whitespace-nowrap\">{formatDate(r.due_date)}</span> }"
)

with open('src/pages/SalesInvoices.jsx', 'w') as f:
    f.write(content)
