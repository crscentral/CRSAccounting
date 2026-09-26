import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

export default function TallyPlaceholder() {
  const navigate = useNavigate()
  const location = useLocation()
  
  const titleMap = {
    '/tally-mode/create': 'Master Creation',
    '/tally-mode/alter': 'Master Alteration',
    '/tally-mode/banking': 'Banking Utilities',
    '/tally-mode/balance-sheet': 'Balance Sheet',
    '/tally-mode/pnl': 'Profit & Loss A/c',
    '/tally-mode/ratios': 'Ratio Analysis',
    '/tally-mode/display': 'Display More Reports',
  }

  const title = titleMap[location.pathname] || 'Under Construction'

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
      <div className="tally-voucher-main items-center justify-center">
        <div className="bg-amber-50 border border-amber-200 p-8 text-center max-w-md shadow-lg">
          <h2 className="text-xl font-bold text-slate-800 mb-2">{title}</h2>
          <p className="text-slate-600 mb-4">
            This module is currently a layout preview. Data wiring for this specific screen is pending.
          </p>
          <div className="text-sm text-slate-500 font-bold">
            Press ESC to return to Gateway
          </div>
        </div>
      </div>
    </div>
  )
}
