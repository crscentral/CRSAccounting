with open('src/pages/RestaurantRevenue.jsx', 'r') as f:
    content = f.read()

old_summary = """        ['Total Revenue', fmt(totalRevenue)],
        ['Total Covers', totalCovers],
        ['Average Revenue / Cover', totalCovers > 0 ? fmt(totalRevenue / totalCovers) : '—'],"""

new_summary = """        ['Total Revenue', fmt(totalRevenue)],
        ['Total Covers', totalCovers],
        ['Average Revenue / Cover', totalCovers > 0 ? fmt(totalRevenue / totalCovers) : '—'],
        ['Food Revenue', fmt(rows.reduce((s, r) => s + Number(r.food_amount_usd), 0))],
        ['Beverage Revenue', fmt(rows.reduce((s, r) => s + Number(r.beverage_amount_usd), 0))],
        ['Other Revenue', fmt(rows.reduce((s, r) => s + Number(r.other_amount_usd), 0))],"""

content = content.replace(old_summary, new_summary)

with open('src/pages/RestaurantRevenue.jsx', 'w') as f:
    f.write(content)
