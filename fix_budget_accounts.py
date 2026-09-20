import re

with open('src/pages/HotelExpenseBudget.jsx', 'r') as f:
    content = f.read()

# Fix 1: Fetch Accounts
content = content.replace(
    "const { data } = await supabase.from('accounts').select('code, name').eq('company_id', activeCompany.id).eq('type', 'Expenses').order('code')",
    "const { data } = await supabase.from('accounts').select('code, name').eq('company_id', activeCompany.id).eq('product', 'hotel').eq('type', 'Expenses').order('code')"
)

with open('src/pages/HotelExpenseBudget.jsx', 'w') as f:
    f.write(content)
