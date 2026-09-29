with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

content = content.replace("food_sales_usd", "food_amount_usd")
content = content.replace("beverage_sales_usd", "beverage_amount_usd")
content = content.replace("other_revenue_usd", "other_amount_usd")

with open('src/pages/Analytics.jsx', 'w') as f:
    f.write(content)
