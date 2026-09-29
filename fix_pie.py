import re

def patch(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    content = content.replace("Expense Breakdown (CPOR:", "Expense Breakdown (Cost Per Occupied Room:")
    content = content.replace("Expense Breakdown (PAR:", "Expense Breakdown (Cost Per Available Room:")
    
    with open(filepath, 'w') as f:
        f.write(content)
    print("Patched", filepath)

patch('src/pages/HotelExpenses.jsx')
