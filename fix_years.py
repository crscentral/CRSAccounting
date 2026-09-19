import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

content = content.replace("const years = [startYear, startYear + 1, startYear + 2, startYear + 3, startYear + 4]", "const years = [startYear]")
# Change the report modal too
content = content.replace("label: 'Starting Year (Includes Next 4 Years)',", "label: 'Select Year',")
content = content.replace("gte('budget_year', startYear).lte('budget_year', startYear + 4)", "eq('budget_year', startYear)")
content = content.replace("gte('stat_date', `${startYear}-01-01`).lte('stat_date', `${startYear + 4}-12-31`)", "gte('stat_date', `${startYear}-01-01`).lte('stat_date', `${startYear}-12-31`)")
content = content.replace("const years = [sy, sy + 1, sy + 2, sy + 3, sy + 4]", "const years = [sy]")
content = content.replace("${startYear}–${startYear + 4}", "${startYear}")

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
