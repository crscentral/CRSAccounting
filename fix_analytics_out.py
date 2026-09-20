import re

with open('src/pages/Analytics.jsx', 'r') as f:
    content = f.read()

old_out1 = """      outstanding = hgiSel.reduce((s2, i) => s2 + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)"""
new_out1 = """      outstanding = hgiSel.reduce((s2, i) => s2 + (Number(i.invoice_amount_usd) - Number(i.collected_amount_usd)), 0)
      outstanding += hrsSel.reduce((s2, i) => s2 + (Number(i.room_revenue_usd || 0) - Number(i.manual_room_revenue_collected_usd || 0)), 0)
      outstanding += hreSel.reduce((s2, i) => s2 + (Number(i.amount_usd || 0) - Number(i.collected_usd || i.amount_usd || 0)), 0)
      outstanding += rdrSel.reduce((s2, i) => s2 + ((Number(i.total_amount_usd) || (Number(i.food_amount_usd||0) + Number(i.beverage_amount_usd||0) + Number(i.other_amount_usd||0))) - Number(i.collected_usd || 0)), 0)"""

# Wait, `rdrSel`? Where is `rdrSel` defined in Analytics.jsx?
