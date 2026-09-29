with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

# I will just remove the "try {" I added.
content = content.replace("try {\n    const start = new Date(cp.range.from)", "const start = new Date(cp.range.from)")

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)
