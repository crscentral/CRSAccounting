import re

with open('src/lib/exportUtils.js', 'r') as f:
    code = f.read()

# Replace the non-wrapping doc.text names with wrapping logic
old_code = """  doc.text(fromName, col1, y)
  doc.text(toName, col2, y)
  doc.text(invoice.invoice_number || '', col3, y)
  y += 4.5"""

new_code = """  const fromNameWrapped = doc.splitTextToSize(fromName, 60)
  const toNameWrapped = doc.splitTextToSize(toName, 62)
  const docNameWrapped = doc.splitTextToSize(invoice.invoice_number || '', 55)

  doc.text(fromNameWrapped, col1, y)
  doc.text(toNameWrapped, col2, y)
  doc.text(docNameWrapped, col3, y)
  
  y += Math.max(fromNameWrapped.length, toNameWrapped.length, docNameWrapped.length) * 4.5"""

code = code.replace(old_code, new_code)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(code)
