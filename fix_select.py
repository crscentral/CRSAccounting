import re

def patch_select(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # We need to replace .select('account_id, debit_usd, credit_usd, entry_date, accounts!inner(type)')
    # with .select('account_id, debit_usd, credit_usd, entry_date, source_type, accounts!inner(type)')
    
    old_sel = "select('account_id, debit_usd, credit_usd, entry_date, accounts!inner(type)')"
    new_sel = "select('account_id, debit_usd, credit_usd, entry_date, source_type, accounts!inner(type)')"
    
    if old_sel in content:
        content = content.replace(old_sel, new_sel)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Patched {filepath} select(inner)")

    # In Ledger.jsx, it might just be select('*') or something else.
    # Let's check what it uses.
    
patch_select('src/pages/Reports.jsx')
patch_select('src/pages/Comparison.jsx')
