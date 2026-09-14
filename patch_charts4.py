import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

new_block = """      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 flex flex-col items-center">
          <h2 className="font-semibold text-slate-700 flex items-center gap-2 mb-4 self-start">
            <DollarSign size={18} /> Expected Profit Breakdown
          </h2>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={netProfit >= 0 ? [
                    { name: 'Revenue', value: cp.convert(totalBilled), color: '#10b981' },
                    { name: 'Expenses', value: cp.convert(totalExpenses), color: '#ef4444' },
                    { name: 'Profit', value: cp.convert(netProfit), color: '#3b82f6' }
                  ] : [
                    { name: 'Revenue', value: cp.convert(totalBilled), color: '#10b981' },
                    { name: 'Expenses', value: cp.convert(totalExpenses), color: '#ef4444' },
                    { name: 'Loss', value: cp.convert(Math.abs(netProfit)), color: '#f59e0b' }
                  ]}
                  cx="50%" cy="50%" innerRadius={80} outerRadius={120} paddingAngle={2} dataKey="value"
                >
                  {(netProfit >= 0 ? [1,2,3] : [1,2,3]).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={(netProfit >= 0 ? ['#10b981', '#ef4444', '#3b82f6'] : ['#10b981', '#ef4444', '#f59e0b'])[index]} />
                  ))}
                </Pie>
                <Tooltip 
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      // Base percentage on Total Revenue to show true margins
                      const totalRev = cp.convert(totalBilled) || 1;
                      const pct = ((data.value / totalRev) * 100).toFixed(1);
                      return (
                        <div className="bg-white border border-slate-200 p-2 shadow-lg rounded text-sm">
                          <p className="font-semibold" style={{ color: data.color }}>{data.name}</p>
                          <p>{cp.fmt(data.value)} ({pct}%)</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-x-6 gap-y-2 justify-center text-sm mt-2 text-slate-600 w-full">
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-emerald-500"></span> Revenue: {cp.fmt(totalBilled)}</div>
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-500"></span> Expenses: {cp.fmt(totalExpenses)}</div>
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: netProfit >= 0 ? '#3b82f6' : '#f59e0b'}}></span> {netProfit >= 0 ? 'Profit' : 'Loss'}: {cp.fmt(Math.abs(netProfit))}</div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 flex flex-col items-center">
          <h2 className="font-semibold text-slate-700 flex items-center gap-2 mb-4 self-start">
            <Receipt size={18} /> Actual Profit Breakdown
          </h2>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={actualProfit >= 0 ? [
                    { name: 'Collected', value: cp.convert(collected), color: '#10b981' },
                    { name: 'Made', value: cp.convert(expensesMade), color: '#f97316' },
                    { name: 'Profit', value: cp.convert(actualProfit), color: '#3b82f6' }
                  ] : [
                    { name: 'Collected', value: cp.convert(collected), color: '#10b981' },
                    { name: 'Made', value: cp.convert(expensesMade), color: '#f97316' },
                    { name: 'Loss', value: cp.convert(Math.abs(actualProfit)), color: '#f59e0b' }
                  ]}
                  cx="50%" cy="50%" innerRadius={80} outerRadius={120} paddingAngle={2} dataKey="value"
                >
                  {(actualProfit >= 0 ? [1,2,3] : [1,2,3]).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={(actualProfit >= 0 ? ['#10b981', '#f97316', '#3b82f6'] : ['#10b981', '#f97316', '#f59e0b'])[index]} />
                  ))}
                </Pie>
                <Tooltip 
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      const totalCol = cp.convert(collected) || 1;
                      const pct = ((data.value / totalCol) * 100).toFixed(1);
                      return (
                        <div className="bg-white border border-slate-200 p-2 shadow-lg rounded text-sm">
                          <p className="font-semibold" style={{ color: data.color }}>{data.name}</p>
                          <p>{cp.fmt(data.value)} ({pct}%)</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-x-6 gap-y-2 justify-center text-sm mt-2 text-slate-600 w-full">
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-emerald-500"></span> Collected: {cp.fmt(collected)}</div>
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-orange-500"></span> Made: {cp.fmt(expensesMade)}</div>
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full" style={{backgroundColor: actualProfit >= 0 ? '#3b82f6' : '#f59e0b'}}></span> {actualProfit >= 0 ? 'Profit' : 'Loss'}: {cp.fmt(Math.abs(actualProfit))}</div>
          </div>
        </div>
      </div>\n"""

# Regex replacement
code = re.sub(
    r'      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">.*?      {activeProduct === \'hotel\' && hotelStats && \(',
    new_block + "      {activeProduct === 'hotel' && hotelStats && (",
    code,
    flags=re.DOTALL
)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
