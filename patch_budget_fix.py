with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

content = content.replace("        ])\n      }\n    }))\n    const sections", "        ])\n      }\n    })\n    const sections")

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
