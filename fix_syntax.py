import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    'sublabel="{activeProduct === "restaurant" ? "Food Sales Account" : "Room Revenue + Front Office"}"',
    'sublabel={activeProduct === "restaurant" ? "Food Sales Account" : "Room Revenue + Front Office"}'
)

content = content.replace(
    'sublabel="{activeProduct === "restaurant" ? "Beverage Sales Account" : "F&B Service Accounts"}"',
    'sublabel={activeProduct === "restaurant" ? "Beverage Sales Account" : "F&B Service Accounts"}'
)

content = content.replace(
    'label={`${startYear} {activeProduct === "restaurant" ? "Food Sales" : "Front Office Revenue"}`}',
    'label={`${startYear} ${activeProduct === "restaurant" ? "Food Sales" : "Front Office Revenue"}`}'
)

content = content.replace(
    'label={`${startYear} {activeProduct === "restaurant" ? "Beverage Sales" : "F&B Service Revenue"}`}',
    'label={`${startYear} ${activeProduct === "restaurant" ? "Beverage Sales" : "F&B Service Revenue"}`}'
)


with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
