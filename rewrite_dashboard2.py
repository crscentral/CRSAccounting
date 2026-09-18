import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Replace the first pie block entirely
# Currently it starts at `<div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">`
# and ends right before `</div>` that closes the grid, but let's just do a greedy match
# Actually, it's safer to just split by `"grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4"` and `"const billingChartData = chartData.map"`

old_grid_start = code.find('<div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">')
old_grid_end = code.find('<div className="mt-6 flex flex-col xl:flex-row gap-6">')

if old_grid_start != -1 and old_grid_end != -1:
    new_trend_block = """<div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
                <h3 className="font-semibold text-slate-700 mb-4">Actual vs Budget ({cp.displayCurrency})</h3>
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
                      <Tooltip formatter={(val, name, props) => cp.fmt(props.payload.realValue)} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
                <h3 className="font-semibold text-slate-700 mb-4">Actual vs Budget (USD Base)</h3>
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
                      <Tooltip formatter={(val, name, props) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(props.payload.realValue)} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 lg:col-span-2">
                <h3 className="font-semibold text-slate-700 mb-4">Room Revenue: Actual vs Daily Budget</h3>
                <div className="h-64 sm:h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={hotelStats.dailyTrend}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip formatter={v => cp.fmt(v)} />
                      <Legend />
                      <Bar dataKey="Actual" fill="#1B3A6B" radius={[3, 3, 0, 0]} />
                      <Bar dataKey="Budget" fill="#C9A84C" radius={[3, 3, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>\n\n            """
    code = code[:old_grid_start] + new_trend_block + code[old_grid_end:]
    
    with open('src/pages/Dashboard.jsx', 'w') as f:
        f.write(code)
    print("Success")
else:
    print("Could not find blocks")
