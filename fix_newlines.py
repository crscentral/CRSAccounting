with open('src/lib/exportUtils.js', 'r') as f:
    code = f.read()

import re
code = re.sub(
    r"    const combined = \[invoice\.payment_terms, invoice\.notes\]\.filter\(Boolean\)\.join\('.*?'\)",
    "    const combined = [invoice.payment_terms, invoice.notes].filter(Boolean).join('\\n\\n')",
    code,
    flags=re.DOTALL
)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(code)
