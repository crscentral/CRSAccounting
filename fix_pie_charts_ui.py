import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Fix the first pie
old_pie1 = r'innerRadius=\{40\} outerRadius=\{100\} label=\{.*?\}'
new_pie1 = r'innerRadius={50} outerRadius={80} label={({ cx, cy, midAngle, innerRadius, outerRadius, realValue, name }) => { const RADIAN = Math.PI / 180; const radius = outerRadius + 30; const x = cx + radius * Math.cos(-midAngle * RADIAN); const y = cy + radius * Math.sin(-midAngle * RADIAN); return <text x={x} y={y} fill="#475569" textAnchor={x > cx ? "start" : "end"} dominantBaseline="central" fontSize={10}>{name}: {cp.fmt(realValue)}</text>; }}'
code = re.sub(old_pie1, new_pie1, code, count=1)

# Fix the second pie
old_pie2 = r'innerRadius=\{40\} outerRadius=\{100\} label=\{.*?\}'
new_pie2 = r'innerRadius={50} outerRadius={80} label={({ cx, cy, midAngle, innerRadius, outerRadius, realValue, name }) => { const RADIAN = Math.PI / 180; const radius = outerRadius + 30; const x = cx + radius * Math.cos(-midAngle * RADIAN); const y = cy + radius * Math.sin(-midAngle * RADIAN); return <text x={x} y={y} fill="#475569" textAnchor={x > cx ? "start" : "end"} dominantBaseline="central" fontSize={10}>{name}: {new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(realValue)}</text>; }}'
code = re.sub(old_pie2, new_pie2, code, count=1)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
