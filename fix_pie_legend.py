import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Add renderCustomLegend helper if not exists
if 'const renderCustomLegend' not in code:
    old_func = r"function Dashboard\(\) \{"
    new_func = """const renderCustomLegend = (props, formatter) => {
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

function Dashboard() {"""
    code = re.sub(old_func, new_func, code)

# Replace the first pie block entirely
old_pie1 = r"<h3 className=\"font-semibold text-slate-700 mb-4\">Actual vs Budget \(\{activeCompany\.currency\}\)</h3>.*?<Tooltip formatter=\{\(val, name, props\) => new Intl\.NumberFormat\('en-US', \{ style: 'currency', currency: activeCompany\.currency \}\)\.format\(props\.payload\.realValue\)\} />"
new_pie1 = """<h3 className="font-semibold text-slate-700 mb-4">Actual vs Budget (Budget Currency)</h3>
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
                </div>"""
code = re.sub(old_pie1, new_pie1, code, flags=re.DOTALL)

# Replace the second pie block entirely
old_pie2 = r"<h3 className=\"font-semibold text-slate-700 mb-4\">Actual vs Budget \(\{cp\.displayCurrency\}\)</h3>.*?<Tooltip formatter=\{\(val, name, props\) => cp\.fmt\(props\.payload\.realValue\)\} />"
new_pie2 = """<h3 className="font-semibold text-slate-700 mb-4">Actual vs Budget (Base Currency)</h3>
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
                      <Tooltip formatter={(val, name, props) => new Intl.NumberFormat('en-US', { style: 'currency', currency: activeCompany.currency || 'USD' }).format(props.payload.realValue)} />
                      <Legend content={(props) => renderCustomLegend(props, (v) => new Intl.NumberFormat('en-US', { style: 'currency', currency: activeCompany.currency || 'USD' }).format(v))} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>"""
code = re.sub(old_pie2, new_pie2, code, flags=re.DOTALL)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
