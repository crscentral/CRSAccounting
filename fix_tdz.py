import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# Find the block of state declarations around line 193
state_block = """  const [saving, setSaving] = useState({})
  const [displayCurrency, setDisplayCurrency] = useState('USD')
  const [rate, setRate] = useState(1)
  const [rates, setRates] = useState({})"""

# Remove it from its current position
content = content.replace(state_block, "")

# Insert it at the top, right after `const [actuals, setActuals] = useState({})`
top_state = """  const [actuals, setActuals] = useState({}) // key: "year-month" -> { occ, adr, revenue, currency }
  const [saving, setSaving] = useState({})
  const [displayCurrency, setDisplayCurrency] = useState('USD')
  const [rate, setRate] = useState(1)
  const [rates, setRates] = useState({})
"""

content = content.replace('  const [actuals, setActuals] = useState({}) // key: "year-month" -> { occ, adr, revenue, currency }', top_state)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
