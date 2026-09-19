import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# 1. Clamp daysInView
old_days = "const daysInView = Math.max(1, Math.round((new Date(cp.range.to) - new Date(cp.range.from)) / (1000 * 60 * 60 * 24)) + 1)"
new_days = "const daysInView = Math.max(1, Math.round((Math.min(new Date(cp.range.to).getTime(), new Date().getTime()) - new Date(cp.range.from).getTime()) / (1000 * 60 * 60 * 24)) + 1)"
code = code.replace(old_days, new_days)

# 2. Clamp endDate for trend chart and totalBudgetUsd
old_end = "const endDate = new Date(cp.range.to)"
new_end = "const endDate = new Date(Math.min(new Date(cp.range.to).getTime(), new Date().getTime()))"
code = code.replace(old_end, new_end)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
