import re

for filename in ['src/pages/RestaurantExpenses.jsx', 'src/pages/HotelExpenses.jsx']:
    with open(filename, 'r') as f:
        content = f.read()

    # 1. Fix contacts query
    content = content.replace(
        "supabase.from('contacts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('name')",
        "supabase.from('contacts').select('*').eq('company_id', activeCompany.id).order('name')"
    )

    # 2. Fix accounts query to include type
    content = content.replace(
        "supabase.from('accounts').select('id, code, name, subtype').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Expenses').order('code')",
        "supabase.from('accounts').select('id, code, name, subtype, type').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Expenses').order('code')"
    )

    with open(filename, 'w') as f:
        f.write(content)
