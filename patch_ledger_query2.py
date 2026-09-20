import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

old_promise = """      const [{ data: budgetRows }, { data: ledgerRows }, { data: restRev }] = await Promise.all([
        supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('budget_year', startYear),
        supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', 'hotel').gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue').neq('accounts.code', '4010'),
        supabase.from('restaurant_daily_revenue').select('revenue_date, meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', `${startYear}-01-01`).lte('revenue_date', `${startYear}-12-31`)
      ])"""

new_promise = """      let ledgerQuery = supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue')
      if (activeProduct === 'hotel') ledgerQuery = ledgerQuery.neq('accounts.code', '4010')
      
      const [{ data: budgetRows }, { data: ledgerRows }, { data: restRev }] = await Promise.all([
        supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', startYear),
        ledgerQuery,
        supabase.from('restaurant_daily_revenue').select('revenue_date, meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd').eq('company_id', activeCompany.id).gte('revenue_date', `${startYear}-01-01`).lte('revenue_date', `${startYear}-12-31`)
      ])"""

content = content.replace(old_promise, new_promise)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
