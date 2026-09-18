import re

with open('src/pages/HotelRevenue.jsx', 'r') as f:
    code = f.read()

# Replace the flex block for the header actions
old_actions = r'<div className="flex flex-wrap items-center gap-2 sm:gap-3">'
new_actions = '<div className="flex items-center gap-2 sm:gap-3 overflow-x-auto whitespace-nowrap pb-1 scrollbar-hide">'
code = re.sub(old_actions, new_actions, code)

with open('src/pages/HotelRevenue.jsx', 'w') as f:
    f.write(code)
