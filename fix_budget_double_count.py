import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

old_inject = """            aMap[foodKey] = (aMap[foodKey] || 0) + (Number(r.food_amount_usd) || 0)
            aMap[bevKey] = (aMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
            aMap[otherKey] = (aMap[otherKey] || 0) + (Number(r.other_amount_usd) || 0)
            
          } else if (activeProduct === 'restaurant') {
            const foodKey = r.meal_period === 'Breakfast' ? `4016-${m}` : `4010-${m}`
            const bevKey = `4011-${m}`
            const otherKey = `4019-${m}`
            
            aMap[foodKey] = (aMap[foodKey] || 0) + (Number(r.food_amount_usd) || 0)
            aMap[bevKey] = (aMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
            aMap[otherKey] = (aMap[otherKey] || 0) + (Number(r.other_amount_usd) || 0)
          }"""

new_inject = """            aMap[foodKey] = (aMap[foodKey] || 0) + (Number(r.food_amount_usd) || 0)
            aMap[bevKey] = (aMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
            aMap[otherKey] = (aMap[otherKey] || 0) + (Number(r.other_amount_usd) || 0)
            
          }
          // Note: If activeProduct === 'restaurant', we do NOT inject restRev manually because 
          // those postings are already in ledger_entries and caught by ledgerQuery!"""

content = content.replace(old_inject, new_inject)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)

