import re

for filename in ['src/components/PurchaseInvoiceFormModal.jsx', 'src/components/SalesInvoiceFormModal.jsx']:
    with open(filename, 'r') as f:
        content = f.read()

    # TDS calculation fix
    content = content.replace(
        "const tdsAmount = total * (Number(tdsPercent || 0) / 100)",
        "const tdsAmount = subtotal * (Number(tdsPercent || 0) / 100)"
    )

    # Preview link for attachment (only for Purchase, wait... let's check both if they have attachmentUrl)
    # The label is "File attached ✓"
    preview_link_html = "{attachmentUrl ? (<><span className=\"mr-2\">File attached ✓</span><a href={attachmentUrl} target=\"_blank\" rel=\"noopener noreferrer\" className=\"text-navy-600 hover:underline text-xs font-medium\" onClick={e => e.stopPropagation()}>Preview</a></>) : 'Choose File'}"
    content = content.replace(
        "{uploading ? 'Uploading…' : attachmentUrl ? 'File attached ✓' : 'Choose File'}",
        "{uploading ? 'Uploading…' : " + preview_link_html + "}"
    )
    
    with open(filename, 'w') as f:
        f.write(content)
