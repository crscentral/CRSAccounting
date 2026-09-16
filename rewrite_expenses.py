import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    code = f.read()

# Add recharts imports
if 'Recharts' not in code and 'PieChart' not in code:
    code = code.replace(
        "import ReportOptionsModal",
        "import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, Legend } from 'recharts'\nimport ReportOptionsModal"
    )

old_body = """  const totalExpenses = entries.reduce((s, r) => s + Number(r.amount_usd), 0)
  const byHead = {}
  entries.forEach(r => {
    const key = r.account?.name || 'Unknown'
    byHead[key] = (byHead[key] || 0) + Number(r.amount_usd)
  })
  const topHeads = Object.entries(byHead).sort((a, b) => b[1] - a[1]).slice(0, 3)

  return (
    <div>
      <PageHeader"""

new_body = """  const start = new Date(cp.range.from)
  const end = new Date(cp.range.to)
  const monthsInView = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth()) + 1
  const daysInView = Math.max(1, Math.round((end - start) / (1000 * 60 * 60 * 24)) + 1)
  const availableRoomNights = totalRooms * daysInView

  const amcMonthlyTotalUsd = amcContracts.reduce((s, r) => s + (Number(r.annual_amount_usd) / 12), 0)
  const amcTotalForView = amcMonthlyTotalUsd * monthsInView

  const entriesTotalUsd = entries.reduce((s, r) => s + Number(r.amount_usd), 0)
  const totalExpenses = entriesTotalUsd + amcTotalForView

  const byHead = { 'AMC Contracts (Amortized)': amcTotalForView }
  entries.forEach(r => {
    const key = r.account ? `${r.account.code} - ${r.account.name}` : 'Unknown'
    byHead[key] = (byHead[key] || 0) + Number(r.amount_usd)
  })
  
  const pieData = Object.entries(byHead).filter(x => x[1] > 0).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value)
  const COLORS = ['#1e293b', '#3b82f6', '#10b981', '#f59e0b', '#6366f1', '#ec4899', '#8b5cf6', '#14b8a6', '#f43f5e', '#64748b']

  return (
    <div>
      <PageHeader"""

code = code.replace(old_body, new_body)

# Replace the grid cards
old_grid = """      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Expenses" value={fmt(totalExpenses)} tone="blue" />
        {topHeads.map(([name, amount]) => (
          <KpiCard key={name} label={name} value={fmt(amount)} tone="slate" />
        ))}
      </div>"""
new_grid = """      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Expenses (View)" value={fmt(totalExpenses)} tone="blue" />
        <KpiCard label="Entries (View)" value={fmt(entriesTotalUsd)} tone="slate" />
        <KpiCard label="AMC Amortized (View)" value={fmt(amcTotalForView)} tone="slate" />
        <KpiCard label="AMC Annual Run-Rate" value={fmt(amcContracts.reduce((s, r) => s + Number(r.annual_amount_usd), 0))} tone="slate" />
      </div>

      <div className="grid lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Expense Breakdown (CPOR: {totalOccupied > 0 ? fmt(totalExpenses/totalOccupied) : '—'})</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={2}>
                  {pieData.map((e, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <RechartsTooltip formatter={(value) => fmt(value)} />
                <Legend layout="vertical" verticalAlign="middle" align="right" wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="text-sm font-semibold text-slate-800 mb-4">Expense Breakdown (PAR: {availableRoomNights > 0 ? fmt(totalExpenses/availableRoomNights) : '—'})</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}>
                  {pieData.map((e, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <RechartsTooltip formatter={(value) => fmt(value)} />
                <Legend layout="vertical" verticalAlign="middle" align="right" wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>"""
code = code.replace(old_grid, new_grid)

# Add footers to DataTable calls
# For Expense Entries
old_table1 = """      <DataTable
        title="Expense Entries"
        columns={["""
new_table1 = """      <div className="flex justify-between items-end mb-2 mt-8">
        <h3 className="font-semibold text-slate-800">Expense Entries</h3>
        <div className="text-sm text-slate-500 font-medium">
          Total Heads: {new Set(entries.map(e => e.account_id)).size} &bull; Total Amount: {fmt(entriesTotalUsd)}
        </div>
      </div>
      <DataTable
        columns={["""
code = code.replace(old_table1, new_table1)

old_table2 = """      <DataTable
        title="AMC Contracts (auto-split across 12 months)"
        columns={["""
new_table2 = """      <div className="flex justify-between items-end mb-2 mt-8">
        <h3 className="font-semibold text-slate-800">AMC Contracts (auto-split across 12 months)</h3>
        <div className="text-sm text-slate-500 font-medium">
          Total Contracts: {amcContracts.length} &bull; Annual: {fmt(amcContracts.reduce((s, r) => s + Number(r.annual_amount_usd), 0))} &bull; Monthly: {fmt(amcMonthlyTotalUsd)}
        </div>
      </div>
      <DataTable
        columns={["""
code = code.replace(old_table2, new_table2)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(code)
