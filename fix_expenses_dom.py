import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    code = f.read()

# I need to restore topHeads calculation
code = code.replace(
    "const COLORS = ['#1e293b', '#3b82f6', '#10b981', '#f59e0b', '#6366f1', '#ec4899', '#8b5cf6', '#14b8a6', '#f43f5e', '#64748b']",
    """const COLORS = ['#1e293b', '#3b82f6', '#10b981', '#f59e0b', '#6366f1', '#ec4899', '#8b5cf6', '#14b8a6', '#f43f5e', '#64748b']
  const topHeads = Object.entries(byHead).sort((a, b) => b[1] - a[1]).slice(0, 3)"""
)

# Now inject the pie charts BELOW the KPI cards.
old_grid = """      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Expenses" value={cp.fmt(totalExpenses)} tone="red" />
        {topHeads.map(([name, usd]) => <KpiCard key={name} label={name} value={cp.fmt(usd)} tone="slate" />)}
      </div>"""

new_grid = """      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Expenses" value={cp.fmt(totalExpenses)} tone="red" />
        {topHeads.map(([name, usd]) => <KpiCard key={name} label={name} value={cp.fmt(usd)} tone="slate" />)}
      </div>

      <div className="grid lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Expense Breakdown (CPOR: {totalOccupied > 0 ? cp.fmt(totalExpenses/totalOccupied) : '—'})</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={2}>
                  {pieData.map((e, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <RechartsTooltip formatter={(value) => cp.fmt(value)} />
                <Legend layout="vertical" verticalAlign="middle" align="right" wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Expense Breakdown (PAR: {availableRoomNights > 0 ? cp.fmt(totalExpenses/availableRoomNights) : '—'})</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}>
                  {pieData.map((e, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <RechartsTooltip formatter={(value) => cp.fmt(value)} />
                <Legend layout="vertical" verticalAlign="middle" align="right" wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>"""

code = code.replace(old_grid, new_grid)

# Now fix the footers
old_entries = """      <h3 className="font-semibold text-slate-700 mb-3 flex items-center justify-between">
        <span>Expense Entries</span>
        {can(['owner', 'admin', 'accountant']) && (
          <button onClick={() => setNewHeadModalOpen(true)} className="text-xs text-navy-600 hover:text-navy-800 font-medium">+ Add Expense Head</button>
        )}
      </h3>"""
new_entries = """      <div className="flex justify-between items-end mb-3 mt-8">
        <div>
          <h3 className="font-semibold text-slate-700 flex items-center gap-3">
            <span>Expense Entries</span>
            {can(['owner', 'admin', 'accountant']) && (
              <button onClick={() => setNewHeadModalOpen(true)} className="text-xs text-navy-600 hover:text-navy-800 font-medium">+ Add Expense Head</button>
            )}
          </h3>
        </div>
        <div className="text-sm text-slate-500 font-medium">
          Total Heads: {new Set(entries.map(e => e.account_id)).size} &bull; Total Amount: {cp.fmt(entriesTotalUsd)}
        </div>
      </div>"""
code = code.replace(old_entries, new_entries)


old_amc = """      <h3 className="font-semibold text-slate-700 mb-3 mt-10 flex items-center justify-between">
        <span>AMC Contracts (auto-split across 12 months)</span>
      </h3>"""
new_amc = """      <div className="flex justify-between items-end mb-3 mt-10">
        <h3 className="font-semibold text-slate-700">AMC Contracts (auto-split across 12 months)</h3>
        <div className="text-sm text-slate-500 font-medium">
          Total Contracts: {amcContracts.length} &bull; Annual: {cp.fmt(amcContracts.reduce((s, r) => s + Number(r.annual_amount_usd), 0))} &bull; Monthly: {cp.fmt(amcMonthlyTotalUsd)}
        </div>
      </div>"""
code = code.replace(old_amc, new_amc)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(code)
