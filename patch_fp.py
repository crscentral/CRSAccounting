import re

with open('src/pages/FinancialPerformance.jsx', 'r') as f:
    content = f.read()

old_load = """  async function loadData() {
    const { data: accounts } = await supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    const { data: entries } = await supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd, entry_date, accounts!inner(type, subtype)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to)

    const balances = {}
    ;(entries || []).forEach(e => {
"""

new_load = """  async function loadData() {
    const { data: accounts } = await supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    const { data: entries } = await supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd, entry_date, accounts!inner(type, subtype)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to)

    let combined = entries || []
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      const roomRevAcc = (accounts || []).find(a => (a.name || '').toLowerCase().includes('room revenue'))
      const mainAcc = (accounts || []).find(a => (a.name || '').toLowerCase().includes('maintenance') || (a.name || '').toLowerCase().includes('repairs') || a.type === 'Expenses')
      const foodAcc = (accounts || []).find(a => (a.name || '').toLowerCase().includes('food') && a.type === 'Revenue') || roomRevAcc
      const bevAcc = (accounts || []).find(a => (a.name || '').toLowerCase().includes('beverage') && a.type === 'Revenue') || roomRevAcc
      const otherFbAcc = (accounts || []).find(a => (a.name || '').toLowerCase().includes('other') && a.type === 'Revenue') || roomRevAcc
      
      const [{ data: hrs }, { data: hre }, { data: hee }, { data: amc }, { data: rdr }] = await Promise.all([
        supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to),
        supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to),
        supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to),
        supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id),
        supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
      ])
      
      if (roomRevAcc) {
        ;(hrs || []).forEach(r => {
          if (Number(r.room_revenue_usd) > 0) combined.push({ account_id: roomRevAcc.id, debit_usd: 0, credit_usd: r.room_revenue_usd, entry_date: r.stat_date, accounts: { type: roomRevAcc.type, subtype: roomRevAcc.subtype } })
        })
      }
      
      ;(hre || []).forEach(r => {
        const a = (accounts || []).find(ac => ac.id === r.account_id)
        if (a && Number(r.amount_usd) > 0) combined.push({ account_id: a.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.entry_date, accounts: { type: a.type, subtype: a.subtype } })
      })
      
      ;(hee || []).forEach(r => {
        const a = (accounts || []).find(ac => ac.id === r.account_id)
        if (a && Number(r.amount_usd) > 0) combined.push({ account_id: a.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.expense_date, accounts: { type: a.type, subtype: a.subtype } })
      })
      
      if (mainAcc && amc && amc.length > 0) {
        const amcMonthly = amc.reduce((s, r) => s + (Number(r.annual_amount_usd)/12), 0)
        if (amcMonthly > 0) {
          const start = new Date(cp.range.from)
          const end = new Date(cp.range.to)
          let cur = new Date(start.getFullYear(), start.getMonth(), 1)
          while (cur <= end) {
            const dStr = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}-28`
            if (dStr >= cp.range.from && dStr <= cp.range.to) {
              combined.push({ account_id: mainAcc.id, debit_usd: amcMonthly, credit_usd: 0, entry_date: dStr, accounts: { type: mainAcc.type, subtype: mainAcc.subtype } })
            }
            cur.setMonth(cur.getMonth() + 1)
          }
        }
      }
      
      ;(rdr || []).forEach(r => {
        if (foodAcc && Number(r.food_amount_usd) > 0) combined.push({ account_id: foodAcc.id, debit_usd: 0, credit_usd: r.food_amount_usd, entry_date: r.revenue_date, accounts: { type: foodAcc.type, subtype: foodAcc.subtype } })
        if (bevAcc && Number(r.beverage_amount_usd) > 0) combined.push({ account_id: bevAcc.id, debit_usd: 0, credit_usd: r.beverage_amount_usd, entry_date: r.revenue_date, accounts: { type: bevAcc.type, subtype: bevAcc.subtype } })
        if (otherFbAcc && Number(r.other_amount_usd) > 0) combined.push({ account_id: otherFbAcc.id, debit_usd: 0, credit_usd: r.other_amount_usd, entry_date: r.revenue_date, accounts: { type: otherFbAcc.type, subtype: otherFbAcc.subtype } })
      })
    }

    const balances = {}
    ;(combined || []).forEach(e => {
"""

content = content.replace(old_load, new_load)

with open('src/pages/FinancialPerformance.jsx', 'w') as f:
    f.write(content)

