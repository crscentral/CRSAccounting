import os

with open('src/App.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "import RestaurantRevenue from './pages/RestaurantRevenue'",
    "import RestaurantRevenue from './pages/RestaurantRevenue'\nimport RestaurantExpenses from './pages/RestaurantExpenses'"
)

content = content.replace(
    '<Route path="/restaurant-revenue" element={<RestaurantRevenue />} />',
    '<Route path="/restaurant-revenue" element={<RestaurantRevenue />} />\n        <Route path="/restaurant-expenses" element={<RestaurantExpenses />} />'
)

with open('src/App.jsx', 'w') as f:
    f.write(content)
