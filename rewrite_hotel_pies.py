import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Replace the two Hotel Pie charts
old_pie_grid = r'<div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">\s*<h3 className="font-semibold text-slate-700 mb-4">Actual vs Budget \(\{hotelStats\.budgetCurrency\}\)</h3>.*?<div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 lg:col-span-2">'

new_pie_grid = """<div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 flex flex-col items-center">
                <h3 className="font-semibold text-slate-700 mb-4 self-start">Actual vs Budget ({hotelStats.budgetCurrency})</h3>
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={[
                        { name: 'Actual', value: Math.abs(hotelStats.totalRevenue), realValue: hotelStats.totalRevenue, fill: '#1B3A6B' },
                        { name: 'Budgeted', value: Math.abs(hotelStats.totalBudgetUsd), realValue: hotelStats.totalBudgetUsd, fill: '#C9A84C' },
                        { name: 'Variance', value: Math.abs(hotelStats.totalVarianceUsd), realValue: hotelStats.totalVarianceUsd, fill: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444' }
                      ]} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={80} outerRadius={120} paddingAngle={2} label={false}>
                        { [1,2,3].map((_, i) => <Cell key={i} />) }
                      </Pie>
                      <Tooltip formatter={(val, name, props) => new Intl.NumberFormat('en-US', { style: 'currency', currency: hotelStats.budgetCurrency }).format(props.payload.realValue)} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap gap-x-6 gap-y-2 justify-center text-sm mt-2 text-slate-600 w-full">
                   <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: '#1B3A6B'}}></span> Actual: {new Intl.NumberFormat('en-US', { style: 'currency', currency: hotelStats.budgetCurrency }).format(hotelStats.totalRevenue)}</div>
                   <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: '#C9A84C'}}></span> Budgeted: {new Intl.NumberFormat('en-US', { style: 'currency', currency: hotelStats.budgetCurrency }).format(hotelStats.totalBudgetUsd)}</div>
                   <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444'}}></span> Variance: {new Intl.NumberFormat('en-US', { style: 'currency', currency: hotelStats.budgetCurrency }).format(hotelStats.totalVarianceUsd)}</div>
                </div>
              </div>
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 flex flex-col items-center">
                <h3 className="font-semibold text-slate-700 mb-4 self-start">Actual vs Budget ({cp.displayCurrency})</h3>
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={[
                        { name: 'Actual', value: Math.abs(hotelStats.totalRevenue), realValue: hotelStats.totalRevenue, fill: '#1B3A6B' },
                        { name: 'Budgeted', value: Math.abs(hotelStats.totalBudgetUsd), realValue: hotelStats.totalBudgetUsd, fill: '#C9A84C' },
                        { name: 'Variance', value: Math.abs(hotelStats.totalVarianceUsd), realValue: hotelStats.totalVarianceUsd, fill: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444' }
                      ]} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={80} outerRadius={120} paddingAngle={2} label={false}>
                        { [1,2,3].map((_, i) => <Cell key={i} />) }
                      </Pie>
                      <Tooltip formatter={(val, name, props) => cp.fmt(props.payload.realValue)} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap gap-x-6 gap-y-2 justify-center text-sm mt-2 text-slate-600 w-full">
                   <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: '#1B3A6B'}}></span> Actual: {cp.fmt(hotelStats.totalRevenue)}</div>
                   <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: '#C9A84C'}}></span> Budgeted: {cp.fmt(hotelStats.totalBudgetUsd)}</div>
                   <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444'}}></span> Variance: {cp.fmt(hotelStats.totalVarianceUsd)}</div>
                </div>
              </div>
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 lg:col-span-2">"""

code = re.sub(old_pie_grid, new_pie_grid, code, flags=re.DOTALL)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
