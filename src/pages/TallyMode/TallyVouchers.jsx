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
  const [narration, setNarration] = useState('')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  
  const [ledgers, setLedgers] = useState([])
  const [filteredLedgers, setFilteredLedgers] = useState([])
  const [balances, setBalances] = useState({})
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [selectedLedgerIndex, setSelectedLedgerIndex] = useState(0)
  
  const [entries, setEntries] = useState([{ id: 1, type: 'Dr', ledgerName: '', amount: '' }, { id: 2, type: 'Cr', ledgerName: '', amount: '' }])
  const [activeRowId, setActiveRowId] = useState(1)
  const [activeField, setActiveField] = useState('ledgerName') // type, ledgerName, amount, narration

  useEffect(() => {
    if (activeCompany) {
      Promise.all([
        supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct),
        supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd').eq('company_id', activeCompany.id).eq('product', activeProduct)
      ]).then(([accRes, ledgRes]) => {
        const accs = accRes.data || []
        const ents = ledgRes.data || []
        
        const bals = {}
        accs.forEach(a => bals[a.id] = 0)
        
        ents.forEach(e => {
          if (bals[e.account_id] !== undefined) {
            bals[e.account_id] += (Number(e.debit_usd) || 0) - (Number(e.credit_usd) || 0)
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

  const totalDr = entries.filter(e => e.type === 'Dr').reduce((sum, e) => sum + (Number(e.amount) || 0), 0)
  const totalCr = entries.filter(e => e.type === 'Cr').reduce((sum, e) => sum + (Number(e.amount) || 0), 0)

  const handleInputKeyDown = (e, rowId, field) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (field === 'type') {
        setActiveField('ledgerName')
      } else if (field === 'ledgerName') {
        setActiveField('amount')
      } else if (field === 'amount') {
        const isBalanced = totalDr > 0 && totalCr > 0 && totalDr === totalCr
        
        if (isBalanced) {
          // If balanced, move to narration
          setActiveRowId('narration')
          setActiveField('narration')
        } else {
          // Move to next row
          const idx = entries.findIndex(r => r.id === rowId)
          if (idx === entries.length - 1) {
            // Suggest the opposite type of what we need
            const nextType = totalDr > totalCr ? 'Cr' : 'Dr'
            const suggestedAmount = Math.abs(totalDr - totalCr)
            setEntries([...entries, { id: Date.now(), type: nextType, ledgerName: '', amount: suggestedAmount ? String(suggestedAmount) : '' }])
            setActiveRowId(Date.now())
          } else {
            setActiveRowId(entries[idx+1].id)
          }
          setActiveField('type')
        }
      }
    }
  }

  const handleNarrationKeyDown = async (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      
      // Save logic!
      const validEntries = entries.filter(e => e.accountId && Number(e.amount) > 0)
      if (validEntries.length < 2 || totalDr !== totalCr) {
        setMessage('Voucher must be balanced and have at least 2 entries.')
        setTimeout(() => setMessage(''), 3000)
        return
      }

      setSaving(true)
      setMessage('Saving...')
      
      const legPayloads = validEntries.map(ent => ({
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
      }
      
      setMessage('Voucher Saved Successfully!')
      setSaving(false)
      
      // Reset form
      setTimeout(() => {
        setVoucherNumber(prev => prev + 1)
        setEntries([{ id: Date.now(), type: 'Dr', ledgerName: '', amount: '' }, { id: Date.now()+1, type: 'Cr', ledgerName: '', amount: '' }])
        setNarration('')
        setActiveRowId(entries[0].id)
        setActiveField('ledgerName')
        setMessage('')
      }, 1500)
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
      <div className="tally-voucher-main relative flex flex-col">
        <div className="tally-voucher-header items-center">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/tally-mode')} className="bg-slate-200 text-slate-800 px-2 py-0.5 border border-slate-400 text-xs hover:bg-slate-300">ESC: Quit</button>
            <span>Accounting Voucher Creation</span>
          </div>
          <span className="text-blue-900">{voucherType}</span>
        </div>
        
        <div className="flex justify-between mb-4 px-2 font-semibold">
          <div>No. <span className="text-red-800">{voucherNumber}</span></div>
          <div>
             <input type="date" className="bg-transparent border-none outline-none text-right font-bold" value={date} onChange={e => setDate(e.target.value)} />
          </div>
        </div>
        
        <div className="tally-grid flex flex-col">
          <div className="tally-grid-row bg-slate-100 font-bold text-center h-8 flex items-center">
            <div className="w-16 border-r border-slate-200">Dr/Cr</div>
            <div className="flex-1 border-r border-slate-200">Particulars</div>
            <div className="w-32">Amount</div>
          </div>
          
          <div className="flex-1 overflow-y-auto min-h-[300px]">
            {entries.map(row => (
              <div key={row.id} className="tally-grid-row border-b border-slate-100">
                <div className="w-16 p-2 border-r border-slate-100">
                  <input 
                    autoFocus={activeRowId === row.id && activeField === 'type'}
                    className="tally-input font-bold" 
                    value={row.type} 
                    onChange={e => setEntries(prev => prev.map(ent => ent.id === row.id ? { ...ent, type: e.target.value } : ent))}
                    onKeyDown={e => handleInputKeyDown(e, row.id, 'type')}
                    onFocus={() => { setActiveRowId(row.id); setActiveField('type'); setSidebarOpen(false) }}
                  />
                </div>
                <div className="flex-1 p-2 relative border-r border-slate-100">
                  <input 
                    autoFocus={activeRowId === row.id && activeField === 'ledgerName'}
                    className="tally-input font-bold" 
                    value={row.ledgerName} 
                    placeholder={activeRowId === row.id ? "Select Ledger" : ""}
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
                <div className="w-32 p-2">
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

          <div className="tally-grid-row font-bold p-2 border-t border-slate-300 bg-amber-50/50">
            <div className="flex-1 text-right pr-4 italic text-slate-600">Total</div>
            <div className="w-32 text-right">
               {totalDr > 0 && totalDr === totalCr ? (
                 <span className="text-green-700">{totalDr.toLocaleString(undefined, {minimumFractionDigits:2})}</span>
               ) : (
                 <span className="text-red-600">{totalDr} Dr / {totalCr} Cr</span>
               )}
            </div>
          </div>
        </div>

        <div className="mt-4 bg-white p-2 border border-slate-300 flex items-center">
          <div className="font-bold w-24">Narration:</div>
          <input
            autoFocus={activeField === 'narration'}
            className="flex-1 tally-input italic border-b border-dashed border-slate-400 p-1"
            value={narration}
            onChange={e => setNarration(e.target.value)}
            onKeyDown={handleNarrationKeyDown}
            onFocus={() => { setActiveField('narration'); setActiveRowId('narration') }}
            placeholder="Press Enter here to save the voucher..."
          />
        </div>

        {message && (
          <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 px-8 py-4 font-bold text-lg shadow-xl border ${message.includes('Error') ? 'bg-red-100 text-red-800 border-red-300' : 'bg-green-100 text-green-800 border-green-300'}`}>
            {message}
          </div>
        )}
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
