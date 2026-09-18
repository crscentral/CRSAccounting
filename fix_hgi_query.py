import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Remove invoice_number from the select and the label mapping
old_query = "select('invoice_number, invoice_date, invoice_amount_usd, currency, guest_name')"
new_query = "select('id, invoice_date, invoice_amount_usd, currency, guest_name')"
code = code.replace(old_query, new_query)

old_map = "label: r.guest_name || r.invoice_number,"
new_map = "label: r.guest_name || 'Guest Invoice',"
code = code.replace(old_map, new_map)

# Also fix the fallback string logic to use String() to be perfectly safe against null dates
old_sort = "sort((a, b) => b.date.localeCompare(a.date))"
new_sort = "sort((a, b) => String(b.date || '').localeCompare(String(a.date || '')))"
code = code.replace(old_sort, new_sort)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
