import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Dashboard from '../Dashboard'

export default function TallyDashboardEmbed() {
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
}
