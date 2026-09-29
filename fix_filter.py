import re

def patch(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    old = "'hotel_expense_entry', 'hotel_amc', 'hotel_guest_invoice'"
    new = "'hotel_expense_entry', 'hotel_amc_contract', 'hotel_guest_invoice'"
    
    if old in content:
        content = content.replace(old, new)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Patched {filepath}")

patch('src/pages/Reports.jsx')
patch('src/pages/Comparison.jsx')
patch('src/pages/Ledger.jsx')
