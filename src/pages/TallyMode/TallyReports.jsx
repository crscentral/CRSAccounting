import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { supabase } from '../../lib/supabaseClient'
import { useAuth } from '../../lib/AuthContext'

export default function TallyReports() {
  const { activeCompany, activeProduct } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  
  const [data, setData] = useState([])
  
  const type = location.pathname.split('/').pop() // alter, banking, balance-sheet, pnl, ratios, display

  const titleMap = {
    'alter': 'List of Ledgers (Alteration)',
    'banking': 'Banking Utilities',
    'balance-sheet': 'Balance Sheet',
    'pnl': 'Profit & Loss A/c',
    'ratios': 'Ratio Analysis',
    'display': 'Display More Reports',
  }
  
  useEffect(() => {
    if (activeCompany) {
      if (type === 'alter') {
        supabase.from('accounts').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).then(({ data }) => {
          setData(data || [])
        })
      } else {
        // Just mock some data for the reports for now
        setData([
          { name: 'Data wiring pending for this report', amount: '' }
        ])
      }
    }
  }, [activeCompany, activeProduct, type])

  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape') {
        navigate('/tally-mode')
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [navigate])

  return (
    <div className="tally-voucher-container">
      <div className="tally-voucher-main">
        <div className="tally-voucher-header items-center">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/tally-mode')} className="bg-slate-200 text-slate-800 px-2 py-0.5 border border-slate-400 text-xs hover:bg-slate-300">ESC: Quit</button>
            <span>{titleMap[type]}</span>
          </div>
        </div>
        
        <div className="bg-white border border-slate-300 p-4 max-w-4xl mx-auto w-full shadow-sm flex-1">
          <div className="font-bold text-lg mb-4 text-center text-slate-800 border-b pb-2">{titleMap[type]}</div>
          
          <div className="tally-grid">
            {type === 'alter' ? (
              data.map(l => (
                <div key={l.id} className="tally-grid-row p-2 cursor-pointer hover:bg-[#f8c146]" onClick={() => navigate('/tally-mode')}>
                  <div className="w-1/3 font-semibold">{l.name}</div>
                  <div className="w-1/3 text-slate-600">{l.type}</div>
                  <div className="w-1/3 text-slate-600">{l.subtype}</div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-slate-500 italic">
                Report generation engine is being wired up for {titleMap[type]}.
              </div>
            )}
            
            {type === 'alter' && data.length === 0 && (
              <div className="p-4 text-center text-slate-500">No ledgers found.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
