import re

with open('src/pages/TallyMode/TallyDashboardEmbed.jsx', 'r') as f:
    content = f.read()

# Replace imports
imports = """import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../../lib/supabaseClient'
import { useAuth } from '../../lib/AuthContext'
import { useCurrencyAndPeriod } from '../../lib/useCurrencyAndPeriod'"""

content = re.sub(r'import { useEffect } from \'react\'\nimport { useNavigate } from \'react-router-dom\'\nimport Dashboard from \'\.\./Dashboard\'', imports, content)

# Replace the component body
old_body = """export default function TallyDashboardEmbed() {
  const navigate = useNavigate()

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
    <div className="bg-[#f8f9fa] w-full h-full overflow-y-auto">
      <div className="bg-white border-b p-2 flex justify-between items-center sticky top-0 z-10 shadow-sm">
        <span className="font-bold text-navy-700">Financial Dashboard</span>
        <button onClick={() => navigate('/tally-mode')} className="bg-slate-200 text-slate-800 px-2 py-0.5 border border-slate-400 text-xs hover:bg-slate-300">ESC: Gateway</button>
      </div>
      <div className="p-4 relative">
        {/* We have to reset tally CSS scoping effects on Dashboard children if any leaked, but it's isolated enough */}
        <Dashboard />
      </div>
    </div>
  )
}"""

new_body = """export default function TallyDashboardEmbed() {
  const navigate = useNavigate()
  const { activeCompany, activeProduct } = useAuth()
  const cp = useCurrencyAndPeriod()
  
  const [data, setData] = useState({ revenue: 0, expenses: 0, assets: 0, liabilities: 0, equity: 0 })

  useEffect(() => {
    if (activeCompany) {
      supabase.from('ledger_entries')
        .select('debit_usd, credit_usd, accounts!inner(type)')
        .eq('company_id', activeCompany.id)
        .eq('product', activeProduct)
        .gte('entry_date', cp.range.from)
        .lte('entry_date', cp.range.to)
        .then(({ data: entries }) => {
          if (!entries) return
          let rev = 0, exp = 0, ast = 0, liab = 0, eq = 0
          
          entries.forEach(e => {
            const dr = Number(e.debit_usd) || 0
            const cr = Number(e.credit_usd) || 0
            const type = e.accounts?.type
            
            if (type === 'Revenue') rev += (cr - dr)
            if (type === 'Expense') exp += (dr - cr)
            if (type === 'Asset') ast += (dr - cr)
            if (type === 'Liability') liab += (cr - dr)
            if (type === 'Equity') eq += (cr - dr)
          })
          
          setData({ revenue: rev, expenses: exp, assets: ast, liabilities: liab, equity: eq })
        })
    }
  }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape') {
        navigate('/tally-mode')
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [navigate])

  const fmt = val => Math.abs(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

  return (
    <div className="tally-voucher-container">
      <div className="tally-voucher-main">
        <div className="tally-voucher-header items-center">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/tally-mode')} className="bg-slate-200 text-slate-800 px-2 py-0.5 border border-slate-400 text-xs hover:bg-slate-300">ESC: Quit</button>
            <span>Financial Dashboard (Tally View)</span>
          </div>
        </div>
        
        <div className="bg-white border border-slate-300 p-8 max-w-4xl mx-auto w-full shadow-sm">
          <div className="font-bold text-lg mb-6 border-b pb-2 text-center text-slate-800 uppercase tracking-widest">
            {activeCompany?.name} - Key Performance Indicators
          </div>
          <div className="text-center font-semibold text-slate-500 mb-8">{cp.range.from} to {cp.range.to}</div>
          
          <div className="tally-grid text-[15px]">
            <div className="tally-grid-row border-b-2 border-slate-400 font-bold bg-amber-50">
              <div className="tally-grid-col w-1/2">Metric</div>
              <div className="tally-grid-col w-1/2 text-right">Amount (USD)</div>
            </div>
            
            <div className="tally-grid-row hover:bg-amber-100">
              <div className="tally-grid-col w-1/2 font-semibold text-green-800">Total Revenue</div>
              <div className="tally-grid-col w-1/2 text-right font-bold">{fmt(data.revenue)} {data.revenue < 0 ? 'Dr' : 'Cr'}</div>
            </div>
            <div className="tally-grid-row hover:bg-amber-100">
              <div className="tally-grid-col w-1/2 font-semibold text-red-800">Total Expenses</div>
              <div className="tally-grid-col w-1/2 text-right font-bold">{fmt(data.expenses)} {data.expenses < 0 ? 'Cr' : 'Dr'}</div>
            </div>
            <div className="tally-grid-row border-b border-dashed border-slate-400 hover:bg-amber-100">
              <div className="tally-grid-col w-1/2 font-bold italic text-blue-900">Net Profit</div>
              <div className="tally-grid-col w-1/2 text-right font-bold italic">{fmt(data.revenue - data.expenses)}</div>
            </div>
            
            <div className="tally-grid-row hover:bg-amber-100 mt-4 border-t border-slate-400">
              <div className="tally-grid-col w-1/2 font-semibold">Total Assets</div>
              <div className="tally-grid-col w-1/2 text-right font-bold">{fmt(data.assets)} {data.assets < 0 ? 'Cr' : 'Dr'}</div>
            </div>
            <div className="tally-grid-row hover:bg-amber-100">
              <div className="tally-grid-col w-1/2 font-semibold">Total Liabilities</div>
              <div className="tally-grid-col w-1/2 text-right font-bold">{fmt(data.liabilities)} {data.liabilities < 0 ? 'Dr' : 'Cr'}</div>
            </div>
            <div className="tally-grid-row border-b border-dashed border-slate-400 hover:bg-amber-100">
              <div className="tally-grid-col w-1/2 font-semibold">Total Equity</div>
              <div className="tally-grid-col w-1/2 text-right font-bold">{fmt(data.equity)} {data.equity < 0 ? 'Dr' : 'Cr'}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}"""

content = content.replace(old_body, new_body)

with open('src/pages/TallyMode/TallyDashboardEmbed.jsx', 'w') as f:
    f.write(content)
