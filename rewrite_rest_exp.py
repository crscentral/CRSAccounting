import re

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

# Calculate budgetTotal based on range
# We need a small helper to calculate budget months in range.
budget_calc = """
    let bTotal = 0
    if (budgetsData && budgetsData.length > 0) {
      const fromDate = new Date(cp.range.from)
      const toDate = new Date(cp.range.to)
      
      budgetsData.forEach(b => {
        // b.budget_year and b.budget_month
        const d = new Date(b.budget_year, b.budget_month - 1, 15) // middle of month
        if (d >= fromDate && d <= toDate) {
          bTotal += Number(b.amount_usd || 0)
        }
      })
    }
    setBudgetTotal(bTotal)
"""
content = content.replace("setExpenseAccounts(accs || [])", "setExpenseAccounts(accs || [])\n" + budget_calc)

# 3. Modify KPIs
kpi_regex = r'<div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-5 gap-4 lg:gap-6 mb-6">[\s\S]*?</div>'

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

content = re.sub(kpi_regex, new_kpis, content)

# 4. Remove Pie Charts
pie_regex = r'{/\* Department Breakdown \*/}[\s\S]*?</div>\s*</div>'
content = re.sub(pie_regex, '', content)

with open('src/pages/RestaurantExpenses.jsx', 'w') as f:
    f.write(content)

