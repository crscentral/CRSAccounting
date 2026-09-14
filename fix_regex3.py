with open('src/lib/exportUtils.js', 'r') as f:
    code = f.read()

import re
code = re.sub(
    r"function sanitizeText\(str\) \{.*?\}",
    lambda m: "function sanitizeText(str) {\n  if (typeof str !== 'string') return str;\n  return str.replace(/₹/g, 'INR ').replace(/฿/g, 'THB ').replace(/€/g, 'EUR ').replace(/£/g, 'GBP ').replace(/[^\\x00-\\x7F]/g, '');\n}",
    code,
    flags=re.DOTALL
)

with open('src/lib/exportUtils.js', 'w') as f:
    f.write(code)
