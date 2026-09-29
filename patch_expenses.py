import re

with open('daily_block.txt', 'r') as f:
    daily = f.read()

with open('purchase_block.txt', 'r') as f:
    purchase = f.read()

# 1. Prepare Daily Block for Hotel
hotel_daily = daily.replace(
    "<span>Daily Expense Entries</span>", "<span>Hotel Daily Expense Entries</span>"
).replace(
    "{new Set(entries.map(e => e.account_id)).size}", "{new Set(hotelEntries.map(e => e.account_id)).size}"
).replace(
    "{cp.fmt(entriesTotalUsd)}", "{cp.fmt(hotelEntriesTotal)}"
).replace(
    "rows={entries}", "rows={hotelEntries}"
).replace(
    "AMC Contracts (auto-split across 12 months)", "Hotel AMC Contracts (auto-split across 12 months)"
).replace(
    "rows={amcContracts}", "rows={hotelAmc}"
)

# Strip out the {activeTab === 'daily' && ( <> and </> )} from the hotel version to make it easy to append restaurant
hotel_daily = hotel_daily.replace("{activeTab === 'daily' && (\n        <>\n", "")
hotel_daily = hotel_daily.replace("        </>\n      )\n\n      ", "")

# 2. Prepare Daily Block for Restaurant
# We take the hotel_daily and adapt it for restaurant
rest_daily = hotel_daily.replace(
    "Hotel Daily Expense Entries", "Restaurant Daily Expense Entries"
).replace(
    "hotelEntries", "restEntries"
).replace(
    "hotelEntriesTotal", "restEntriesTotal"
).replace(
    "Hotel AMC Contracts", "Restaurant AMC Contracts"
).replace(
    "hotelAmc", "restAmc"
).replace(
    "+ Add Expense Head", "" # Remove add expense head button for restaurant
).replace(
    "{can(['owner', 'admin', 'accountant']) && (\n              <button onClick={() => setNewHeadModalOpen(true)} className=\"text-xs text-navy-600 hover:text-navy-800 font-medium\"></button>\n            )}", ""
)

# Combine Daily
new_daily_block = f"""{{activeTab === 'daily' && (
        <>
{hotel_daily}
          {{(restEntries.length > 0 || restAmc.length > 0) && (
            <div className="mt-10 pt-8 border-t border-slate-200">
{rest_daily}
            </div>
          )}}
        </>
      )}}
"""

# 3. Prepare Purchase Block
hotel_purchase = purchase.replace(
    "Purchase Invoices", "Hotel Purchase Invoices"
).replace(
    "rows={purchaseInvoices}", "rows={hotelPI}"
)

hotel_purchase_inner = hotel_purchase.replace("{activeTab === 'purchase' && (\n        <div className=\"mt-4\">\n", "")
hotel_purchase_inner = hotel_purchase_inner.replace("        </div>\n      )", "")

rest_purchase = hotel_purchase_inner.replace(
    "Hotel Purchase Invoices", "Restaurant Purchase Invoices"
).replace(
    "hotelPI", "restPI"
)

new_purchase_block = f"""{{activeTab === 'purchase' && (
        <div className="mt-4">
{hotel_purchase_inner}
          {{restPI.length > 0 && (
            <div className="mt-10 pt-8 border-t border-slate-200">
{rest_purchase}
            </div>
          )}}
        </div>
      )}}"""

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

# Replace the blocks in the file
content = content.replace(daily, new_daily_block)
content = content.replace(purchase, new_purchase_block)

# Replace the total declarations
old_totals = "const entriesTotalUsd = entries.reduce((s, r) => s + Number(r.amount_usd), 0)"
new_totals = """const entriesTotalUsd = entries.reduce((s, r) => s + Number(r.amount_usd), 0)
  const hotelEntries = entries.filter(e => e.product === 'hotel')
  const restEntries = entries.filter(e => e.product === 'restaurant')
  const hotelAmc = amcContracts.filter(a => a.product === 'hotel')
  const restAmc = amcContracts.filter(a => a.product === 'restaurant')
  const hotelPI = purchaseInvoices.filter(p => p.product === 'hotel')
  const restPI = purchaseInvoices.filter(p => p.product === 'restaurant')
  
  const hotelEntriesTotal = hotelEntries.reduce((s, r) => s + Number(r.amount_usd), 0)
  const restEntriesTotal = restEntries.reduce((s, r) => s + Number(r.amount_usd), 0)"""

content = content.replace(old_totals, new_totals)

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)

print("Patch successful!")
