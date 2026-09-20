import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# Fix the ledger_entries fetch to use activeProduct
old_ledger = "supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', 'hotel').gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue').neq('accounts.code', '4010')"
new_ledger = "supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue').neq('accounts.code', '4010')"
content = content.replace(old_ledger, new_ledger)

# Fix the injection of restRev
# If activeProduct === 'hotel', we map it to 4019 and 4011 (because those are the Hotel F&B Revenue heads).
# But if activeProduct === 'restaurant', we map it to 4010 (Food Sales) and 4011 (Beverage Sales). Wait! 
# 4010 is excluded from ancillary (because of neq 4010). 4010 is handled by `hotel_room_stats`!
# Wait! In `loadAll()`, `hotel_room_stats` handles `4010`. But for Restaurant, there are no `hotel_room_stats` rows!
# In my earlier thought I realized I need to patch `loadAll` to fetch `restaurant_daily_revenue` and sum it into `actualMap` for `4010`.
