import os

with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

# Fix the broken line 28
content = content.replace(
    "{ to: '/restaurant-revenue',\n    '/restaurant-expenses', label: 'Table Revenue', icon: UtensilsCrossed, products: ['restaurant'] },",
    "{ to: '/restaurant-revenue', label: 'Table Revenue', icon: UtensilsCrossed, products: ['restaurant'] },"
)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
