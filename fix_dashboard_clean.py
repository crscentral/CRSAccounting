import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

code = code.replace("export default export default function Dashboard() {", "export default function Dashboard() {")

# Add renderCustomLegend helper if not exists
if 'const renderCustomLegend' not in code:
    code = code.replace("export default function Dashboard() {", """const renderCustomLegend = (props, formatter) => {
  const { payload } = props;
  return (
    <ul className="flex flex-wrap justify-center gap-4 mt-2 text-xs">
      {payload.map((entry, index) => (
        <li key={`item-${index}`} className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
          <span className="text-slate-600 font-medium">
            {entry.value}: {formatter(entry.payload.realValue)}
          </span>
        </li>
      ))}
    </ul>
  );
}

export default function Dashboard() {""")

# Replace pie charts cleanly using string parsing, not regex dotall
import ast
import textwrap

# The best way is to split by `<div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 lg:col-span-2">` which is the start of the Trend chart right after the two pie charts.
parts = code.split('<div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 lg:col-span-2">')

if len(parts) == 2:
    # Now find the start of the grid containing the pie charts
    start_str = '<div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">'
    grid_start = parts[0].find(start_str)
    if grid_start != -1:
        prefix = parts[0][:grid_start + len(start_str)]
        
        new_pies = """
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
                <h3 className="font-semibold text-slate-700 mb-4">Actual vs Budget ({activeCompany?.currency || 'USD'})</h3>
                <div className="h-64 sm:h-72 flex flex-col justify-center">
                  <ResponsiveContainer width="100%" height="80%">
                    <PieChart>
                      <Pie data={[
                        { name: 'Actual', value: Math.abs(hotelStats.totalRevenue), realValue: hotelStats.totalRevenue, fill: '#1B3A6B' },
                        { name: 'Budgeted', value: Math.abs(hotelStats.totalBudgetUsd), realValue: hotelStats.totalBudgetUsd, fill: '#C9A84C' },
                        { name: 'Variance', value: Math.abs(hotelStats.totalVarianceUsd), realValue: hotelStats.totalVarianceUsd, fill: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444' }
                      ]} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} label={false}>
                        { [1,2,3].map((_, i) => <Cell key={i} />) }
                      </Pie>
                      <Tooltip formatter={(val, name, props) => new Intl.NumberFormat('en-US', { style: 'currency', currency: activeCompany?.currency || 'USD' }).format(props.payload.realValue)} />
                      <Legend content={(props) => renderCustomLegend(props, (v) => new Intl.NumberFormat('en-US', { style: 'currency', currency: activeCompany?.currency || 'USD' }).format(v))} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
                <h3 className="font-semibold text-slate-700 mb-4">Actual vs Budget ({cp.displayCurrency})</h3>
                <div className="h-64 sm:h-72 flex flex-col justify-center">
                  <ResponsiveContainer width="100%" height="80%">
                    <PieChart>
                      <Pie data={[
                        { name: 'Actual', value: Math.abs(hotelStats.totalRevenue), realValue: hotelStats.totalRevenue, fill: '#1B3A6B' },
                        { name: 'Budgeted', value: Math.abs(hotelStats.totalBudgetUsd), realValue: hotelStats.totalBudgetUsd, fill: '#C9A84C' },
                        { name: 'Variance', value: Math.abs(hotelStats.totalVarianceUsd), realValue: hotelStats.totalVarianceUsd, fill: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444' }
                      ]} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} label={false}>
                        { [1,2,3].map((_, i) => <Cell key={i} />) }
                      </Pie>
                      <Tooltip formatter={(val, name, props) => cp.fmt(props.payload.realValue)} />
                      <Legend content={(props) => renderCustomLegend(props, cp.fmt)} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
              """
        
        code = prefix + new_pies + '<div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 lg:col-span-2">' + parts[1]

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)

