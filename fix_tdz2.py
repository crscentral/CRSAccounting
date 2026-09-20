import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

top_state = """  const [actuals, setActuals] = useState({}) // key: "year-month" -> revenue_usd actual
  const [saving, setSaving] = useState({})
  const [displayCurrency, setDisplayCurrency] = useState('USD')
  const [rate, setRate] = useState(1)
  const [rates, setRates] = useState({})
"""

content = content.replace('  const [actuals, setActuals] = useState({}) // key: "year-month" -> revenue_usd actual', top_state)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
