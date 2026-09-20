import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# I need to fetch meal_period, other_amount_usd from restaurant_daily_revenue
old_query = "supabase.from('restaurant_daily_revenue').select('revenue_date, food_amount_usd, beverage_amount_usd')"
new_query = "supabase.from('restaurant_daily_revenue').select('revenue_date, meal_period, food_amount_usd, beverage_amount_usd, other_amount_usd')"
content = content.replace(old_query, new_query)

old_logic = """      // Inject Restaurant Table Revenue into Hotel F&B Revenue Actuals
      if (activeProduct === 'hotel' && restRev) {
        restRev.forEach(r => {
          const m = parseInt(r.revenue_date.split('-')[1], 10)
          // food_amount -> 4019 - Restaurant Revenue
          const foodKey = `4019-${m}`
          // beverage_amount -> 4011 - Beverage Revenue
          const bevKey = `4011-${m}`
          aMap[foodKey] = (aMap[foodKey] || 0) + (Number(r.food_amount_usd) || 0)
          aMap[bevKey] = (aMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
        })
      } else if (activeProduct === 'restaurant' && restRev) {
        // In restaurant, the main Food Sales (4010) is handled above. 
        // Beverage Sales is 4011. Other Operating Income is 4019.
        restRev.forEach(r => {
          const m = parseInt(r.revenue_date.split('-')[1], 10)
          const bevKey = `4011-${m}`
          aMap[bevKey] = (aMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
        })
      }"""

new_logic = """      // Dynamically Inject Restaurant Table Revenue based on activeProduct and Meal Period
      if (restRev) {
        restRev.forEach(r => {
          const m = parseInt(r.revenue_date.split('-')[1], 10)
          
          if (activeProduct === 'hotel') {
            const foodKey = r.meal_period === 'Breakfast' ? `4016-${m}` : `4011-${m}`
            const bevKey = `4020-${m}`
            const otherKey = `4021-${m}`
            
            aMap[foodKey] = (aMap[foodKey] || 0) + (Number(r.food_amount_usd) || 0)
            aMap[bevKey] = (aMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
            aMap[otherKey] = (aMap[otherKey] || 0) + (Number(r.other_amount_usd) || 0)
            
          } else if (activeProduct === 'restaurant') {
            const foodKey = r.meal_period === 'Breakfast' ? `4016-${m}` : `4010-${m}`
            const bevKey = `4011-${m}`
            const otherKey = `4019-${m}`
            
            aMap[foodKey] = (aMap[foodKey] || 0) + (Number(r.food_amount_usd) || 0)
            aMap[bevKey] = (aMap[bevKey] || 0) + (Number(r.beverage_amount_usd) || 0)
            aMap[otherKey] = (aMap[otherKey] || 0) + (Number(r.other_amount_usd) || 0)
          }
        })
      }"""

content = content.replace(old_logic, new_logic)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
