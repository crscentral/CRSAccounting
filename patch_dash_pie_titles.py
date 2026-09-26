import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

# I want to change:
# <DollarSign size={18} /> Expected Profit Breakdown
# to
# <DollarSign size={18} /> {['hotel', 'restaurant'].includes(activeProduct) ? 'Accrued Net Profit' : 'Expected Profit Breakdown'}
content = content.replace("<DollarSign size={18} /> Expected Profit Breakdown", "<DollarSign size={18} /> {['hotel', 'restaurant'].includes(activeProduct) ? 'Accrued Net Profit' : 'Expected Profit Breakdown'}")

# I want to change:
# <Receipt size={18} /> Cash Net Profit
# to
# <Receipt size={18} /> {['hotel', 'restaurant'].includes(activeProduct) ? 'Cash Net Profit' : 'Actual Profit Breakdown'}
content = content.replace("<Receipt size={18} /> Cash Net Profit", "<Receipt size={18} /> {['hotel', 'restaurant'].includes(activeProduct) ? 'Cash Net Profit' : 'Actual Profit Breakdown'}")

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)
