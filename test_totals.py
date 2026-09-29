with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

import re
match = re.search(r"const totalExpenses = (.*?)\n", content)
print(match.group(0))
