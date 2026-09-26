with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

# Replace Pie Chart labels
old_pie_1 = """          <h2 className="font-semibold text-slate-700 flex items-center gap-2 mb-4 self-start">
            <DollarSign size={18} /> Expected Profit Breakdown
          </h2>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={[{ name: 'Total Revenue', value: totalBilled }, { name: 'Total Expenses', value: totalExpenses }]} cx="50%" cy="50%" innerRadius={70} outerRadius={100} paddingAngle={2} dataKey="value">"""

new_pie_1 = """          <h2 className="font-semibold text-slate-700 flex items-center gap-2 mb-4 self-start">
            <DollarSign size={18} /> {['hotel', 'restaurant'].includes(activeProduct) ? 'Accrued Profit Breakdown' : 'Expected Profit Breakdown'}
          </h2>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={[{ name: ['hotel', 'restaurant'].includes(activeProduct) ? 'Accrued Revenue' : 'Total Revenue', value: totalBilled }, { name: ['hotel', 'restaurant'].includes(activeProduct) ? 'Accrued Expenses' : 'Total Expenses', value: totalExpenses }]} cx="50%" cy="50%" innerRadius={70} outerRadius={100} paddingAngle={2} dataKey="value">"""

old_pie_2 = """          <h2 className="font-semibold text-slate-700 flex items-center gap-2 mb-4 self-start">
            <Receipt size={18} /> Actual Profit Breakdown
          </h2>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={[{ name: 'Revenue Collected', value: collected }, { name: 'Expenses Made', value: expensesMade }]} cx="50%" cy="50%" innerRadius={70} outerRadius={100} paddingAngle={2} dataKey="value">"""

new_pie_2 = """          <h2 className="font-semibold text-slate-700 flex items-center gap-2 mb-4 self-start">
            <Receipt size={18} /> {['hotel', 'restaurant'].includes(activeProduct) ? 'Cash Profit Breakdown' : 'Actual Profit Breakdown'}
          </h2>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={[{ name: 'Revenue Collected', value: collected }, { name: 'Expenses Paid', value: expensesMade }]} cx="50%" cy="50%" innerRadius={70} outerRadius={100} paddingAngle={2} dataKey="value">"""

content = content.replace(old_pie_1, new_pie_1)
content = content.replace(old_pie_2, new_pie_2)

# Also update the KPI card titles to match Accrued/Cash instead of Expected/Actual for Hotel
old_kpi_profit = """<KpiCard label="Expected Net Profit" value={cp.fmt(netProfit)} sublabel="revenue minus expenses" icon={DollarSign} tone={netProfit >= 0 ? 'green' : 'red'} />"""
new_kpi_profit = """<KpiCard label={['hotel', 'restaurant'].includes(activeProduct) ? 'Accrued Net Profit' : 'Expected Net Profit'} value={cp.fmt(netProfit)} sublabel="revenue minus expenses" icon={DollarSign} tone={netProfit >= 0 ? 'green' : 'red'} />"""

old_kpi_actual = """<KpiCard label="Actual Profit" value={cp.fmt(actualProfit)} sublabel="collected minus paid" icon={DollarSign} tone={actualProfit >= 0 ? 'green' : 'red'} />"""
new_kpi_actual = """<KpiCard label={['hotel', 'restaurant'].includes(activeProduct) ? 'Cash Net Profit' : 'Actual Profit'} value={cp.fmt(actualProfit)} sublabel="collected minus paid" icon={DollarSign} tone={actualProfit >= 0 ? 'green' : 'red'} />"""

content = content.replace(old_kpi_profit, new_kpi_profit)
content = content.replace(old_kpi_actual, new_kpi_actual)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)
