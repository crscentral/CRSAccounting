import re

def patch():
    with open('src/pages/Ledger.jsx', 'r') as f:
        content = f.read()

    # Find the hrs foreach block and comment it out
    # Pattern: ;(hrs || []).forEach(r => { ... })
    pattern = r";\(hrs \|\| \[\]\)\.forEach\(r => \{\n\s*const rev = Number\(r\.room_revenue_usd\) \|\| 0\n\s*const col = Number\(r\.manual_room_revenue_collected_usd\) \|\| rev\n\s*const uncol = Math\.max\(0, rev - col\)\n\s*if \(uncol > 0\) combined\.push\(\{ id: `hrs-ar-\$\{r\.id\}`, entry_date: r\.stat_date, description: 'Room Revenue Uncollected', currency: r\.currency \|\| 'USD', debit_usd: uncol, credit_usd: 0 \}\)\n\s*\}\)"
    
    content = re.sub(pattern, "// Disabled hotel_room_stats AR injection to prevent double counting with Guest Invoices", content)
    
    # Also fix restaurant uncol to support overcollection and not just max(0, ..)
    rdr_pattern = r"const uncol = Math\.max\(0, total - col\)\n\s*if \(uncol > 0\) combined\.push\(\{ id: `rdr-ar-\$\{r\.id\}`, entry_date: r\.revenue_date, description: `\$\{r\.meal_period\} F&B Uncollected`, currency: 'USD', debit_usd: uncol, credit_usd: 0 \}\)"
    
    rdr_repl = """const uncol = total - col
               if (uncol > 0) {
                 combined.push({ id: `rdr-ar-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Uncollected`, currency: 'USD', debit_usd: uncol, credit_usd: 0 })
               } else if (uncol < 0) {
                 combined.push({ id: `rdr-ar-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Overcollection`, currency: 'USD', debit_usd: 0, credit_usd: Math.abs(uncol) })
               }"""
    
    content = re.sub(rdr_pattern, rdr_repl, content)

    with open('src/pages/Ledger.jsx', 'w') as f:
        f.write(content)
        print("Patched successfully")

patch()
