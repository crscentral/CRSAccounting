with open('src/components/AppShell.jsx', 'r') as f:
    code = f.read()

code = code.replace(
    "{ to: '/hotel-budget', label: 'Room Revenue Budget', icon: Target, products: ['hotel'] },",
    "{ to: '/hotel-budget', label: 'Room Revenue Budget', icon: Target, products: ['hotel'] },\n  { to: '/hotel-expense-budget', label: 'Expenses Budget', icon: Target, products: ['hotel'] },"
)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(code)
