import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

# 1. Add state for hotel purchase invoices bounded by period
content = content.replace(
    "const [hotelExpenseEntries, setHotelExpenseEntries] = useState([])",
    "const [hotelExpenseEntries, setHotelExpenseEntries] = useState([])\n  const [hotelPurchaseInvoices, setHotelPurchaseInvoices] = useState([])"
)

# 2. Add state for ALL hotel purchase invoices (for charts/YTD)
content = content.replace(
    "const [allHotelExpenseEntries, setAllHotelExpenseEntries] = useState([])",
    "const [allHotelExpenseEntries, setAllHotelExpenseEntries] = useState([])\n  const [allHotelPurchaseInvoices, setAllHotelPurchaseInvoices] = useState([])"
)

# 3. Fix the destructuring of the first Promise.all in loadData
old_first_destructure = "const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }, { data: accs }, { data: led }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }, { data: rdr }] = await Promise.all(["
new_first_destructure = "const [{ data: s }, { data: p }, { data: r }, { data: allS }, { data: allP }, { data: accs }, { data: led }, { data: hrs }, { data: hgi }, { data: hee }, { data: hamc }, { data: hre }, { data: rdr }, { data: hPi }] = await Promise.all(["
content = content.replace(old_first_destructure, new_first_destructure)

# 4. Set the bounded hPi to state
content = content.replace(
    "setHotelExpenseEntries(hee || [])",
    "setHotelExpenseEntries(hee || [])\n    setHotelPurchaseInvoices(hPi || [])"
)

# 5. Fix the destructuring of the second Promise.all in loadData
old_second_destructure = """    let allHrs = [], allHgi = [], allHee = [], allHre = [], allRdr = [];
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      const [{ data: aHrs }, { data: aHgi }, { data: aHee }, { data: aHre }, { data: aRdr }, { data: aHotelPi }] = await Promise.all(["""
new_second_destructure = """    let allHrs = [], allHgi = [], allHee = [], allHre = [], allRdr = [], allHPi = [];
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      const [{ data: aHrs }, { data: aHgi }, { data: aHee }, { data: aHre }, { data: aRdr }, { data: aHotelPi }] = await Promise.all(["""
content = content.replace(old_second_destructure, new_second_destructure)

content = content.replace(
    "allHee = aHee || []",
    "allHee = aHee || []\n      allHPi = aHotelPi || []"
)

content = content.replace(
    "setAllHotelExpenseEntries(allHee)",
    "setAllHotelExpenseEntries(allHee)\n    setAllHotelPurchaseInvoices(allHPi)"
)

# 6. Fix Total Expenses KPI calculation
old_kpi_calc = """    // Link Total Expenses directly to Expenses page
    const amcTotal = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    const directExpenses = hotelExpenseEntries.reduce((s, e) => s + Number(e.amount_usd || 0), 0)
    totalExpenses = directExpenses + amcTotal"""
new_kpi_calc = """    // Link Total Expenses directly to Expenses page
    const amcTotal = hotelAmc.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0) * monthsInView
    const directExpenses = hotelExpenseEntries.reduce((s, e) => s + Number(e.amount_usd || 0), 0)
    const piExpenses = hotelPurchaseInvoices.reduce((s, e) => s + Number(e.amount_usd || 0), 0)
    totalExpenses = directExpenses + amcTotal + piExpenses"""
content = content.replace(old_kpi_calc, new_kpi_calc)

# 7. Fix exportPDF function destructuring
# Note: exportPDF has exactly the same structure for loadData
content = content.replace(old_first_destructure, new_first_destructure)
content = content.replace(old_second_destructure, new_second_destructure)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)
