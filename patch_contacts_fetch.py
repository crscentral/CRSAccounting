import re

for filename in ['src/pages/RestaurantExpenses.jsx', 'src/pages/HotelExpenses.jsx', 'src/pages/Contacts.jsx']:
    with open(filename, 'r') as f:
        content = f.read()

    # Re-add product filter to contacts
    content = content.replace(
        "supabase.from('contacts').select('*').eq('company_id', activeCompany.id).order('name')",
        "supabase.from('contacts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('name')"
    )

    with open(filename, 'w') as f:
        f.write(content)
