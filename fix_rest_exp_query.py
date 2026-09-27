import os

with open('src/pages/RestaurantExpenses.jsx', 'r') as f:
    content = f.read()

bad_line = "supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).select('rooms_occupied').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to)"
good_line = "supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)"

content = content.replace(bad_line, good_line)

with open('src/pages/RestaurantExpenses.jsx', 'w') as f:
    f.write(content)

