import re

with open('src/pages/SalesInvoices.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    ".select('*, invoice:sales_invoices(invoice_number)')",
    ".select('*, invoice:sales_invoices(invoice_number), contact:contacts(name)')"
)

with open('src/pages/SalesInvoices.jsx', 'w') as f:
    f.write(content)
