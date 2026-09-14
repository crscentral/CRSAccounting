import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Update recharts import
code = code.replace(
    "import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'",
    "import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell } from 'recharts'"
)

# Insert the pie chart code before the BarChart
charts_jsx = """
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
          <h2 className="font-semibold text-slate-700 flex items-center gap-2 mb-2">
            <DollarSign size={18} /> Expected Profit Breakdown
          </h2>
          <div className="text-xs text-slate-500 mb-4 text-center">Total Revenue = Total Expenses + Expected Net Profit</div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={netProfit >= 0 ? [
                    { name: 'Total Expenses', value: cp.convert(totalExpenses), color: '#ef4444' },
                    { name: 'Expected Net Profit', value: cp.convert(netProfit), color: '#10b981' }
                  ] : [
                    { name: 'Total Revenue', value: cp.convert(totalBilled), color: '#10b981' },
                    { name: 'Expected Net Loss', value: cp.convert(Math.abs(netProfit)), color: '#ef4444' }
                  ]}
                  cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={2} dataKey="value"
                >
                  {(netProfit >= 0 ? [1,2] : [1,2]).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={(netProfit >= 0 ? ['#ef4444', '#10b981'] : ['#10b981', '#ef4444'])[index]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => cp.fmt(v)} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
          <h2 className="font-semibold text-slate-700 flex items-center gap-2 mb-2">
            <Receipt size={18} /> Actual Profit Breakdown
          </h2>
          <div className="text-xs text-slate-500 mb-4 text-center">Total Collected = Total Expenses Made + Actual Profit</div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={actualProfit >= 0 ? [
                    { name: 'Total Expenses Made', value: cp.convert(expensesMade), color: '#f97316' },
                    { name: 'Actual Profit', value: cp.convert(actualProfit), color: '#10b981' }
                  ] : [
                    { name: 'Total Collected', value: cp.convert(collected), color: '#eab308' },
                    { name: 'Actual Loss', value: cp.convert(Math.abs(actualProfit)), color: '#ef4444' }
                  ]}
                  cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={2} dataKey="value"
                >
                  {(actualProfit >= 0 ? [1,2] : [1,2]).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={(actualProfit >= 0 ? ['#f97316', '#10b981'] : ['#eab308', '#ef4444'])[index]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => cp.fmt(v)} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
"""

# Find where to insert it. We want it after the KPI cards and before the "Hotel Performance" (if it exists) or the Revenue/Expenses bar chart.
# Let's insert it right after the newly inserted Actual Profit grid!
code = code.replace(
    '        <KpiCard label="Actual Profit" value={cp.fmt(actualProfit)} sublabel="collected minus made" icon={DollarSign} tone={actualProfit >= 0 ? \'green\' : \'red\'} />\n      </div>',
    '        <KpiCard label="Actual Profit" value={cp.fmt(actualProfit)} sublabel="collected minus made" icon={DollarSign} tone={actualProfit >= 0 ? \'green\' : \'red\'} />\n      </div>\n' + charts_jsx
)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
