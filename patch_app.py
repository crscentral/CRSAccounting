import re

with open('src/App.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "<Route path=\"/hotel-expense-budget\" element={<HotelExpenseBudget />} />",
    "<Route path=\"/hotel-expense-budget\" element={<HotelExpenseBudget />} />\n        <Route path=\"/restaurant-budget\" element={<HotelBudget />} />\n        <Route path=\"/restaurant-expense-budget\" element={<HotelExpenseBudget />} />"
)

with open('src/App.jsx', 'w') as f:
    f.write(content)

with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

# Add to NAV_ITEMS
old_nav = "  { to: '/restaurant-revenue', label: 'Table Revenue', icon: UtensilsCrossed, products: ['restaurant'] },"
new_nav = """  { to: '/restaurant-revenue', label: 'Table Revenue', icon: UtensilsCrossed, products: ['restaurant'] },
  { to: '/restaurant-budget', label: 'F&B Revenue Budget', icon: Target, products: ['restaurant'] },
  { to: '/restaurant-expense-budget', label: 'F&B Expense Budget', icon: PiggyBank, products: ['restaurant'] },"""

content = content.replace(old_nav, new_nav)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
