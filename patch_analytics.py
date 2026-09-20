import re

def fix_active_product(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # 1. Replace activeProduct === 'hotel' with ['hotel', 'restaurant'].includes(activeProduct)
    content = content.replace("activeProduct === 'hotel'", "['hotel', 'restaurant'].includes(activeProduct)")
    content = content.replace("activeProduct === 'hotel' \n    ?", "['hotel', 'restaurant'].includes(activeProduct) \n    ?")
    
    # But wait, in Transactions.jsx, I need to fetch restaurant_daily_revenue!
    
    with open(filepath, 'w') as f:
        f.write(content)

fix_active_product('src/pages/Analytics.jsx')
fix_active_product('src/pages/Transactions.jsx')
