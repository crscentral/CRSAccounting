import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

# Add FX Rates state to HotelBudget to show live USD conversions
code = code.replace(
    "const [displayCurrency, setDisplayCurrency] = useState(cp.displayCurrency)",
    "const [displayCurrency, setDisplayCurrency] = useState(cp.displayCurrency)\n  const [rates, setRates] = useState({})"
)

# Fetch latest rates on mount so we can display live USD conversion
code = code.replace(
    "useEffect(() => { if (activeCompany) loadData() }, [activeCompany, activeProduct])",
    "useEffect(() => { if (activeCompany) { loadData(); fetchRates(); } }, [activeCompany, activeProduct])\n  async function fetchRates() {\n    // fetch a few common rates or just rely on getLatestRate for the selected ones\n  }"
)
# Actually, since we need dynamic rates for each row's currency, let's just make a helper that loads rates as needed, or simpler: since they enter it, we can just show `(converted upon save)`.
# Even better, the database ALREADY has `budgeted_room_revenue_usd` for saved rows!
