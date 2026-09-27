import re

with open('src/pages/RestaurantExpenses.jsx', 'r') as f:
    content = f.read()

# Replace the broken KPI block that has totalAmc + totalEntries
broken_kpi_start = '<div className="grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-6 mb-6">'
broken_kpi_end = '</div>'

# Find the block and replace it
start_idx = content.find(broken_kpi_start)
if start_idx != -1:
    end_idx = content.find(broken_kpi_end, start_idx)
    
    new_kpis = """<div className="grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-6 mb-6">
        <KpiCard label="Total Expenses" value={cp.fmt(totalExpenses)} tone="slate" />
        <KpiCard label="Budgeted Expenses" value={cp.fmt(budgetTotal)} tone="slate" />
        <KpiCard 
          label="Over / Under Budget" 
          value={cp.fmt(totalExpenses - budgetTotal)} 
          tone={(totalExpenses - budgetTotal) > 0 ? 'red' : 'green'} 
        />
      </div>"""
    
    content = content[:start_idx] + new_kpis + content[end_idx + len(broken_kpi_end):]

# Remove the Pie Charts block completely
pie_start = '<div className="grid lg:grid-cols-2 gap-4 mb-6">'
pie_end = '{/* Tabs */}'

start_idx = content.find(pie_start)
if start_idx != -1:
    end_idx = content.find(pie_end, start_idx)
    if end_idx != -1:
        content = content[:start_idx] + content[end_idx:]

with open('src/pages/RestaurantExpenses.jsx', 'w') as f:
    f.write(content)
