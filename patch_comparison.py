import re

with open('src/pages/Comparison.jsx', 'r') as f:
    content = f.read()

old_compute = """  async function computeMetrics(range) {
    const { data: accounts } = await supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    const { data: entries } = await supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd, entry_date')
      .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to)

    const balances = {}
    ;(entries || []).forEach(e => { balances[e.account_id] = (balances[e.account_id] || 0) + Number(e.debit_usd) - Number(e.credit_usd) })"""

new_compute = """  async function computeMetrics(range) {
    const { data: accounts } = await supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct)
    const { data: entries } = await supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd, entry_date')
      .eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', range.from).lte('entry_date', range.to)

    let combined = entries || []
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      const roomRevAcc = accounts.find(a => a.name.toLowerCase().includes('room revenue'))
      const mainAcc = accounts.find(a => a.name.toLowerCase().includes('maintenance') || a.name.toLowerCase().includes('repairs') || a.type === 'Expenses')
      const foodAcc = accounts.find(a => a.name.toLowerCase().includes('food') && a.type === 'Revenue') || roomRevAcc
      const bevAcc = accounts.find(a => a.name.toLowerCase().includes('beverage') && a.type === 'Revenue') || roomRevAcc
      const otherFbAcc = accounts.find(a => a.name.toLowerCase().includes('other') && a.type === 'Revenue') || roomRevAcc
      
      const [{ data: hrs }, { data: hre }, { data: hee }, { data: amc }, { data: rdr }] = await Promise.all([
        supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).gte('stat_date', range.from).lte('stat_date', range.to),
        supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).gte('entry_date', range.from).lte('entry_date', range.to),
        supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).gte('expense_date', range.from).lte('expense_date', range.to),
        supabase.from('hotel_amc_contracts').select('*').eq('company_id', activeCompany.id),
        supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to)
      ])
      
      if (roomRevAcc) {
        ;(hrs || []).forEach(r => {
          if (Number(r.room_revenue_usd) > 0) combined.push({ account_id: roomRevAcc.id, debit_usd: 0, credit_usd: r.room_revenue_usd, entry_date: r.stat_date })
        })
      }
      
      ;(hre || []).forEach(r => {
        if (Number(r.amount_usd) > 0) combined.push({ account_id: r.account_id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.entry_date })
      })
      
      ;(hee || []).forEach(r => {
        if (Number(r.amount_usd) > 0) combined.push({ account_id: r.account_id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.expense_date })
      })
      
      if (mainAcc && amc && amc.length > 0) {
        const amcMonthly = amc.reduce((s, r) => s + (Number(r.annual_amount_usd)/12), 0)
        if (amcMonthly > 0) {
          const start = new Date(range.from)
          const end = new Date(range.to)
          let cur = new Date(start.getFullYear(), start.getMonth(), 1)
          while (cur <= end) {
            const dStr = `${cur.getFullYear()}-${String(cur.getMonth()+1).padStart(2, '0')}-28`
            if (dStr >= range.from && dStr <= range.to) {
              combined.push({ account_id: mainAcc.id, debit_usd: amcMonthly, credit_usd: 0, entry_date: dStr })
            }
            cur.setMonth(cur.getMonth() + 1)
          }
        }
      }
      
      ;(rdr || []).forEach(r => {
        if (foodAcc && Number(r.food_amount_usd) > 0) combined.push({ account_id: foodAcc.id, debit_usd: 0, credit_usd: r.food_amount_usd, entry_date: r.revenue_date })
        if (bevAcc && Number(r.beverage_amount_usd) > 0) combined.push({ account_id: bevAcc.id, debit_usd: 0, credit_usd: r.beverage_amount_usd, entry_date: r.revenue_date })
        if (otherFbAcc && Number(r.other_amount_usd) > 0) combined.push({ account_id: otherFbAcc.id, debit_usd: 0, credit_usd: r.other_amount_usd, entry_date: r.revenue_date })
      })
    }

    const balances = {}
    ;(combined || []).forEach(e => { balances[e.account_id] = (balances[e.account_id] || 0) + Number(e.debit_usd) - Number(e.credit_usd) })"""

content = content.replace(old_compute, new_compute)

with open('src/pages/Comparison.jsx', 'w') as f:
    f.write(content)
