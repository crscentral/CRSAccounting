import re

with open('src/pages/Ledger.jsx', 'r') as f:
    content = f.read()

# Wait, instead of a complex regex, I can just write a script to replace the whole block.
# Let's see what is inside Ledger.jsx for hotel/restaurant.
