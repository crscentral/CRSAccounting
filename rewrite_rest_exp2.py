import os

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

# 1. Rename component
content = content.replace('export default function HotelExpenses()', 'export default function RestaurantExpenses()')

# 2. Add budget loading
content = content.replace(
    "supabase.from('hotel_room_stats')", 
    "supabase.from('hotel_expense_budget').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)"
)
content = content.replace("roomStats", "budgetsData")
content = content.replace("setTotalRooms(settings?.total_rooms || 0)", "")
content = content.replace("setTotalOccupied((roomStats || []).reduce((s, r) => s + (Number(r.rooms_occupied) || 0), 0))", "")
content = content.replace("const [totalRooms, setTotalRooms] = useState(0)", "")
content = content.replace("const [totalOccupied, setTotalOccupied] = useState(0)", "const [budgetTotal, setBudgetTotal] = useState(0)")

budget_calc = """
    let bTotal = 0
    if (budgetsData && budgetsData.length > 0) {
      const fromDate = new Date(cp.range.from)
      const toDate = new Date(cp.range.to)
      
      budgetsData.forEach(b => {
        const d = new Date(b.budget_year, b.budget_month - 1, 15)
        if (d >= fromDate && d <= toDate) {
          bTotal += Number(b.amount_usd || 0)
        }
      })
    }
    setBudgetTotal(bTotal)
"""
content = content.replace("setExpenseAccounts(accs || [])", "setExpenseAccounts(accs || [])\n" + budget_calc)

# 3. Modify KPIs
start_kpi = '<div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">'
end_kpi = '</div>'
new_kpis = """<div className="grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-6 mb-6">
        <KpiCard title="Total Expenses" amount={cp.fmt(totalAmc + totalEntries)} />
        <KpiCard title="Budgeted Expenses" amount={cp.fmt(budgetTotal)} />
        <KpiCard 
          title="Over / Under Budget" 
          amount={cp.fmt((totalAmc + totalEntries) - budgetTotal)} 
          isNegative={((totalAmc + totalEntries) - budgetTotal) > 0} 
          subtitle={((totalAmc + totalEntries) - budgetTotal) > 0 ? 'Over Budget' : 'Under Budget'}
        />
      </div>"""

# Replace the block from start_kpi to its closing div (by finding the next <div className="grid lg:grid-cols-2 gap-4 mb-6">)
start_idx = content.find(start_kpi)
end_idx = content.find('<div className="grid lg:grid-cols-2 gap-4 mb-6">')
if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_kpis + "\n      " + content[end_idx:]

# 4. Remove Pie Charts
pie_start = '<div className="grid lg:grid-cols-2 gap-4 mb-6">'
pie_end = '      {/* Tabs */}'
start_idx = content.find(pie_start)
end_idx = content.find(pie_end)
if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + content[end_idx:]

# Also replace references to "HotelExpenses" or "Hotel Expenses"
content = content.replace("HotelExpenses", "RestaurantExpenses")
content = content.replace("Hotel Expenses", "Restaurant Expenses")

with open('src/pages/RestaurantExpenses.jsx', 'w') as f:
    f.write(content)
