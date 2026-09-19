import re

with open('src/components/AppShell.jsx', 'r') as f:
    code = f.read()

# Add to NAV_ITEMS safely
if "to: '/hotel-expense-budget'" not in code:
    code = code.replace(
        "{ to: '/hotel-budget', label: 'Room Revenue Budget', icon: Target, products: ['hotel'] },",
        "{ to: '/hotel-budget', label: 'Room Revenue Budget', icon: Target, products: ['hotel'] },\n  { to: '/hotel-expense-budget', label: 'Expenses Budget', icon: Target, products: ['hotel'] },"
    )

# Add to HOTEL_NAV_ORDER safely
if "'/hotel-expense-budget'" not in code.split("HOTEL_NAV_ORDER")[1]:
    old_order = """    '/hotel-budget',
    '/contacts',"""
    new_order = """    '/hotel-budget',
    '/hotel-expense-budget',
    '/contacts',"""
    code = code.replace(old_order, new_order)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(code)
