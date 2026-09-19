import re

with open('src/pages/HotelExpenseBudget.jsx', 'r') as f:
    content = f.read()

content = content.replace("eq('type', 'Expense')", "eq('type', 'Expenses')")
content = content.replace("eq('accounts.type', 'Expense')", "eq('accounts.type', 'Expenses')")

with open('src/pages/HotelExpenseBudget.jsx', 'w') as f:
    f.write(content)
