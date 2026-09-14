import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# I will find the entire grid grid-cols-1 md:grid-cols-2 block and replace it
# There are two of them now. I'll replace everything between `<div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">` and `{activeProduct === 'hotel' && hotelStats && (`

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
                    { name: 'Total Expenses', value: cp.convert(totalExpenses), color: '#ef4444' },
                    { name: 'Expected Net Profit', value: cp.convert(netProfit), color: '#10b981' }
                  ] : [
                    { name: 'Total Revenue', value: cp.convert(totalBilled), color: '#10b981' },
                    { name: 'Expected Net Loss', value: cp.convert(Math.abs(netProfit)), color: '#ef4444' }
                  ]}
                  cx="50%" cy="50%" innerRadius={80} outerRadius={120} paddingAngle={2} dataKey="value"
                >
                  {(netProfit >= 0 ? [1,2] : [1,2]).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={(netProfit >= 0 ? ['#ef4444', '#10b981'] : ['#10b981', '#ef4444'])[index]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => cp.fmt(v)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-x-6 gap-y-2 justify-center text-sm mt-2 text-slate-600 w-full">
             <div className="flex items-center gap-2 font-medium text-slate-800"><span className="w-3 h-3 rounded-full bg-emerald-500"></span> Revenue: {cp.fmt(totalBilled)}</div>
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-500"></span> Expenses: {cp.fmt(totalExpenses)}</div>
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-emerald-500"></span> Profit: {cp.fmt(netProfit)}</div>
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
                    { name: 'Total Expenses Made', value: cp.convert(expensesMade), color: '#f97316' },
                    { name: 'Actual Profit', value: cp.convert(actualProfit), color: '#10b981' }
                  ] : [
                    { name: 'Total Collected', value: cp.convert(collected), color: '#eab308' },
                    { name: 'Actual Loss', value: cp.convert(Math.abs(actualProfit)), color: '#ef4444' }
                  ]}
                  cx="50%" cy="50%" innerRadius={80} outerRadius={120} paddingAngle={2} dataKey="value"
                >
                  {(actualProfit >= 0 ? [1,2] : [1,2]).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={(actualProfit >= 0 ? ['#f97316', '#10b981'] : ['#eab308', '#ef4444'])[index]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => cp.fmt(v)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-x-6 gap-y-2 justify-center text-sm mt-2 text-slate-600 w-full">
             <div className="flex items-center gap-2 font-medium text-slate-800"><span className="w-3 h-3 rounded-full bg-yellow-500"></span> Collected: {cp.fmt(collected)}</div>
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-orange-500"></span> Made: {cp.fmt(expensesMade)}</div>
             <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-emerald-500"></span> Profit: {cp.fmt(actualProfit)}</div>
          </div>
        </div>
      </div>\n\n"""

# Regex: from <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6"> up to {activeProduct === 'hotel'
code = re.sub(
    r'      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">.*?      {activeProduct === \'hotel\' && hotelStats && \(',
    new_block + "      {activeProduct === 'hotel' && hotelStats && (",
    code,
    flags=re.DOTALL
)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
