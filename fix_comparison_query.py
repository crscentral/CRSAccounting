with open('src/pages/Comparison.jsx', 'r') as f:
    content = f.read()

tables_to_patch = [
    'hotel_room_stats',
    'hotel_revenue_entries',
    'hotel_expense_entries',
    'hotel_amc_contracts',
    'restaurant_daily_revenue'
]

for table in tables_to_patch:
    target = f"supabase.from('{table}').select('*').eq('company_id', activeCompany.id)"
    replacement = f"supabase.from('{table}').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)"
    content = content.replace(target, replacement)

with open('src/pages/Comparison.jsx', 'w') as f:
    f.write(content)
