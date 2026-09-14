with open('src/lib/exportUtils.js', 'r') as f:
    code = f.read()

import re
code = re.sub(
    r"  if \(invoice\.payment_terms \|\| invoice\.notes\) \{.*?finalY = renderRichText\(doc, combined, 14, finalY, pageWidth - 28\)\n  \}",
    "  if (invoice.payment_terms || invoice.notes) {\n    const combined = [invoice.payment_terms, invoice.notes].filter(Boolean).join('\\n\\n')\n    finalY = renderRichText(doc, combined, 14, finalY, pageWidth - 28)\n  }",
    code,
    flags=re.DOTALL
)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(code)
