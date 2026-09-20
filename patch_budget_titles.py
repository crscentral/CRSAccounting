import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# Replace static terms
replacements = {
    'title="Room Revenue Budget"': 'title={activeProduct === "restaurant" ? "F&B Revenue Budget" : "Room Revenue Budget"}',
    'subtitle={`${activeCompany.name} • Feed any two of Occupancy % / ADR / Room Revenue — the third calculates automatically`}': 'subtitle={`${activeCompany.name} • Feed any two of Occupancy % / ${activeProduct === "restaurant" ? "Avg Check" : "ADR"} / ${activeProduct === "restaurant" ? "F&B Revenue" : "Room Revenue"} — the third calculates automatically`}',
    '>Room Inventory<': '>{activeProduct === "restaurant" ? "Seat Inventory" : "Room Inventory"}<',
    'Total rooms available': '{activeProduct === "restaurant" ? "Total seats available" : "Total rooms available"}',
    '{startYear} Front Office Revenue': '{startYear} {activeProduct === "restaurant" ? "Food Sales" : "Front Office Revenue"}',
    '{startYear} F&B Service Revenue': '{startYear} {activeProduct === "restaurant" ? "Beverage Sales" : "F&B Service Revenue"}',
    '{startYear} Other Revenue': '{startYear} Other Revenue',
    'Room Revenue + Front Office': '{activeProduct === "restaurant" ? "Food Sales Account" : "Room Revenue + Front Office"}',
    'F&B Service Accounts': '{activeProduct === "restaurant" ? "Beverage Sales Account" : "F&B Service Accounts"}',
    'Select year for Room & Ancillary Revenue': 'Select year for Revenue Budget',
    '{startYear} - Room Revenue with ADR & Occ% vs Actual': '{startYear} - {activeProduct === "restaurant" ? "F&B Revenue" : "Room Revenue"} with {activeProduct === "restaurant" ? "Avg Check" : "ADR"} & Occ% vs Actual',
    '>ADR<': '>{activeProduct === "restaurant" ? "Avg Check" : "ADR"}<',
    '>Rooms Occ.<': '>{activeProduct === "restaurant" ? "Covers" : "Rooms Occ."}<',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
