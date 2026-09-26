import re

with open('src/pages/TallyMode/TallyVouchers.jsx', 'r') as f:
    content = f.read()

# Replace useAuth
content = content.replace(
    "const { activeCompany } = useAuth()",
    "const { activeCompany, activeProduct } = useAuth()"
)

# Replace supabase query
old_query = "supabase.from('accounts').select('*').eq('company_id', activeCompany.id).then(({ data }) => {"
new_query = "supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).then(({ data }) => {"
content = content.replace(old_query, new_query)

# Replace useEffect dependency
content = content.replace(
    "}, [activeCompany])",
    "}, [activeCompany, activeProduct])"
)

with open('src/pages/TallyMode/TallyVouchers.jsx', 'w') as f:
    f.write(content)
