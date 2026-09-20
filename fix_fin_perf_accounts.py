import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "supabase.from('accounts').select('code, type').eq('company_id', activeCompany.id)",
    "supabase.from('accounts').select('code, type').eq('company_id', activeCompany.id).eq('product', 'hotel')"
)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
