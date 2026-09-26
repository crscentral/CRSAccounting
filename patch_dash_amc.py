with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

content = content.replace("expensesMade = directExpenses\n  } else {", "expensesMade = directExpenses + amcTotal\n  } else {")

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)
