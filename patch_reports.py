import re

with open('src/pages/Reports.jsx', 'r') as f:
    code = f.read()

# 1. Patch Row component
row_component = """function Row({ label, value, percent, bold, large }) {
  return (
    <div className={`flex items-center justify-between px-3 py-2 ${bold ? 'font-bold text-slate-800' : 'text-slate-600'} ${large ? 'text-lg py-3' : 'text-sm'}`}>
      <span>{label}</span>
      <div className="flex items-center justify-end">
        {percent && <span className="text-slate-400 text-xs w-16 text-right mr-3 font-normal">{percent}</span>}
        <span className="text-right min-w-[100px]">{value}</span>
      </div>
    </div>
  )
}"""

code = re.sub(
    r"function Row\(\{ label, value, bold, large \}\) \{.*?  \)\n\}",
    row_component,
    code,
    flags=re.DOTALL
)

# 2. Patch Revenue mapping
new_revenue = """                {byType('Revenue').map(a => {
                  const val = -(balances[a.id] || 0)
                  const pct = totalRevenue ? ((val / totalRevenue) * 100).toFixed(1) + '%' : '0.0%'
                  return <Row key={a.id} label={a.name} value={cp.fmt(val)} percent={pct} />
                })}
                <Row label="Total Revenue" value={cp.fmt(totalRevenue)} percent="100.0%" bold />"""

code = re.sub(
    r"                \{byType\('Revenue'\)\.map\(a => \(\n                  <Row key=\{a\.id\} label=\{a\.name\} value=\{cp\.fmt\(-\(balances\[a\.id\] \|\| 0\)\)\} />\n                \)\)\}\n                <Row label=\"Total Revenue\" value=\{cp\.fmt\(totalRevenue\)\} bold />",
    new_revenue,
    code
)

# 3. Patch Expenses mapping
new_expenses = """                {operatingAccounts.map(a => {
                  const val = balances[a.id] || 0
                  const pct = operatingExpenses ? ((val / operatingExpenses) * 100).toFixed(1) + '%' : '0.0%'
                  return <Row key={a.id} label={a.name} value={cp.fmt(val)} percent={pct} />
                })}
                <Row label="Total Operating Expenses" value={cp.fmt(operatingExpenses)} percent="100.0%" bold />"""

code = re.sub(
    r"                \{operatingAccounts\.map\(a => \(\n                  <Row key=\{a\.id\} label=\{a\.name\} value=\{cp\.fmt\(balances\[a\.id\] \|\| 0\)\} />\n                \)\)\}\n                <Row label=\"Total Operating Expenses\" value=\{cp\.fmt\(operatingExpenses\)\} bold />",
    new_expenses,
    code
)

with open('src/pages/Reports.jsx', 'w') as f:
    f.write(code)
