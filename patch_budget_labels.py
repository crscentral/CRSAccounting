import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    """<KpiCard label={`${startYear} ${activeProduct === "restaurant" ? "Food Sales" : "Front Office Revenue"}`}""",
    """<KpiCard label={`${startYear} ${activeProduct === "restaurant" ? "Food Sales Budget" : "Front Office Revenue Budget"}`}"""
)
content = content.replace(
    """<KpiCard label={`${startYear} ${activeProduct === "restaurant" ? "Beverage Sales" : "F&B Service Revenue"}`}""",
    """<KpiCard label={`${startYear} ${activeProduct === "restaurant" ? "Beverage Sales Budget" : "F&B Service Budget"}`}"""
)
content = content.replace(
    """<KpiCard label={`${startYear} Other Revenue`}""",
    """<KpiCard label={`${startYear} Other Revenue Budget`}"""
)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
