import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Replace the first pie chart title and label
old_pie1 = r"<h3 className=\"font-semibold text-slate-700 mb-4\">Actual vs Budget \(\{cp\.displayCurrency\}\)</h3>.*?<Tooltip formatter=\{\(val, name, props\) => cp\.fmt\(props\.payload\.realValue\)\} />"
new_pie1 = """<h3 className="font-semibold text-slate-700 mb-4">Actual vs Budget ({activeCompany.currency})</h3>
                <div className="h-64 sm:h-72 flex justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={[
                        { name: 'Actual', value: Math.abs(hotelStats.totalRevenue), realValue: hotelStats.totalRevenue, fill: '#1B3A6B' },
                        { name: 'Budgeted', value: Math.abs(hotelStats.totalBudgetUsd), realValue: hotelStats.totalBudgetUsd, fill: '#C9A84C' },
                        { name: 'Variance', value: Math.abs(hotelStats.totalVarianceUsd), realValue: hotelStats.totalVarianceUsd, fill: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444' }
                      ]} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={80} 
                      label={({ cx, cy, midAngle, innerRadius, outerRadius, realValue, name }) => { const RADIAN = Math.PI / 180; const radius = outerRadius + 20; const x = cx + radius * Math.cos(-midAngle * RADIAN); const y = cy + radius * Math.sin(-midAngle * RADIAN); return <text x={x} y={y} fill="#475569" textAnchor={x > cx ? "start" : "end"} dominantBaseline="central" fontSize={11}>{name}</text>; }}>
                        { [1,2,3].map((_, i) => <Cell key={i} />) }
                      </Pie>
                      <Tooltip formatter={(val, name, props) => new Intl.NumberFormat('en-US', { style: 'currency', currency: activeCompany.currency }).format(props.payload.realValue)} />"""
code = re.sub(old_pie1, new_pie1, code, flags=re.DOTALL)

# Replace the second pie chart title and label
old_pie2 = r"<h3 className=\"font-semibold text-slate-700 mb-4\">Actual vs Budget \(USD\)</h3>.*?<Tooltip formatter=\{\(val, name, props\) => new Intl\.NumberFormat\('en-US', \{ style: 'currency', currency: 'USD' \}\)\.format\(props\.payload\.realValue\)\} />"
new_pie2 = """<h3 className="font-semibold text-slate-700 mb-4">Actual vs Budget ({cp.displayCurrency})</h3>
                <div className="h-64 sm:h-72 flex justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={[
                        { name: 'Actual', value: Math.abs(hotelStats.totalRevenue), realValue: hotelStats.totalRevenue, fill: '#1B3A6B' },
                        { name: 'Budgeted', value: Math.abs(hotelStats.totalBudgetUsd), realValue: hotelStats.totalBudgetUsd, fill: '#C9A84C' },
                        { name: 'Variance', value: Math.abs(hotelStats.totalVarianceUsd), realValue: hotelStats.totalVarianceUsd, fill: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444' }
                      ]} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={80} 
                      label={({ cx, cy, midAngle, innerRadius, outerRadius, realValue, name }) => { const RADIAN = Math.PI / 180; const radius = outerRadius + 20; const x = cx + radius * Math.cos(-midAngle * RADIAN); const y = cy + radius * Math.sin(-midAngle * RADIAN); return <text x={x} y={y} fill="#475569" textAnchor={x > cx ? "start" : "end"} dominantBaseline="central" fontSize={11}>{name}</text>; }}>
                        { [1,2,3].map((_, i) => <Cell key={i} />) }
                      </Pie>
                      <Tooltip formatter={(val, name, props) => cp.fmt(props.payload.realValue)} />"""
code = re.sub(old_pie2, new_pie2, code, flags=re.DOTALL)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
