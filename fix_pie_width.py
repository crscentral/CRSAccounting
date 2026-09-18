import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# 1. Add budgetCurrency to hotelStats
old_set_stats = r"totalVarianceUsd,"
new_set_stats = "totalVarianceUsd,\n      budgetCurrency: budgetRows?.[0]?.currency || activeCompany?.currency || 'USD',"
code = re.sub(old_set_stats, new_set_stats, code, count=1)

# 2. Fix the pie chart attributes and currency logic
old_pie1 = r"<h3 className=\"font-semibold text-slate-700 mb-4\">Actual vs Budget \(\{activeCompany\?.currency \|\| 'USD'\}\)</h3>.*?<Tooltip formatter=\{\(val, name, props\) => new Intl\.NumberFormat\('en-US', \{ style: 'currency', currency: activeCompany\?.currency \|\| 'USD' \}\)\.format\(props\.payload\.realValue\)\} />\s*<Legend content=\{\(props\) => renderCustomLegend\(props, \(v\) => new Intl\.NumberFormat\('en-US', \{ style: 'currency', currency: activeCompany\?.currency \|\| 'USD' \}\)\.format\(v\)\)\} />\s*</PieChart>"

new_pie1 = """<h3 className="font-semibold text-slate-700 mb-4">Actual vs Budget ({hotelStats.budgetCurrency})</h3>
                <div className="h-64 sm:h-72 flex flex-col justify-center">
                  <ResponsiveContainer width="100%" height="80%">
                    <PieChart>
                      <Pie data={[
                        { name: 'Actual', value: Math.abs(hotelStats.totalRevenue), realValue: hotelStats.totalRevenue, fill: '#1B3A6B' },
                        { name: 'Budgeted', value: Math.abs(hotelStats.totalBudgetUsd), realValue: hotelStats.totalBudgetUsd, fill: '#C9A84C' },
                        { name: 'Variance', value: Math.abs(hotelStats.totalVarianceUsd), realValue: hotelStats.totalVarianceUsd, fill: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444' }
                      ]} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={80} outerRadius={120} paddingAngle={2} label={false}>
                        { [1,2,3].map((_, i) => <Cell key={i} />) }
                      </Pie>
                      <Tooltip formatter={(val, name, props) => new Intl.NumberFormat('en-US', { style: 'currency', currency: hotelStats.budgetCurrency }).format(props.payload.realValue)} />
                      <Legend content={(props) => renderCustomLegend(props, (v) => new Intl.NumberFormat('en-US', { style: 'currency', currency: hotelStats.budgetCurrency }).format(v))} />
                    </PieChart>"""

code = re.sub(old_pie1, new_pie1, code, flags=re.DOTALL)

old_pie2 = r"<h3 className=\"font-semibold text-slate-700 mb-4\">Actual vs Budget \(\{cp\.displayCurrency\}\)</h3>.*?<Legend content=\{\(props\) => renderCustomLegend\(props, cp\.fmt\)\} />\s*</PieChart>"

new_pie2 = """<h3 className="font-semibold text-slate-700 mb-4">Actual vs Budget ({cp.displayCurrency})</h3>
                <div className="h-64 sm:h-72 flex flex-col justify-center">
                  <ResponsiveContainer width="100%" height="80%">
                    <PieChart>
                      <Pie data={[
                        { name: 'Actual', value: Math.abs(hotelStats.totalRevenue), realValue: hotelStats.totalRevenue, fill: '#1B3A6B' },
                        { name: 'Budgeted', value: Math.abs(hotelStats.totalBudgetUsd), realValue: hotelStats.totalBudgetUsd, fill: '#C9A84C' },
                        { name: 'Variance', value: Math.abs(hotelStats.totalVarianceUsd), realValue: hotelStats.totalVarianceUsd, fill: hotelStats.totalVarianceUsd >= 0 ? '#10B981' : '#EF4444' }
                      ]} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={80} outerRadius={120} paddingAngle={2} label={false}>
                        { [1,2,3].map((_, i) => <Cell key={i} />) }
                      </Pie>
                      <Tooltip formatter={(val, name, props) => cp.fmt(props.payload.realValue)} />
                      <Legend content={(props) => renderCustomLegend(props, cp.fmt)} />
                    </PieChart>"""

code = re.sub(old_pie2, new_pie2, code, flags=re.DOTALL)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
