import re

with open('src/pages/Reports.jsx', 'r') as f:
    content = f.read()

old_load_data = """    const { data: entries } = await supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd, entry_date, accounts!inner(type)').eq('company_id', activeCompany.id).eq('product', activeProduct)
    const bal = {}
    ;(entries || []).forEach(e => {"""

new_load_data = """    const { data: entries } = await supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd, entry_date, accounts!inner(type)').eq('company_id', activeCompany.id).eq('product', activeProduct)
    
    let combined = entries || []
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      const roomRevAcc = accs.find(a => a.name.toLowerCase().includes('room revenue'))
      const arAcc = accs.find(a => a.name.toLowerCase().includes('accounts receivable') || a.name.toLowerCase().includes('guest ledger'))
      const cashAcc = accs.find(a => a.name.toLowerCase().includes('cash on hand') || a.name.toLowerCase().includes('cash'))
      const mainAcc = accs.find(a => a.name.toLowerCase().includes('maintenance') || a.name.toLowerCase().includes('repairs') || a.type === 'Expenses')
      const foodAcc = accs.find(a => a.name.toLowerCase().includes('food') && a.type === 'Revenue') || roomRevAcc
      const bevAcc = accs.find(a => a.name.toLowerCase().includes('beverage') && a.type === 'Revenue') || roomRevAcc
      const otherFbAcc = accs.find(a => a.name.toLowerCase().includes('other') && a.type === 'Revenue') || roomRevAcc
      
      const [{ data: hrs }, { data: hre }, { data: hee }, { data: amc }, { data: rdr }, { data: hgi }] = await Promise.all([
        supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id),
        supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id),
        supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id),
        supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id),
        supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id),
        supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id)
      ])
      
      if (roomRevAcc) {
        ;(hrs || []).forEach(r => {
          if (Number(r.room_revenue_usd) > 0) combined.push({ account_id: roomRevAcc.id, debit_usd: 0, credit_usd: r.room_revenue_usd, entry_date: r.stat_date, accounts: { type: roomRevAcc.type } })
        })
      }
      
      ;(hre || []).forEach(r => {
        const a = accs.find(ac => ac.id === r.account_id)
        if (a && Number(r.amount_usd) > 0) combined.push({ account_id: a.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.entry_date, accounts: { type: a.type } })
      })
      
      ;(hee || []).forEach(r => {
        const a = accs.find(ac => ac.id === r.account_id)
        if (a && Number(r.amount_usd) > 0) combined.push({ account_id: a.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.expense_date, accounts: { type: a.type } })
      })
      
      if (mainAcc && amc && amc.length > 0) {
        const amcMonthly = amc.reduce((s, r) => s + (Number(r.annual_amount_usd)/12), 0)
        if (amcMonthly > 0) {
          const start = new Date(cp.range.from < '2020-01-01' ? '2020-01-01' : cp.range.from)
          const end = new Date(cp.range.to)
          let cur = new Date(start.getFullYear(), start.getMonth(), 1)
          while (cur <= end) {
            const dStr = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}-28`
            combined.push({ account_id: mainAcc.id, debit_usd: amcMonthly, credit_usd: 0, entry_date: dStr, accounts: { type: mainAcc.type } })
            cur.setMonth(cur.getMonth() + 1)
          }
        }
      }
      
      ;(rdr || []).forEach(r => {
        if (foodAcc && Number(r.food_amount_usd) > 0) combined.push({ account_id: foodAcc.id, debit_usd: 0, credit_usd: r.food_amount_usd, entry_date: r.revenue_date, accounts: { type: foodAcc.type } })
        if (bevAcc && Number(r.beverage_amount_usd) > 0) combined.push({ account_id: bevAcc.id, debit_usd: 0, credit_usd: r.beverage_amount_usd, entry_date: r.revenue_date, accounts: { type: bevAcc.type } })
        if (otherFbAcc && Number(r.other_amount_usd) > 0) combined.push({ account_id: otherFbAcc.id, debit_usd: 0, credit_usd: r.other_amount_usd, entry_date: r.revenue_date, accounts: { type: otherFbAcc.type } })
      })
      
      if (arAcc) {
        ;(hgi || []).forEach(r => {
          const inv = Number(r.invoice_amount_usd) || 0
          const col = Number(r.collected_amount_usd) || 0
          if (inv > 0) combined.push({ account_id: arAcc.id, debit_usd: inv, credit_usd: 0, entry_date: r.invoice_date, accounts: { type: arAcc.type } })
          if (col > 0) combined.push({ account_id: arAcc.id, debit_usd: 0, credit_usd: col, entry_date: r.invoice_date, accounts: { type: arAcc.type } })
          if (cashAcc && col > 0) combined.push({ account_id: cashAcc.id, debit_usd: col, credit_usd: 0, entry_date: r.invoice_date, accounts: { type: cashAcc.type } })
        })
      }
    }
    
    const bal = {}
    ;(combined || []).forEach(e => {"""

content = content.replace(old_load_data, new_load_data)


old_generate = """    const { data: entries } = await supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd, entry_date, accounts!inner(type)').eq('company_id', activeCompany.id).eq('product', activeProduct)
    const bal = {}
    ;(entries || []).forEach(e => {"""

new_generate = """    const { data: entries } = await supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd, entry_date, accounts!inner(type)').eq('company_id', activeCompany.id).eq('product', activeProduct)
    
    let combined = entries || []
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      const roomRevAcc = accounts.find(a => a.name.toLowerCase().includes('room revenue'))
      const arAcc = accounts.find(a => a.name.toLowerCase().includes('accounts receivable') || a.name.toLowerCase().includes('guest ledger'))
      const cashAcc = accounts.find(a => a.name.toLowerCase().includes('cash on hand') || a.name.toLowerCase().includes('cash'))
      const mainAcc = accounts.find(a => a.name.toLowerCase().includes('maintenance') || a.name.toLowerCase().includes('repairs') || a.type === 'Expenses')
      const foodAcc = accounts.find(a => a.name.toLowerCase().includes('food') && a.type === 'Revenue') || roomRevAcc
      const bevAcc = accounts.find(a => a.name.toLowerCase().includes('beverage') && a.type === 'Revenue') || roomRevAcc
      const otherFbAcc = accounts.find(a => a.name.toLowerCase().includes('other') && a.type === 'Revenue') || roomRevAcc
      
      const [{ data: hrs }, { data: hre }, { data: hee }, { data: amc }, { data: rdr }, { data: hgi }] = await Promise.all([
        supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id),
        supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id),
        supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id),
        supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id),
        supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id),
        supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id)
      ])
      
      if (roomRevAcc) {
        ;(hrs || []).forEach(r => {
          if (Number(r.room_revenue_usd) > 0) combined.push({ account_id: roomRevAcc.id, debit_usd: 0, credit_usd: r.room_revenue_usd, entry_date: r.stat_date, accounts: { type: roomRevAcc.type } })
        })
      }
      
      ;(hre || []).forEach(r => {
        const a = accounts.find(ac => ac.id === r.account_id)
        if (a && Number(r.amount_usd) > 0) combined.push({ account_id: a.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.entry_date, accounts: { type: a.type } })
      })
      
      ;(hee || []).forEach(r => {
        const a = accounts.find(ac => ac.id === r.account_id)
        if (a && Number(r.amount_usd) > 0) combined.push({ account_id: a.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.expense_date, accounts: { type: a.type } })
      })
      
      if (mainAcc && amc && amc.length > 0) {
        const amcMonthly = amc.reduce((s, r) => s + (Number(r.annual_amount_usd)/12), 0)
        if (amcMonthly > 0) {
          const start = new Date(range.from < '2020-01-01' ? '2020-01-01' : range.from)
          const end = new Date(range.to)
          let cur = new Date(start.getFullYear(), start.getMonth(), 1)
          while (cur <= end) {
            const dStr = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}-28`
            combined.push({ account_id: mainAcc.id, debit_usd: amcMonthly, credit_usd: 0, entry_date: dStr, accounts: { type: mainAcc.type } })
            cur.setMonth(cur.getMonth() + 1)
          }
        }
      }
      
      ;(rdr || []).forEach(r => {
        if (foodAcc && Number(r.food_amount_usd) > 0) combined.push({ account_id: foodAcc.id, debit_usd: 0, credit_usd: r.food_amount_usd, entry_date: r.revenue_date, accounts: { type: foodAcc.type } })
        if (bevAcc && Number(r.beverage_amount_usd) > 0) combined.push({ account_id: bevAcc.id, debit_usd: 0, credit_usd: r.beverage_amount_usd, entry_date: r.revenue_date, accounts: { type: bevAcc.type } })
        if (otherFbAcc && Number(r.other_amount_usd) > 0) combined.push({ account_id: otherFbAcc.id, debit_usd: 0, credit_usd: r.other_amount_usd, entry_date: r.revenue_date, accounts: { type: otherFbAcc.type } })
      })
      
      if (arAcc) {
        ;(hgi || []).forEach(r => {
          const inv = Number(r.invoice_amount_usd) || 0
          const col = Number(r.collected_amount_usd) || 0
          if (inv > 0) combined.push({ account_id: arAcc.id, debit_usd: inv, credit_usd: 0, entry_date: r.invoice_date, accounts: { type: arAcc.type } })
          if (col > 0) combined.push({ account_id: arAcc.id, debit_usd: 0, credit_usd: col, entry_date: r.invoice_date, accounts: { type: arAcc.type } })
          if (cashAcc && col > 0) combined.push({ account_id: cashAcc.id, debit_usd: col, credit_usd: 0, entry_date: r.invoice_date, accounts: { type: cashAcc.type } })
        })
      }
    }

    const bal = {}
    ;(combined || []).forEach(e => {"""

content = content.replace(old_generate, new_generate)

with open('src/pages/Reports.jsx', 'w') as f:
    f.write(content)

