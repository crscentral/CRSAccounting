import re

with open('src/pages/Reports.jsx', 'r') as f:
    content = f.read()

def inject_product_filter(match):
    # Match strings like: supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id)
    # We want to append: .eq('product', activeProduct)
    return match.group(0) + ".eq('product', activeProduct)"

# Replace all occurrences of supabase.from(...).select('*').eq('company_id', activeCompany.id)
# EXCEPT for those that already have .eq('product', activeProduct)
# Wait, let's just do it cleanly with standard python replace

tables_to_patch = [
    'hotel_room_stats',
    'hotel_revenue_entries',
    'hotel_expense_entries',
    'hotel_amc_contracts',
    'hotel_guest_invoices',
    'purchase_invoices',
    'restaurant_daily_revenue' # Just in case it's good practice
]

for table in tables_to_patch:
    target = f"supabase.from('{table}').select('*').eq('company_id', activeCompany.id)"
    replacement = f"supabase.from('{table}').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)"
    content = content.replace(target, replacement)

# What about Purchase Invoices? It is also loaded in Reports.jsx?
# Let's check if purchase_invoices is there. Wait, I'll just write it back.

with open('src/pages/Reports.jsx', 'w') as f:
    f.write(content)

