import re

with open('src/pages/Companies.jsx', 'r') as f:
    code = f.read()

# The first one is at line 233. The second at 278, the third at 316.
# Actually, I can just use a regex to find all the checkbox blocks and replace the 2nd and 3rd with just `</Field>\n                </>`

block_regex = r'\n\s*<div className="pt-2 border-t border-slate-100 mt-4">\n\s*<p className="text-sm font-medium text-slate-700 mb-2">Accounting Modules</p>.*?</label>\n\s*\)\)}\n\s*</div>\n\s*</div>\n\s*</>\n'

matches = list(re.finditer(block_regex, code, re.DOTALL))
print(f"Found {len(matches)} matches")

if len(matches) > 1:
    # Keep the first one, replace others
    for match in reversed(matches[1:]):
        start = match.start()
        end = match.end()
        code = code[:start] + "\n                </>\n" + code[end:]

with open('src/pages/Companies.jsx', 'w') as f:
    f.write(code)
