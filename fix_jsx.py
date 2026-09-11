import re

for filename in ['src/components/PurchaseInvoiceFormModal.jsx', 'src/components/SalesInvoiceFormModal.jsx']:
    with open(filename, 'r') as f:
        content = f.read()

    # The string is: {uploading ? 'Uploading…' : {attachmentUrl ? ...}}
    # We want to change it to: {uploading ? 'Uploading…' : attachmentUrl ? (<><span className="mr-2">File attached ✓</span><a href={attachmentUrl} target="_blank" rel="noopener noreferrer" className="text-navy-600 hover:underline text-xs font-medium" onClick={e => e.stopPropagation()}>Preview</a></>) : 'Choose File'}
    content = content.replace(
        "{uploading ? 'Uploading…' : {attachmentUrl ?",
        "{uploading ? 'Uploading…' : attachmentUrl ?"
    )
    content = content.replace(
        ": 'Choose File'}}",
        ": 'Choose File'}"
    )
    
    with open(filename, 'w') as f:
        f.write(content)
