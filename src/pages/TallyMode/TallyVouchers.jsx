import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../../lib/supabaseClient'
import { useAuth } from '../../lib/AuthContext'

export default function TallyVouchers() {
  const { activeCompany, activeProduct } = useAuth()
  const navigate = useNavigate()
  
  const [voucherType, setVoucherType] = useState('Payment')
  const [voucherNumber, setVoucherNumber] = useState(1)
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10))
  
  const [ledgers, setLedgers] = useState([])
  const [filteredLedgers, setFilteredLedgers] = useState([])
  const [balances, setBalances] = useState({})
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [selectedLedgerIndex, setSelectedLedgerIndex] = useState(0)
  
  const [entries, setEntries] = useState([{ id: 1, type: 'Dr', ledgerName: '', amount: '' }, { id: 2, type: 'Cr', ledgerName: '', amount: '' }])
  const [activeRowId, setActiveRowId] = useState(1)
  const [activeField, setActiveField] = useState('ledgerName') // type, ledgerName, amount

  useEffect(() => {
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
  }, [activeCompany, activeProduct])

  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape') {
        if (sidebarOpen) setSidebarOpen(false)
        else navigate('/tally-mode')
      } else if (e.key === 'F4') { e.preventDefault(); setVoucherType('Contra') }
      else if (e.key === 'F5') { e.preventDefault(); setVoucherType('Payment') }
      else if (e.key === 'F6') { e.preventDefault(); setVoucherType('Receipt') }
      else if (e.key === 'F7') { e.preventDefault(); setVoucherType('Journal') }
      else if (e.key === 'F8') { e.preventDefault(); setVoucherType('Sales') }
      else if (e.key === 'F9') { e.preventDefault(); setVoucherType('Purchase') }
      
      // Sidebar ledger selection
      if (sidebarOpen) {
        if (e.key === 'ArrowDown') {
          e.preventDefault()
          setSelectedLedgerIndex(prev => (prev + 1) % filteredLedgers.length)
        } else if (e.key === 'ArrowUp') {
          e.preventDefault()
          setSelectedLedgerIndex(prev => (prev - 1 + filteredLedgers.length) % filteredLedgers.length)
        } else if (e.key === 'Enter') {
          e.preventDefault()
          const selected = filteredLedgers[selectedLedgerIndex]
          if (selected) {
            setEntries(prev => prev.map(ent => ent.id === activeRowId ? { ...ent, ledgerName: selected.name, accountId: selected.id } : ent))
            setSidebarOpen(false)
            setActiveField('amount')
          }
        }
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [navigate, sidebarOpen, filteredLedgers, selectedLedgerIndex, activeRowId])

  const handleInputKeyDown = (e, rowId, field) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (field === 'type') {
        setActiveField('ledgerName')
      } else if (field === 'ledgerName') {
        setActiveField('amount')
      } else if (field === 'amount') {
        // Move to next row
        const idx = entries.findIndex(r => r.id === rowId)
        if (idx === entries.length - 1) {
          setEntries([...entries, { id: Date.now(), type: 'Dr', ledgerName: '', amount: '' }])
          setActiveRowId(Date.now())
        } else {
          setActiveRowId(entries[idx+1].id)
        }
        setActiveField('type')
      }
    }
  }

  const handleLedgerFocus = (rowId) => {
    setActiveRowId(rowId)
    setActiveField('ledgerName')
    setSidebarOpen(true)
    setFilteredLedgers(ledgers)
    setSelectedLedgerIndex(0)
  }

  const handleLedgerChange = (e, rowId) => {
    const val = e.target.value
    setEntries(prev => prev.map(ent => ent.id === rowId ? { ...ent, ledgerName: val } : ent))
    const filtered = ledgers.filter(l => l.name.toLowerCase().includes(val.toLowerCase()) || l.code.includes(val))
    setFilteredLedgers(filtered)
    setSelectedLedgerIndex(0)
  }

  return (
    <div className="tally-voucher-container">
      <div className="tally-voucher-main">
        <div className="tally-voucher-header">
          <span>Accounting Voucher Creation</span>
          <span className="text-blue-900">{voucherType}</span>
        </div>
        
        <div className="flex justify-between mb-4 px-2 font-semibold">
          <div>No. <span className="text-red-800">{voucherNumber}</span></div>
          <div>{date}</div>
        </div>
        
        <div className="tally-grid">
          <div className="tally-grid-row bg-slate-100 font-bold text-center">
            <div className="tally-grid-col w-16">Dr/Cr</div>
            <div className="tally-grid-col flex-1 text-left">Particulars</div>
            <div className="tally-grid-col w-32">Amount</div>
          </div>
          
          {entries.map(row => (
            <div key={row.id} className="tally-grid-row">
              <div className="tally-grid-col w-16">
                <input 
                  autoFocus={activeRowId === row.id && activeField === 'type'}
                  className="tally-input font-bold" 
                  value={row.type} 
                  onChange={e => setEntries(prev => prev.map(ent => ent.id === row.id ? { ...ent, type: e.target.value } : ent))}
                  onKeyDown={e => handleInputKeyDown(e, row.id, 'type')}
                  onFocus={() => { setActiveRowId(row.id); setActiveField('type'); setSidebarOpen(false) }}
                />
              </div>
              <div className="tally-grid-col flex-1 relative">
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
              </div>
              <div className="tally-grid-col w-32">
                <input 
                  autoFocus={activeRowId === row.id && activeField === 'amount'}
                  className="tally-input text-right font-bold" 
                  value={row.amount} 
                  onChange={e => setEntries(prev => prev.map(ent => ent.id === row.id ? { ...ent, amount: e.target.value } : ent))}
                  onKeyDown={e => handleInputKeyDown(e, row.id, 'amount')}
                  onFocus={() => { setActiveRowId(row.id); setActiveField('amount'); setSidebarOpen(false) }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {sidebarOpen && (
        <div className="tally-voucher-sidebar">
          <div className="tally-sidebar-header">List of Ledger Accounts</div>
          <div className="tally-ledger-list">
            {filteredLedgers.map((l, idx) => (
              <div 
                key={l.id} 
                className={`tally-ledger-item ${idx === selectedLedgerIndex ? 'selected' : ''}`}
                onClick={() => {
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
              </div>
            ))}
            {filteredLedgers.length === 0 && <div className="p-4 text-slate-500 text-center">No ledgers found</div>}
          </div>
        </div>
      )}
    </div>
  )
}
