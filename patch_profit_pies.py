import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Replace generic profit pies
old_profit_pie = r"innerRadius=\{60\} outerRadius=\{80\} paddingAngle=\{2\} label=\{false\}"
new_profit_pie = r'innerRadius={40} outerRadius={90} paddingAngle={2} label={({ cx, cy, midAngle, innerRadius, outerRadius, value, name }) => { const RADIAN = Math.PI / 180; const radius = outerRadius + 20; const x = cx + radius * Math.cos(-midAngle * RADIAN); const y = cy + radius * Math.sin(-midAngle * RADIAN); return <text x={x} y={y} fill="#475569" textAnchor={x > cx ? "start" : "end"} dominantBaseline="central" fontSize={11}>{name}: {cp.fmt(value)}</text>; }}'
code = code.replace(old_profit_pie, new_profit_pie)

# Let's fix the second pie chart in the hotel stats (Actual vs Budget (USD)) to format correctly
# Actually, the second pie chart used `value` (which is in USD) and the label uses `cp.fmt(value)` which converts to local currency!
# If it's the USD chart, it should format as USD!
# I will just write a custom script to fix it.
