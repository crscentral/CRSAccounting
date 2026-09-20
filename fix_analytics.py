import re

with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

old_out_top = """    outstanding = hotelGuestInvoices.reduce((s, i) => s + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)"""
new_out_top = """    outstanding = hotelGuestInvoices.reduce((s, i) => s + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)
    outstanding += hotelRoomStats.reduce((s, r) => s + (Number(r.room_revenue_usd || 0) - Number(r.manual_room_revenue_collected_usd || 0)), 0)
    outstanding += hotelRevenueEntries.reduce((s, r) => s + (Number(r.amount_usd || 0) - Number(r.collected_usd || r.amount_usd || 0)), 0)
    outstanding += restaurantRevenue.reduce((s, r) => s + ((Number(r.total_amount_usd) || (Number(r.food_amount_usd||0) + Number(r.beverage_amount_usd||0) + Number(r.other_amount_usd||0))) - Number(r.collected_usd || 0)), 0)"""

content = content.replace(old_out_top, new_out_top)

# I should also fix the outstanding calculation in generateAnalyticsReport, but wait, `generateAnalyticsReport` doesn't fetch `restaurantRevenue` at all in `Analytics.jsx`!
# Let me look at generateAnalyticsReport.
