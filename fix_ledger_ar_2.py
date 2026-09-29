import re

def patch():
    with open('src/pages/Ledger.jsx', 'r') as f:
        content = f.read()

    # 1. Main table
    old_1 = """          if (isAr) {
            ;(hrs || []).forEach(r => {
               const rev = Number(r.room_revenue_usd) || 0
               const col = Number(r.manual_room_revenue_collected_usd) || rev
               const uncol = Math.max(0, rev - col)
               if (uncol > 0) combined.push({ id: `hrs-ar-${r.id}`, entry_date: r.stat_date, description: 'Room Revenue Uncollected', currency: r.currency || 'USD', debit_usd: uncol, credit_usd: 0 })
            })
            ;(rdr || []).forEach(r => {
               const total = (Number(r.food_amount_usd)||0) + (Number(r.beverage_amount_usd)||0) + (Number(r.other_amount_usd)||0)
               const col = r.collected_usd !== null ? Number(r.collected_usd) : total
               const uncol = Math.max(0, total - col)
               if (uncol > 0) combined.push({ id: `rdr-ar-${r.id}`, entry_date: r.revenue_date, description: 'Restaurant Revenue Uncollected', currency: r.currency || 'USD', debit_usd: uncol, credit_usd: 0 })
            })
          }"""
          
    new_1 = """          if (isAr) {
            // Disabled hotel_room_stats AR injection to prevent double counting with Guest Invoices
            ;(rdr || []).forEach(r => {
               const total = (Number(r.food_amount_usd)||0) + (Number(r.beverage_amount_usd)||0) + (Number(r.other_amount_usd)||0)
               const col = r.collected_usd !== null ? Number(r.collected_usd) : total
               const uncol = total - col
               if (uncol > 0) {
                 combined.push({ id: `rdr-ar-${r.id}`, entry_date: r.revenue_date, description: 'Restaurant Revenue Uncollected', currency: r.currency || 'USD', debit_usd: uncol, credit_usd: 0 })
               } else if (uncol < 0) {
                 combined.push({ id: `rdr-ar-${r.id}`, entry_date: r.revenue_date, description: 'Restaurant Overcollection', currency: r.currency || 'USD', debit_usd: 0, credit_usd: Math.abs(uncol) })
               }
            })
          }"""
    
    if old_1 in content:
        content = content.replace(old_1, new_1)
        print("Patched 1")

    with open('src/pages/Ledger.jsx', 'w') as f:
        f.write(content)

patch()
