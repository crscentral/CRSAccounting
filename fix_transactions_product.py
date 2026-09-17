import re

with open('src/pages/Transactions.jsx', 'r') as f:
    code = f.read()

old_s = ".eq('company_id', activeCompany.id).gte('invoice_date', range.from)"
new_s = ".eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from)"
code = code.replace(old_s, new_s)

old_p = ".eq('company_id', activeCompany.id).gte('expense_date', range.from)"
new_p = ".eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', range.from)"
code = code.replace(old_p, new_p)

with open('src/pages/Transactions.jsx', 'w') as f:
    f.write(code)
