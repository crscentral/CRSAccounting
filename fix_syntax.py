import re
with open('src/pages/CapitalTransactions.jsx', 'r') as f:
    code = f.read()

code = re.sub(r" = await supabase.from\('owner_dividends'\).delete\(\).eq\('id', row.id\)\n.*?loadAll\(\)\n  \}", "", code, flags=re.DOTALL)

with open('src/pages/CapitalTransactions.jsx', 'w') as f:
    f.write(code)
