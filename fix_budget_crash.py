import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

# Replace fmt(dailyBudget) with fmt(monthlyBudget)
code = code.replace("fmt(dailyBudget)", "fmt(monthlyBudget)")

# Replace the TH headers just in case they didn't get replaced either
code = code.replace(">Daily Budget</th>", ">Monthly Budget</th>")
code = code.replace(">Budgeted Revenue</th>", ">Budgeted Daily Rev.</th>")

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
