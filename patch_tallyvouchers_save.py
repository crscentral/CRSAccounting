import re

with open('src/pages/TallyMode/TallyVouchers.jsx', 'r') as f:
    content = f.read()

# Fix balance fetching
old_fetch = """        supabase.from('ledger_entries').select('account_id, debit_amount, credit_amount').eq('company_id', activeCompany.id).eq('product', activeProduct)"""
new_fetch = """        supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd').eq('company_id', activeCompany.id).eq('product', activeProduct)"""
content = content.replace(old_fetch, new_fetch)

# Fix balance computation
old_compute = """          if (bals[e.account_id] !== undefined) {
            bals[e.account_id] += (Number(e.debit_amount) || 0) - (Number(e.credit_amount) || 0)
          }"""
new_compute = """          if (bals[e.account_id] !== undefined) {
            bals[e.account_id] += (Number(e.debit_usd) || 0) - (Number(e.credit_usd) || 0)
          }"""
content = content.replace(old_compute, new_compute)

# Fix saving logic
old_save = """      const trxPayload = {
        company_id: activeCompany.id,
        product: activeProduct,
        transactionn_date: date, // Notice the DB column name is transactionn_date
        description: narration || `${voucherType} Voucher`,
        type: 'General',
        total_amount: totalDr
      }
      
      const { data: trx, error: errTrx } = await supabase.from('transactions').insert(trxPayload).select().single()
      if (errTrx) {
        setMessage('Error saving transaction: ' + errTrx.message)
        setSaving(false)
        return
      }
      
      const legPayloads = validEntries.map(ent => ({
        company_id: activeCompany.id,
        product: activeProduct,
        transaction_id: trx.id,
        account_id: ent.accountId,
        entry_date: date,
        debit_amount: ent.type === 'Dr' ? Number(ent.amount) : 0,
        credit_amount: ent.type === 'Cr' ? Number(ent.amount) : 0,
        description: narration
      }))
      
      await supabase.from('ledger_entries').insert(legPayloads)"""

new_save = """      const legPayloads = validEntries.map(ent => ({
        company_id: activeCompany.id,
        product: activeProduct,
        account_id: ent.accountId,
        entry_date: date,
        debit_usd: ent.type === 'Dr' ? Number(ent.amount) : 0,
        credit_usd: ent.type === 'Cr' ? Number(ent.amount) : 0
      }))
      
      const { error: errLeg } = await supabase.from('ledger_entries').insert(legPayloads)
      if (errLeg) {
        setMessage('Error saving ledger entries: ' + errLeg.message)
        setSaving(false)
        return
      }"""
content = content.replace(old_save, new_save)

with open('src/pages/TallyMode/TallyVouchers.jsx', 'w') as f:
    f.write(content)
