with open('src/components/AppShell.jsx', 'r') as f:
    code = f.read()

code = code.replace(
    "'/hotel-budget',",
    "'/hotel-budget',\n    '/hotel-expense-budget',"
)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(code)
