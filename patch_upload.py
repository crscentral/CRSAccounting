import re

with open('src/components/PurchaseInvoiceFormModal.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    'label="Upload Supplier Invoice PDF"',
    'label="Upload Supplier Invoice (PDF, JPG, PNG)"'
)
content = content.replace(
    'accept="application/pdf"',
    'accept="application/pdf,image/jpeg,image/png,image/jpg"'
)

with open('src/components/PurchaseInvoiceFormModal.jsx', 'w') as f:
    f.write(content)
