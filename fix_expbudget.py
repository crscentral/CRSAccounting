import re

with open('src/pages/HotelExpenseBudget.jsx', 'r') as f:
    content = f.read()

old_upsert = """    await supabase.from('hotel_expense_budget').upsert({
      company_id: activeCompany.id,
      budget_year: startYear,
      budget_month: month,
      account_code: accountCode,
      amount: row.amount,
      currency: currency,
      amount_usd: amountUsd,
      updated_at: new Date().toISOString()
    }, { onConflict: 'company_id, budget_year, budget_month, account_code' })"""

new_upsert = """    await supabase.from('hotel_expense_budget').upsert({
      company_id: activeCompany.id,
      product: activeProduct,
      budget_year: startYear,
      budget_month: month,
      account_code: accountCode,
      amount: row.amount,
      currency: currency,
      amount_usd: amountUsd,
      updated_at: new Date().toISOString()
    }, { onConflict: 'company_id, product, budget_year, budget_month, account_code' })"""

content = content.replace(old_upsert, new_upsert)

with open('src/pages/HotelExpenseBudget.jsx', 'w') as f:
    f.write(content)
