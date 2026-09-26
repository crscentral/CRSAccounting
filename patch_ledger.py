import re

with open('src/pages/Ledger.jsx', 'r') as f:
    content = f.read()

# We will modify loadEntries and generateLedgerReport
# Let's find the loadEntries block
old_load_entries = """  async function loadEntries() {
    const { data } = await supabase
      .from('ledger_entries')
      .select('*')
      .eq('company_id', activeCompany.id)
      .eq('account_id', accountId)
      .gte('entry_date', cp.range.from)
      .lte('entry_date', cp.range.to)
      .order('entry_date')
    setEntries(data || [])
  }"""

new_load_entries = """  async function loadEntries() {
    const { data } = await supabase
      .from('ledger_entries')
      .select('*')
      .eq('company_id', activeCompany.id)
      .eq('account_id', accountId)
      .gte('entry_date', cp.range.from)
      .lte('entry_date', cp.range.to)
      .order('entry_date')
      
    let combined = data || []
    
    if (['hotel', 'restaurant'].includes(activeProduct)) {
      const selectedAccount = accounts.find(a => a.id === accountId)
      if (selectedAccount) {
        const isRoomRev = selectedAccount.name.toLowerCase().includes('room revenue')
        const isExpense = selectedAccount.type === 'Expenses'
        const isRevenue = selectedAccount.type === 'Revenue'
        
        if (isRoomRev) {
          const { data: hrs } = await supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', cp.range.from).lte('stat_date', cp.range.to)
          ;(hrs || []).forEach(r => {
            if (Number(r.room_revenue_usd) > 0) {
              combined.push({ id: `hrs-${r.id}`, entry_date: r.stat_date, description: 'Daily Room Revenue', currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.room_revenue_usd })
            }
          })
        }
        
        if (isExpense) {
          const { data: hee } = await supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('account_id', accountId).gte('expense_date', cp.range.from).lte('expense_date', cp.range.to)
          ;(hee || []).forEach(r => {
            combined.push({ id: `hee-${r.id}`, entry_date: r.expense_date, description: r.notes || 'Expense Entry', currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
          })
        }
        
        if (isRevenue && !isRoomRev) {
          const { data: hre } = await supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('account_id', accountId).gte('entry_date', cp.range.from).lte('entry_date', cp.range.to)
          ;(hre || []).forEach(r => {
            combined.push({ id: `hre-${r.id}`, entry_date: r.entry_date, description: r.notes || 'Ancillary Revenue', currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
          })
        }
        
        // F&B Revenue injection
        if (selectedAccount.code && selectedAccount.code.startsWith('41')) {
          const { data: rdr } = await supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
          ;(rdr || []).forEach(r => {
            let amount = 0
            if (selectedAccount.name.toLowerCase().includes('food')) amount = Number(r.food_amount_usd) || 0
            else if (selectedAccount.name.toLowerCase().includes('beverage')) amount = Number(r.beverage_amount_usd) || 0
            else if (selectedAccount.name.toLowerCase().includes('other')) amount = Number(r.other_amount_usd) || 0
            else amount = Number(r.total_amount_usd) || 0
            
            if (amount > 0) {
              combined.push({ id: `rdr-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Revenue`, currency: 'USD', debit_usd: 0, credit_usd: amount })
            }
          })
        }
        
        // Guest Invoices (Accounts Receivable) - AR is typically an Asset account. 
        if (selectedAccount.name.toLowerCase().includes('accounts receivable') || selectedAccount.name.toLowerCase().includes('guest ledger')) {
          const { data: hgi } = await supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to)
          ;(hgi || []).forEach(i => {
            if (Number(i.invoice_amount_usd) > 0) {
              combined.push({ id: `hgi-inv-${i.id}`, entry_date: i.invoice_date, description: `Invoice ${(i.invoice_number || '').substring(0,8)} - ${i.guest_name}`, currency: i.currency || 'USD', debit_usd: i.invoice_amount_usd, credit_usd: 0 })
            }
            if (Number(i.collected_amount_usd) > 0) {
              combined.push({ id: `hgi-col-${i.id}`, entry_date: i.invoice_date, description: `Payment Collected - ${(i.invoice_number || '').substring(0,8)}`, currency: i.currency || 'USD', debit_usd: 0, credit_usd: i.collected_amount_usd })
            }
          })
        }
      }
      
      combined.sort((a, b) => a.entry_date.localeCompare(b.entry_date))
    }
    
    setEntries(combined)
  }"""

content = content.replace(old_load_entries, new_load_entries)


old_report_gen = """    const account = accounts.find(a => a.id === selections.account)
    const { data } = await supabase.from('ledger_entries').select('*').eq('company_id', activeCompany.id).eq('account_id', selections.account)
      .gte('entry_date', range.from).lte('entry_date', range.to).order('entry_date')

    let running = 0
    const rows = (data || []).map(e => {"""

new_report_gen = """    const account = accounts.find(a => a.id === selections.account)
    const { data } = await supabase.from('ledger_entries').select('*').eq('company_id', activeCompany.id).eq('account_id', selections.account)
      .gte('entry_date', range.from).lte('entry_date', range.to).order('entry_date')

    let combined = data || []
    
    if (['hotel', 'restaurant'].includes(activeProduct) && account) {
      const isRoomRev = account.name.toLowerCase().includes('room revenue')
      const isExpense = account.type === 'Expenses'
      const isRevenue = account.type === 'Revenue'
      
      if (isRoomRev) {
        const { data: hrs } = await supabase.from('hotel_room_stats').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('stat_date', range.from).lte('stat_date', range.to)
        ;(hrs || []).forEach(r => {
          if (Number(r.room_revenue_usd) > 0) {
            combined.push({ id: `hrs-${r.id}`, entry_date: r.stat_date, description: 'Daily Room Revenue', currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.room_revenue_usd })
          }
        })
      }
      
      if (isExpense) {
        const { data: hee } = await supabase.from('hotel_expense_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('account_id', account.id).gte('expense_date', range.from).lte('expense_date', range.to)
        ;(hee || []).forEach(r => {
          combined.push({ id: `hee-${r.id}`, entry_date: r.expense_date, description: r.notes || 'Expense Entry', currency: r.currency || 'USD', debit_usd: r.amount_usd, credit_usd: 0 })
        })
      }
      
      if (isRevenue && !isRoomRev) {
        const { data: hre } = await supabase.from('hotel_revenue_entries').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('account_id', account.id).gte('entry_date', range.from).lte('entry_date', range.to)
        ;(hre || []).forEach(r => {
          combined.push({ id: `hre-${r.id}`, entry_date: r.entry_date, description: r.notes || 'Ancillary Revenue', currency: r.currency || 'USD', debit_usd: 0, credit_usd: r.amount_usd })
        })
      }
      
      if (account.code && account.code.startsWith('41')) {
        const { data: rdr } = await supabase.from('restaurant_daily_revenue').select('*').eq('company_id', activeCompany.id).gte('revenue_date', range.from).lte('revenue_date', range.to)
        ;(rdr || []).forEach(r => {
          let amount = 0
          if (account.name.toLowerCase().includes('food')) amount = Number(r.food_amount_usd) || 0
          else if (account.name.toLowerCase().includes('beverage')) amount = Number(r.beverage_amount_usd) || 0
          else if (account.name.toLowerCase().includes('other')) amount = Number(r.other_amount_usd) || 0
          else amount = Number(r.total_amount_usd) || 0
          
          if (amount > 0) {
            combined.push({ id: `rdr-${r.id}`, entry_date: r.revenue_date, description: `${r.meal_period} F&B Revenue`, currency: 'USD', debit_usd: 0, credit_usd: amount })
          }
        })
      }
      
      if (account.name.toLowerCase().includes('accounts receivable') || account.name.toLowerCase().includes('guest ledger')) {
        const { data: hgi } = await supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', range.from).lte('invoice_date', range.to)
        ;(hgi || []).forEach(i => {
          if (Number(i.invoice_amount_usd) > 0) {
            combined.push({ id: `hgi-inv-${i.id}`, entry_date: i.invoice_date, description: `Invoice ${(i.invoice_number || '').substring(0,8)} - ${i.guest_name}`, currency: i.currency || 'USD', debit_usd: i.invoice_amount_usd, credit_usd: 0 })
          }
          if (Number(i.collected_amount_usd) > 0) {
            combined.push({ id: `hgi-col-${i.id}`, entry_date: i.invoice_date, description: `Payment Collected - ${(i.invoice_number || '').substring(0,8)}`, currency: i.currency || 'USD', debit_usd: 0, credit_usd: i.collected_amount_usd })
          }
        })
      }
      
      combined.sort((a, b) => a.entry_date.localeCompare(b.entry_date))
    }

    let running = 0
    const rows = combined.map(e => {"""

content = content.replace(old_report_gen, new_report_gen)

with open('src/pages/Ledger.jsx', 'w') as f:
    f.write(content)

