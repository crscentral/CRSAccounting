with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

# I need to find "Actual Profit Breakdown" and replace it with "Cash Net Profit".
# Also need to check if there is logic for 'hotel' / 'restaurant' that sets it to "Actual Profit Breakdown".
# Let's search for "Profit Breakdown" in Dashboard.jsx

# Earlier I had: 
# const pieTitle1 = ['hotel', 'restaurant'].includes(activeProduct) ? 'Accrued Profit Breakdown' : 'Expected Profit Breakdown'
# const pieTitle2 = ['hotel', 'restaurant'].includes(activeProduct) ? 'Actual Profit Breakdown' : 'Actual Profit Breakdown'
# Or maybe it's hardcoded.

import re

# First let's just see how it's defined currently
with open('src/pages/Dashboard.jsx', 'w') as f:
    # If it is hardcoded in the JSX:
    content = content.replace("Actual Profit Breakdown", "Cash Net Profit")
    
    # Wait, what if there's a dynamic title?
    # Let's look for "Expected Profit Breakdown" as well, it should probably be "Accrued Net Profit" for hotel?
    # The user only asked to rename "Actual Profit Breakdown" to "Cash Net Profit". I'll just do a global replace for now, it's safer.
    
    f.write(content)
