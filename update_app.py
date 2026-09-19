with open('src/App.jsx', 'r') as f:
    code = f.read()

code = code.replace(
    "import HotelBudget from './pages/HotelBudget'",
    "import HotelBudget from './pages/HotelBudget'\nimport HotelExpenseBudget from './pages/HotelExpenseBudget'"
)

code = code.replace(
    '<Route path="/hotel-budget" element={<HotelBudget />} />',
    '<Route path="/hotel-budget" element={<HotelBudget />} />\n          <Route path="/hotel-expense-budget" element={<HotelExpenseBudget />} />'
)

with open('src/App.jsx', 'w') as f:
    f.write(code)
