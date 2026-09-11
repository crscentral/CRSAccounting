import re

with open('src/lib/exportUtils.js', 'r') as f:
    content = f.read()

content = content.replace(
    "export async function exportInvoicePDF({ type, invoice, items, company, contact, itemDescription }) {",
    "export async function exportInvoicePDF({ type, invoice, items, company, contact, itemDescription, preview = false }) {"
)

content = content.replace(
    "  doc.save(`${invoice.invoice_number}.pdf`)\n}",
    """  if (preview) {
    const blob = doc.output('blob')
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  } else {
    doc.save(`${invoice.invoice_number}.pdf`)
  }
}"""
)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(content)
