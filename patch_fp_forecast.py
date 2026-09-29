with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

old_prop = "canEdit={can(['owner', 'admin', 'accountant'])}"
new_prop = "canEdit={can(['owner', 'admin', 'accountant']) && activeProduct === 'basic'}"

content = content.replace(old_prop, new_prop)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)
