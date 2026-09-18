import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Replace the messy double-wrappers
code = code.replace("{activeProduct !== 'hotel' && (\n      {activeProduct !== 'hotel' && (\n      <div", "{activeProduct !== 'hotel' && (\n      <div")

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
