import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# I already hid the top table in fix_hotel_budget.py!
# But let me check if it's hidden properly.
# The middle table is currently:
# {activeProduct === 'restaurant' ? `${startYear} - F&B Revenue & Actual` : `${startYear} - Other Revenue vs Actuals`}
# If I do this, the user gets exactly what they want: The middle table is renamed to F&B Revenue & Actual.
# Wait, they explicitly said "2026 - Other Revenue vs Actuals - this is not needed at all - Delete this completely".
# If they see the middle table renamed to F&B Revenue & Actual, they might still think "Wait, where is the table where I can input Daily Budget?"
