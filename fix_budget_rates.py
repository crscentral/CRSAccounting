import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

# 1. Add `rates` state and update `loadAll`
old_state = r'const \[rate, setRate\] = useState\(1\)'
new_state = """const [rate, setRate] = useState(1)
  const [rates, setRates] = useState({})"""

code = re.sub(old_state, new_state, code)

old_load_effect = r"useEffect\(\(\) => \{ if \(activeCompany\) loadAll\(\) \}, \[activeCompany, activeProduct, startYear\]\)"
new_load_effect = """useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct, startYear])

  useEffect(() => {
    async function loadRates() {
      const rs = {}
      for (const c of CURRENCIES) {
        if (c.code !== 'USD') rs[c.code] = await getLatestRate(c.code)
      }
      setRates(rs)
    }
    loadRates()
  }, [])"""

code = re.sub(old_load_effect, new_load_effect, code)


old_tbody = r'const actualLocal = convertFromUsd\(actualUsd, row.currency \|\| displayCurrency, \{ \[row.currency \|\| displayCurrency\]: rate \}\)'
new_tbody = """const cur = row.currency || displayCurrency
                const r = cur === 'USD' ? 1 : (rates[cur] || rate)
                const actualLocal = cur === 'USD' ? actualUsd : (actualUsd * r)"""

code = re.sub(old_tbody, new_tbody, code)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
