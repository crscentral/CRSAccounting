import { useEffect } from 'react'
import { Outlet, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../lib/AuthContext'
import './tally.css'

export default function TallyLayout() {
  const { activeCompany } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    // Add specific tally class to body to scope any global resets if necessary, though we try to scope to tally-app-container
    document.body.classList.add('tally-mode-active')
    return () => document.body.classList.remove('tally-mode-active')
  }, [])

  return (
    <div className="tally-app-container">
      {/* Tally Header Bar */}
      <div className="tally-header">
        <div className="tally-header-left">
          <span className="tally-title">TallyPrime - {activeCompany?.name || 'Company'}</span>
        </div>
        <div className="tally-header-right">
          <Link to="/" className="tally-exit-btn">Exit Tally View</Link>
        </div>
      </div>

      {/* Main Working Area */}
      <div className="tally-main-area">
        <Outlet />
      </div>

      {/* Tally Footer Bar */}
      <div className="tally-footer">
        <div>Tally Classic View Module (Isolator Layer)</div>
        <div>Ctrl+M: Gateway | ESC: Quit</div>
      </div>
    </div>
  )
}
