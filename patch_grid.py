import re

for filename in ['src/pages/RestaurantExpenses.jsx', 'src/pages/HotelExpenses.jsx']:
    with open(filename, 'r') as f:
        content = f.read()

    old_cols = """        columns={[
          { key: 'expense_date', label: 'Date' },
          { key: 'account', label: 'Expense Head', render: r => r.account ? `${r.account.code} - ${r.account.name}` : '—' },"""
          
    new_cols = """        columns={[
          { key: 'expense_date', label: 'Date' },
          { key: 'invoice_number', label: 'Invoice #', render: r => r.invoice_number || '—' },
          { key: 'account', label: 'Expense Head', render: r => r.account ? `${r.account.code} - ${r.account.name}` : '—' },"""

    content = content.replace(old_cols, new_cols)

    with open(filename, 'w') as f:
        f.write(content)
