import re

with open('src/pages/Ledger.jsx', 'r') as f:
    content = f.read()

# First, modify loadData
block_to_add1 = """        
        // CASH & AR INJECTION (Hotel/Restaurant specific)
        const isCash = (selectedAccount.name || '').toLowerCase().includes('cash on hand') || (selectedAccount.name || '').toLowerCase().includes('cash')
        const isAr = (selectedAccount.name || '').toLowerCase().includes('accounts receivable') || (selectedAccount.name || '').toLowerCase().includes('guest ledger')
        
        if (isCash || isAr) {
          const [{ data: hrs }, { data: rdr }, { data: hre }, { data: hee }, { data: amc }, { data: hgi }] = await Promise.all([
            supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to),
            supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to),
            supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
            supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to),
            supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
            supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
          ])
          
          if (isCash) {
            ;(hrs || []).forEach(r => {
               const col = Number(r.manual_room_revenue_collected_usd) || Number(r.room_revenue_usd) || 0
               if (col > 0) combined.push({ id: `hrs-c-${r.id}`, entry_date: r.stat_date, description: 'Room Revenue Collected', currency: r.currency || 'USD', debit_usd: col, credit_usd: 0 })
            })
            ;(rdr || []).forEach(r => {
               const total = (Number(r.food_amount_usd)||0) + (Number(r.beverage_amount_usd)||0) + (Number(r.other_amount_usd)||0)
               const col = r.collected_usd !== null ? Number(r.collected_usd) : total
               if (col > 0) combined.push({ id: `rdr-c-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Collected`, currency: 'USD', debit_usd: col, credit_usd: 0 })
            })
            ;(hre || []).forEach(r => {
               const col = Number(r.collected_usd) || Number(r.amount_usd) || 0
               if (col > 0) combined.push({ id: `hre-c-${r.id}`, entry_date: r.entry_date, description: r.notes || 'Ancillary Collected', currency: r.currency || 'USD', debit_usd: col, credit_usd: 0 })
            })
            ;(hee || []).forEach(r => {
               const amt = Number(r.amount_usd) || 0
               if (amt > 0) combined.push({ id: `hee-c-${r.id}`, entry_date: r.expense_date, description: r.notes || 'Expense Paid', currency: r.currency || 'USD', debit_usd: 0, credit_usd: amt })
            })
            if (amc && amc.length > 0) {
              const amcMonthly = amc.reduce((s, r) => s + (Number(r.annual_amount_usd)/12), 0)
              if (amcMonthly > 0) {
                const start = new Date(cp.range.from < '2020-01-01' ? '2020-01-01' : cp.range.from)
                const end = new Date(cp.range.to)
                let cur = new Date(start.getFullYear(), start.getMonth(), 1)
                while (cur <= end) {
                  const dStr = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}-28`
                  combined.push({ id: `amc-c-${dStr}`, entry_date: dStr, description: 'AMC Monthly Amortization', currency: 'USD', debit_usd: 0, credit_usd: amcMonthly })
                  cur.setMonth(cur.getMonth() + 1)
                }
              }
            }
            ;(hgi || []).forEach(r => {
               const col = Number(r.collected_amount_usd) || 0
               if (col > 0) combined.push({ id: `hgi-c-${r.id}`, entry_date: r.invoice_date, description: `Invoice Collected: ${(r.invoice_number||'').substring(0,8)}`, currency: r.currency || 'USD', debit_usd: col, credit_usd: 0 })
            })
          }
          
          if (isAr) {
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
               if (uncol > 0) combined.push({ id: `rdr-ar-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Uncollected`, currency: 'USD', debit_usd: uncol, credit_usd: 0 })
            })
            ;(hre || []).forEach(r => {
               const rev = Number(r.amount_usd) || 0
               const col = Number(r.collected_usd) || rev
               const uncol = Math.max(0, rev - col)
               if (uncol > 0) combined.push({ id: `hre-ar-${r.id}`, entry_date: r.entry_date, description: r.notes || 'Ancillary Uncollected', currency: r.currency || 'USD', debit_usd: uncol, credit_usd: 0 })
            })
            // hgi is already partially handled by the block above it, but we can safely remove the old hgi block and rely entirely on this new AR block!
            // Wait, I will just let the old hgi block stay, but modify my new AR block to NOT include hgi, to avoid double counting!
            // Actually, the old hgi block does: debit_usd: i.invoice_amount_usd, credit_usd: 0 (for invoice). And credit_usd: i.collected_amount_usd (for collection).
            // That is mathematically perfect for AR! So we skip hgi here.
          }
        }
"""

old_hgi = """        // Guest Invoices (Accounts Receivable) - AR is typically an Asset account. 
        if ((selectedAccount.name || '').toLowerCase().includes('accounts receivable') || (selectedAccount.name || '').toLowerCase().includes('guest ledger')) {
          const { data: hgi } = await supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
          ;(hgi || []).forEach(i => {
            if (Number(i.invoice_amount_usd) > 0) {
              combined.push({ id: `hgi-inv-${i.id}`, entry_date: i.invoice_date, description: `Invoice ${(i.invoice_number || '').substring(0,8)} - ${i.guest_name}`, currency: i.currency || 'USD', debit_usd: i.invoice_amount_usd, credit_usd: 0 })
            }
            if (Number(i.collected_amount_usd) > 0) {
              combined.push({ id: `hgi-col-${i.id}`, entry_date: i.invoice_date, description: `Payment Collected - ${(i.invoice_number || '').substring(0,8)}`, currency: i.currency || 'USD', debit_usd: 0, credit_usd: i.collected_amount_usd })
            }
          })
        }"""

# I will replace the old_hgi block with old_hgi + block_to_add1
content = content.replace(old_hgi, old_hgi + block_to_add1)

# Now, do the exact same thing for generateLedgerReport
block_to_add2 = block_to_add1.replace('selectedAccount', 'account').replace('cp.range.from', 'range.from').replace('cp.range.to', 'range.to')

old_hgi_2 = """      if ((account.name || '').toLowerCase().includes('accounts receivable') || (account.name || '').toLowerCase().includes('guest ledger')) {
        const { data: hgi } = await supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
        ;(hgi || []).forEach(i => {
          if (Number(i.invoice_amount_usd) > 0) {
            combined.push({ id: `hgi-inv-${i.id}`, entry_date: i.invoice_date, description: `Invoice ${(i.invoice_number || '').substring(0,8)} - ${i.guest_name}`, currency: i.currency || 'USD', debit_usd: i.invoice_amount_usd, credit_usd: 0 })
          }
          if (Number(i.collected_amount_usd) > 0) {
            combined.push({ id: `hgi-col-${i.id}`, entry_date: i.invoice_date, description: `Payment Collected - ${(i.invoice_number || '').substring(0,8)}`, currency: i.currency || 'USD', debit_usd: 0, credit_usd: i.collected_amount_usd })
          }
        })
      }"""

content = content.replace(old_hgi_2, old_hgi_2 + block_to_add2)

with open('src/pages/Ledger.jsx', 'w') as f:
    f.write(content)
