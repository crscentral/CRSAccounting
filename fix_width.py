import re

with open('src/lib/exportUtils.js', 'r') as f:
    code = f.read()

code = code.replace(
    "const docNameWrapped = doc.splitTextToSize(invoice.invoice_number || '', 55)",
    "const docNameWrapped = doc.splitTextToSize(invoice.invoice_number || '', 46)"
)

# I should also fix the renderColumn call for docLines which uses 55
code = code.replace(
    "const endY3 = renderColumn(docLines, col3, 55, colStartY)",
    "const endY3 = renderColumn(docLines, col3, 46, colStartY)"
)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(code)
