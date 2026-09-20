import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "const { data } = await supabase.from('accounts').select('code, name, subtype').eq('company_id', activeCompany.id).eq('type', 'Revenue').neq('code', '4010')",
    "const { data } = await supabase.from('accounts').select('code, name, subtype').eq('company_id', activeCompany.id).eq('product', 'hotel').eq('type', 'Revenue').neq('code', '4010')"
)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
