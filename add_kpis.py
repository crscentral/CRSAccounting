with open('src/pages/RestaurantExpenses.jsx', 'r') as f:
    content = f.read()

anchor = """      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-6 mb-6">
        <KpiCard label="Total Expenses" value={cp.fmt(totalExpenses)} tone="slate" />
        <KpiCard label="Budgeted Expenses" value={cp.fmt(budgetTotal)} tone="slate" />
        <KpiCard 
          label="Over / Under Budget" 
          value={cp.fmt(totalExpenses - budgetTotal)} 
          tone={(totalExpenses - budgetTotal) > 0 ? 'red' : 'green'} 
        />
      </div>"""

to_insert = """
      <div className="grid grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Billed" value={cp.fmt(totalBilled)} tone="slate" />
        <KpiCard label="Total Paid" value={cp.fmt(totalPaid)} tone="green" />
        <KpiCard label="Total Pending" value={cp.fmt(totalPending)} tone="red" />
      </div>"""

content = content.replace(anchor, anchor + to_insert)

with open('src/pages/RestaurantExpenses.jsx', 'w') as f:
    f.write(content)
