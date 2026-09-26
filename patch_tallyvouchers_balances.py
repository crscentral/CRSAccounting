import re

with open('src/pages/TallyMode/TallyVouchers.jsx', 'r') as f:
    content = f.read()

# Add balances state
content = content.replace(
    "const [filteredLedgers, setFilteredLedgers] = useState([])",
    "const [filteredLedgers, setFilteredLedgers] = useState([])\n  const [balances, setBalances] = useState({})"
)

# Fetch ledger entries and compute balances
old_useEffect = """  useEffect(() => {
    if (activeCompany) {
      supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).then(({ data }) => {
        setLedgers(data || [])
        setFilteredLedgers(data || [])
      })
    }
  }, [activeCompany, activeProduct])"""

new_useEffect = """  useEffect(() => {
    if (activeCompany) {
      Promise.all([
        supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
        supabase.from('ledger_entries').select('account_id, debit_amount, credit_amount').eq('company_id', activeCompany.id).eq('product', activeProduct)
      ]).then(([accRes, ledgRes]) => {
        const accs = accRes.data || []
        const entries = ledgRes.data || []
        
        const bals = {}
        accs.forEach(a => bals[a.id] = 0)
        
        entries.forEach(e => {
          if (bals[e.account_id] !== undefined) {
            bals[e.account_id] += (Number(e.debit_amount) || 0) - (Number(e.credit_amount) || 0)
          }
        })
        
        setLedgers(accs)
        setFilteredLedgers(accs)
        setBalances(bals)
      })
    }
  }, [activeCompany, activeProduct])"""
content = content.replace(old_useEffect, new_useEffect)

# Update the ledger input rendering to show balance below it
old_input = """              <div className="tally-grid-col flex-1">
                <input 
                  autoFocus={activeRowId === row.id && activeField === 'ledgerName'}
                  className="tally-input font-bold" 
                  value={row.ledgerName} 
                  placeholder="Ledger Account"
                  onChange={e => handleLedgerChange(e, row.id)}
                  onKeyDown={e => handleInputKeyDown(e, row.id, 'ledgerName')}
                  onFocus={() => handleLedgerFocus(row.id)}
                />
              </div>"""

new_input = """              <div className="tally-grid-col flex-1 relative">
                <input 
                  autoFocus={activeRowId === row.id && activeField === 'ledgerName'}
                  className="tally-input font-bold" 
                  value={row.ledgerName} 
                  placeholder="Ledger Account"
                  onChange={e => handleLedgerChange(e, row.id)}
                  onKeyDown={e => handleInputKeyDown(e, row.id, 'ledgerName')}
                  onFocus={() => handleLedgerFocus(row.id)}
                />
                {row.accountId && balances[row.accountId] !== undefined && (
                  <div className="text-[11px] text-slate-500 italic mt-0.5">
                    Cur Bal: {Math.abs(balances[row.accountId]).toLocaleString(undefined, {minimumFractionDigits: 2})} {balances[row.accountId] >= 0 ? 'Dr' : 'Cr'}
                  </div>
                )}
              </div>"""
content = content.replace(old_input, new_input)

# Update sidebar to show balances
old_sidebar_item = """                onClick={() => {
                  setEntries(prev => prev.map(ent => ent.id === activeRowId ? { ...ent, ledgerName: l.name, accountId: l.id } : ent))
                  setSidebarOpen(false)
                  setActiveField('amount')
                }}
              >
                {l.name}
              </div>"""

new_sidebar_item = """                onClick={() => {
                  setEntries(prev => prev.map(ent => ent.id === activeRowId ? { ...ent, ledgerName: l.name, accountId: l.id } : ent))
                  setSidebarOpen(false)
                  setActiveField('amount')
                }}
              >
                <div className="flex justify-between w-full">
                  <span>{l.name}</span>
                  {balances[l.id] !== undefined && (
                    <span className="text-xs text-slate-500">{Math.abs(balances[l.id]).toLocaleString(undefined, {minimumFractionDigits: 2})} {balances[l.id] >= 0 ? 'Dr' : 'Cr'}</span>
                  )}
                </div>
              </div>"""
content = content.replace(old_sidebar_item, new_sidebar_item)


with open('src/pages/TallyMode/TallyVouchers.jsx', 'w') as f:
    f.write(content)
