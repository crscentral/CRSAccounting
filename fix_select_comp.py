import re
with open('src/pages/Comparison.jsx', 'r') as f:
    content = f.read()

old_sel = "select('account_id, debit_usd, credit_usd, entry_date')"
new_sel = "select('account_id, debit_usd, credit_usd, entry_date, source_type')"
if old_sel in content:
    content = content.replace(old_sel, new_sel)
    with open('src/pages/Comparison.jsx', 'w') as f:
        f.write(content)
    print("Patched Comparison.jsx select")
