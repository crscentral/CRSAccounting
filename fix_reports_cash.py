with open('src/pages/Reports.jsx', 'r') as f:
    content = f.read()

# For hrs (Hotel Room Stats)
old_hrs = """      if (roomRevAcc) {
        ;(hrs || []).forEach(r => {
          if (Number(r.room_revenue_usd) > 0) combined.push({ account_id: roomRevAcc.id, debit_usd: 0, credit_usd: r.room_revenue_usd, entry_date: r.stat_date, accounts: { type: roomRevAcc.type } })
        })
      }"""
new_hrs = """      if (roomRevAcc) {
        ;(hrs || []).forEach(r => {
          if (Number(r.room_revenue_usd) > 0) {
            combined.push({ account_id: roomRevAcc.id, debit_usd: 0, credit_usd: r.room_revenue_usd, entry_date: r.stat_date, accounts: { type: roomRevAcc.type } })
            if (cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: r.room_revenue_usd, credit_usd: 0, entry_date: r.stat_date, accounts: { type: cashAcc.type } })
          }
        })
      }"""
content = content.replace(old_hrs, new_hrs)

# For rdr (Restaurant Daily Revenue)
old_rdr = """      ;(rdr || []).forEach(r => {
        if (foodAcc && Number(r.food_amount_usd) > 0) combined.push({ account_id: foodAcc.id, debit_usd: 0, credit_usd: r.food_amount_usd, entry_date: r.revenue_date, accounts: { type: foodAcc.type } })
        if (bevAcc && Number(r.beverage_amount_usd) > 0) combined.push({ account_id: bevAcc.id, debit_usd: 0, credit_usd: r.beverage_amount_usd, entry_date: r.revenue_date, accounts: { type: bevAcc.type } })
        if (otherFbAcc && Number(r.other_amount_usd) > 0) combined.push({ account_id: otherFbAcc.id, debit_usd: 0, credit_usd: r.other_amount_usd, entry_date: r.revenue_date, accounts: { type: otherFbAcc.type } })
      })"""
new_rdr = """      ;(rdr || []).forEach(r => {
        if (foodAcc && Number(r.food_amount_usd) > 0) combined.push({ account_id: foodAcc.id, debit_usd: 0, credit_usd: r.food_amount_usd, entry_date: r.revenue_date, accounts: { type: foodAcc.type } })
        if (bevAcc && Number(r.beverage_amount_usd) > 0) combined.push({ account_id: bevAcc.id, debit_usd: 0, credit_usd: r.beverage_amount_usd, entry_date: r.revenue_date, accounts: { type: bevAcc.type } })
        if (otherFbAcc && Number(r.other_amount_usd) > 0) combined.push({ account_id: otherFbAcc.id, debit_usd: 0, credit_usd: r.other_amount_usd, entry_date: r.revenue_date, accounts: { type: otherFbAcc.type } })
        const totalRev = Number(r.food_amount_usd || 0) + Number(r.beverage_amount_usd || 0) + Number(r.other_amount_usd || 0)
        if (cashAcc && totalRev > 0) combined.push({ account_id: cashAcc.id, debit_usd: totalRev, credit_usd: 0, entry_date: r.revenue_date, accounts: { type: cashAcc.type } })
      })"""
content = content.replace(old_rdr, new_rdr)

# For hre (Hotel Revenue Entries / Ancillary)
old_hre = """      ;(hre || []).forEach(r => {
        const a = (accs || []).find(ac => ac.id === r.account_id)
        if (a && Number(r.amount_usd) > 0) combined.push({ account_id: a.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.entry_date, accounts: { type: a.type } })
      })"""
new_hre = """      ;(hre || []).forEach(r => {
        const a = (accs || []).find(ac => ac.id === r.account_id)
        if (a && Number(r.amount_usd) > 0) {
          combined.push({ account_id: a.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.entry_date, accounts: { type: a.type } })
          if (cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.entry_date, accounts: { type: cashAcc.type } })
        }
      })"""
content = content.replace(old_hre, new_hre)

# For hee (Hotel Expense Entries) - needs Accounts Payable / Cash
# Wait! Expenses are debits. The credit side should be Cash!
old_hee = """      ;(hee || []).forEach(r => {
        const a = (accs || []).find(ac => ac.id === r.account_id)
        if (a && Number(r.amount_usd) > 0) combined.push({ account_id: a.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.expense_date, accounts: { type: a.type } })
      })"""
new_hee = """      ;(hee || []).forEach(r => {
        const a = (accs || []).find(ac => ac.id === r.account_id)
        if (a && Number(r.amount_usd) > 0) {
          combined.push({ account_id: a.id, debit_usd: r.amount_usd, credit_usd: 0, entry_date: r.expense_date, accounts: { type: a.type } })
          if (cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: 0, credit_usd: r.amount_usd, entry_date: r.expense_date, accounts: { type: cashAcc.type } })
        }
      })"""
content = content.replace(old_hee, new_hee)

# For AMC
old_amc = """            combined.push({ account_id: mainAcc.id, debit_usd: amcMonthly, credit_usd: 0, entry_date: dStr, accounts: { type: mainAcc.type } })"""
new_amc = """            combined.push({ account_id: mainAcc.id, debit_usd: amcMonthly, credit_usd: 0, entry_date: dStr, accounts: { type: mainAcc.type } })
            if (cashAcc) combined.push({ account_id: cashAcc.id, debit_usd: 0, credit_usd: amcMonthly, entry_date: dStr, accounts: { type: cashAcc.type } })"""
content = content.replace(old_amc, new_amc)


with open('src/pages/Reports.jsx', 'w') as f:
    f.write(content)
