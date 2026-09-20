import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    """subtitle={`${activeCompany.name} • Feed any two of Occupancy % / ${activeProduct === "restaurant" ? "Avg Check" : "ADR"} / ${activeProduct === "restaurant" ? "F&B Revenue" : "Room Revenue"} — the third calculates automatically`}""",
    """subtitle={`${activeCompany.name} • ${activeProduct === "restaurant" ? "Manage your Monthly Budgets for Food, Beverage, and Other Revenue." : "Feed any two of Occupancy % / ADR / Room Revenue — the third calculates automatically"}`}"""
)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
