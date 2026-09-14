import re
with open('src/pages/Reports.jsx', 'r') as f:
    code = f.read()

# 1. Update Row
row_code = """function Row({ label, value, percent, bold, large, color }) {
  let textColor = bold ? 'font-bold text-slate-800' : 'text-slate-600'
  if (color) textColor = color

  return (
    <div className={`flex items-center justify-between px-3 py-2 ${textColor} ${large ? 'text-lg py-3' : 'text-sm'}`}>
      <span>{label}</span>
      <div className="flex items-center justify-end">
        {percent && <span className={`${color ? color : 'text-slate-400'} text-xs w-16 text-right mr-3 font-normal`}>{percent}</span>}
        <span className="text-right min-w-[100px]">{value}</span>
      </div>
    </div>
  )
}"""
code = re.sub(
    r"function Row\(\{ label, value, percent, bold, large \}\) \{.*?  \)\n\}",
    row_code,
    code,
    flags=re.DOTALL
)

# 2. Update GOP
gop_code = """            <Row label={`GOP/GOL (${gop >= 0 ? 'Gross Operating Profit' : 'Gross Operating Loss'})`} value={cp.fmt(gop)} percent={totalRevenue ? ((gop / totalRevenue) * 100).toFixed(1) + '%' : '0.0%'} bold large color={gop >= 0 ? 'text-emerald-600 font-bold' : 'text-red-600 font-bold'} />"""
code = re.sub(
    r"            <Row label=\{\`GOP/GOL \(\$\{gop >= 0 \? 'Gross Operating Profit' : 'Gross Operating Loss'\}\)\`\} value=\{cp\.fmt\(gop\)\} bold large />",
    gop_code,
    code
)

# 3. Update EBITDA
ebitda_code = """            <Row label="EBITDA" value={cp.fmt(ebitda)} percent={totalRevenue ? ((ebitda / totalRevenue) * 100).toFixed(1) + '%' : '0.0%'} bold large color={ebitda >= 0 ? 'text-emerald-600 font-bold' : 'text-red-600 font-bold'} />"""
code = re.sub(
    r"            <Row label=\"EBITDA\" value=\{cp\.fmt\(ebitda\)\} bold large />",
    ebitda_code,
    code
)

# 4. Update Net Income
net_income_code = """            <Row label="Net Income" value={cp.fmt(retainedEarnings)} percent={totalRevenue ? ((retainedEarnings / totalRevenue) * 100).toFixed(1) + '%' : '0.0%'} bold large color={retainedEarnings >= 0 ? 'text-emerald-600 font-bold' : 'text-red-600 font-bold'} />"""
code = re.sub(
    r"            <Row label=\"Net Income\" value=\{cp\.fmt\(retainedEarnings\)\} bold large />",
    net_income_code,
    code
)

with open('src/pages/Reports.jsx', 'w') as f:
    f.write(code)
