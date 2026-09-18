import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# 1. Update loadHotelStats to export totalBudget and totalVariance
old_stats_set = r'setHotelStats\(\{ occupancyPct, adr, revpar, invoicesPending, totalRevenue, dailyTrend \}\)'
new_stats_set = """const totalBudgetUsd = dailyTrend.reduce((sum, d) => sum + d.Budget, 0)
    const totalVarianceUsd = totalRevenue - totalBudgetUsd
    setHotelStats({ occupancyPct, adr, revpar, invoicesPending, totalRevenue, totalBudgetUsd, totalVarianceUsd, dailyTrend })"""
code = re.sub(old_stats_set, new_stats_set, code)

# 2. Render the two pie charts
old_trend_block = r'\{\s*hotelStats.dailyTrend.length > 1 && \(\s*<div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mt-4">.*?</div>\s*\)\s*\}'
new_trend_block = """{hotelStats.dailyTrend.length > 1 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
                <h3 className="font-semibold text-slate-700 mb-4">Actual vs Budget ({cp.displayCurrency})</h3>
                <div className="h-64 sm:h-72 flex justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={[
                        { name: 'Actual', value: Math.abs(hotelStats.totalRevenue), realValue: hotelStats.totalRevenue, fill: '#1B3A6B' },
                        { name: 'Budgeted', value: Math.abs(hotelStats.totalBudgetUsd), realValue: hotelStats.totalBudgetUsd, fill: '#C9A84C' },
                        { name: 'Variance', value: Math.abs(hotelStats.totalVarianceUsd), realValue: hotelStats.totalVarianceUsd, fill: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444' }
                      ]} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} label={false}>
                        { [1,2,3].map((_, i) => <Cell key={i} />) }
                      </Pie>
                      <Tooltip formatter={(val, name, props) => cp.fmt(props.payload.realValue)} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
                <h3 className="font-semibold text-slate-700 mb-4">Actual vs Budget (USD)</h3>
                <div className="h-64 sm:h-72 flex justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={[
                        { name: 'Actual', value: Math.abs(hotelStats.totalRevenue), realValue: hotelStats.totalRevenue, fill: '#1B3A6B' },
                        { name: 'Budgeted', value: Math.abs(hotelStats.totalBudgetUsd), realValue: hotelStats.totalBudgetUsd, fill: '#C9A84C' },
                        { name: 'Variance', value: Math.abs(hotelStats.totalVarianceUsd), realValue: hotelStats.totalVarianceUsd, fill: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444' }
                      ]} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} label={false}>
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
            </div>
          )}"""

code = re.sub(old_trend_block, new_trend_block, code, flags=re.DOTALL)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
