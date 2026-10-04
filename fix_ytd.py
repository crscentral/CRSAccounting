with open("src/pages/Dashboard.jsx", "r") as f:
    content = f.read()

replacement = """
    // Now calculate YTD directly from the raw records for accuracy
    ytdRevenue = 
      allHotelRoomStats.filter(r => r.stat_date >= ytdRange.from && r.stat_date <= ytdRange.to).reduce((s, r) => s + Number(r.room_revenue_usd || 0), 0) +
      allHotelRevenueEntries.filter(r => r.entry_date >= ytdRange.from && r.entry_date <= ytdRange.to).reduce((s, r) => s + Number(r.amount_usd || 0), 0) +
      allRestaurantRevenue.filter(r => r.revenue_date >= ytdRange.from && r.revenue_date <= ytdRange.to).reduce((s, r) => s + (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))), 0);
      
    ytdExpenses = 
      allHotelExpenseEntries.filter(r => r.expense_date >= ytdRange.from && r.expense_date <= ytdRange.to).reduce((s, r) => s + Number(r.amount_usd || 0), 0) +
      allHotelPurchaseInvoices.filter(r => r.invoice_date >= ytdRange.from && r.invoice_date <= ytdRange.to).reduce((s, r) => s + Number(r.amount_usd || 0), 0) +
      hotelAmc.reduce((s, r) => s + getAmcOverlapUsd(r, activeCompany.fiscal_year_start_month || 1, ytdRange.from, ytdRange.to), 0);
      
    // Calculate All-Time directly from raw records
    allTimeRevenue = 
      allHotelRoomStats.reduce((s, r) => s + Number(r.room_revenue_usd || 0), 0) +
      allHotelRevenueEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0) +
      allRestaurantRevenue.reduce((s, r) => s + (Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))), 0);
      
    const todayStr = new Date().toISOString().split('T')[0]
    allTimeExpenses = 
      allHotelExpenseEntries.reduce((s, r) => s + Number(r.amount_usd || 0), 0) +
      allHotelPurchaseInvoices.reduce((s, r) => s + Number(r.amount_usd || 0), 0) +
      hotelAmc.reduce((s, r) => s + getAmcOverlapUsd(r, activeCompany.fiscal_year_start_month || 1, '2000-01-01', todayStr), 0);
"""

import re
content = re.sub(
    r'    // Now calculate YTD from the map\s+ytdRevenue = Object\.values\(monthlyMap\)\.filter\([\s\S]*?allTimeExpenses = Object\.values\(monthlyMap\)\.reduce\(\(s, m\) => s \+ m\.Expenses, 0\)',
    replacement,
    content
)

with open("src/pages/Dashboard.jsx", "w") as f:
    f.write(content)
