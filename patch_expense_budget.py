import re

with open('src/pages/HotelExpenseBudget.jsx', 'r') as f:
    content = f.read()

# 1. Accounts fetch
content = content.replace(
    ".eq('product', 'hotel')",
    ".eq('product', activeProduct)"
)

# 2. Budget rows fetch
content = content.replace(
    "supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('budget_year', selectedYear)",
    "supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('budget_year', selectedYear)"
)

# 3. Upsert
content = content.replace(
    "company_id: activeCompany.id,\n      budget_year: selectedYear,",
    "company_id: activeCompany.id,\n      product: activeProduct,\n      budget_year: selectedYear,"
)

# 4. Title
content = content.replace(
    'title="Expenses Budget"',
    'title={activeProduct === "restaurant" ? "F&B Expense Budget" : "Expenses Budget"}'
)

with open('src/pages/HotelExpenseBudget.jsx', 'w') as f:
    f.write(content)
