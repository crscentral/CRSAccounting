import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# Fix 1: fetchAncillaryAccounts
content = content.replace(
    ".eq('product', 'hotel')",
    ".eq('product', activeProduct)"
)

# Fix 2: loadAncillary's ledgerRows
content = content.replace(
    "supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', 'hotel').gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue').neq('accounts.code', '4010')",
    "supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue').neq('accounts.code', '4010')"
)

# Fix 3: hotel_expense_budget upsert needs product
content = content.replace(
    """const { error } = await supabase.from('hotel_expense_budget').upsert({
      company_id: activeCompany.id,
      budget_year: startYear,
      budget_month: ancillaryMonth,""",
    """const { error } = await supabase.from('hotel_expense_budget').upsert({
      company_id: activeCompany.id,
      product: activeProduct,
      budget_year: startYear,
      budget_month: ancillaryMonth,"""
)

# Fix 4: hotel_expense_budget fetch needs product
content = content.replace(
    "supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('budget_year', startYear)",
    "supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', startYear)"
)

# Fix 5: Actuals injection for Restaurant Table Revenue
# ONLY inject if activeProduct === 'hotel' because if we are in 'restaurant', the ledger_entries ALREADY have the table revenue?
# Wait! In the restaurant module, Table Revenue DOES NOT post to ledger_entries unless they create Sales Invoices.
# Wait! In Restaurant module, they post "Table Revenue". Does it post to `ledger_entries`?
# NO! It only posts to `restaurant_daily_revenue`.
# So for the Restaurant Revenue Budget to show actuals, it MUST pull from `restaurant_daily_revenue`!
# Ah, I see. In `HotelBudget.jsx` earlier I added:
# `activeProduct === 'hotel' ? supabase.from('restaurant_daily_revenue')` - Wait, in HotelBudget.jsx, the previous patch was:
# `supabase.from('restaurant_daily_revenue').select('revenue_date, food_amount_usd, beverage_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', ...)`
# Let's check how it is exactly written.
