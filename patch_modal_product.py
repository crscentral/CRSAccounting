import re

with open('src/components/PurchaseInvoiceFormModal.jsx', 'r') as f:
    content = f.read()

# Update the insert statement in PurchaseInvoiceFormModal.jsx
old_insert = ".insert({ company_id: companyId, type: 'supplier', name: supplierName.trim(), email: supplierEmail || null, phone: supplierPhone || null, tax_id: supplierGstin || null, address: supplierAddress || null })"
new_insert = ".insert({ company_id: companyId, product, type: 'supplier', name: supplierName.trim(), email: supplierEmail || null, phone: supplierPhone || null, tax_id: supplierGstin || null, address: supplierAddress || null })"
content = content.replace(old_insert, new_insert)

with open('src/components/PurchaseInvoiceFormModal.jsx', 'w') as f:
    f.write(content)
