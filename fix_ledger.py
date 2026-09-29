with open('src/pages/Ledger.jsx', 'r') as f:
    content = f.read()

# I will add basic accounting sources to ignoredSources for hotel/restaurant
target = "const ignoredSources = ['restaurant_revenue', 'hotel_room_stats', 'hotel_revenue_entry', 'hotel_expense_entry', 'hotel_amc_contract', 'hotel_guest_invoice', 'owner_contribution', 'owner_dividend', 'loan_taken', 'loan_principal']"
replacement = "const ignoredSources = ['restaurant_revenue', 'hotel_room_stats', 'hotel_revenue_entry', 'hotel_expense_entry', 'hotel_amc_contract', 'hotel_guest_invoice', 'owner_contribution', 'owner_dividend', 'loan_taken', 'loan_principal', 'sales_invoice', 'purchase_invoice', 'payment_receipt']"

if target in content:
    content = content.replace(target, replacement)
else:
    print("Not found")

with open('src/pages/Ledger.jsx', 'w') as f:
    f.write(content)
