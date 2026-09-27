import os

with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "{ to: '/restaurant-revenue', label: 'Table Revenue', icon: UtensilsCrossed, products: ['restaurant'] },",
    "{ to: '/restaurant-revenue', label: 'Table Revenue', icon: UtensilsCrossed, products: ['restaurant'] },\n  { to: '/restaurant-expenses', label: 'Restaurant Expenses', icon: Receipt, products: ['restaurant'] },"
)

content = content.replace(
    "'/restaurant-revenue',",
    "'/restaurant-revenue',\n    '/restaurant-expenses',"
)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
