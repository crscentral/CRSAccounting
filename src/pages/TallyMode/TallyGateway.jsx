import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../lib/AuthContext'
import { useCurrencyAndPeriod } from '../../lib/useCurrencyAndPeriod'

const MENU_ITEMS = [
  { section: 'Masters', items: [{ label: 'Create', hotkey: 'C', path: '/tally-mode/create' }, { label: 'Alter', hotkey: 'A', path: '/tally-mode/alter' }] },
  { section: 'Transactions', items: [{ label: 'Vouchers', hotkey: 'V', path: '/tally-mode/vouchers' }] },
  { section: 'Utilities', items: [{ label: 'Banking', hotkey: 'B', path: '/tally-mode/banking' }] },
  { section: 'Reports', items: [{ label: 'Balance Sheet', hotkey: 'B', path: '/tally-mode/balance-sheet' }, { label: 'Profit & Loss A/c', hotkey: 'P', path: '/tally-mode/pnl' }, { label: 'Ratio Analysis', hotkey: 'R', path: '/tally-mode/ratios' }, { label: 'Display More Reports', hotkey: 'D', path: '/tally-mode/display' }] },
]

export default function TallyGateway() {
  const navigate = useNavigate()
  const { activeCompany } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [selectedIndex, setSelectedIndex] = useState(0)

  // Flatten menu for simple arrow navigation
  const flatMenu = MENU_ITEMS.reduce((acc, section) => [...acc, ...section.items], [])

  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'ArrowDown') {
        setSelectedIndex(prev => (prev + 1) % flatMenu.length)
      } else if (e.key === 'ArrowUp') {
        setSelectedIndex(prev => (prev - 1 + flatMenu.length) % flatMenu.length)
      } else if (e.key === 'Enter') {
        navigate(flatMenu[selectedIndex].path)
      } else if (e.key === 'Escape') {
        navigate('/') // Exit
      } else {
        // Hotkey navigation
        const key = e.key.toUpperCase()
        const match = flatMenu.find(item => item.hotkey.toUpperCase() === key)
        if (match) {
          navigate(match.path)
        }
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [selectedIndex, navigate, flatMenu])

  let globalIndex = 0

  return (
    <div className="flex flex-1 w-full bg-[#fdf5e6]">
      {/* Left Pane: Company Info */}
      <div className="flex-1 flex flex-col border-r border-[#c0b3a0] p-4 text-slate-800">
        <div className="flex justify-between border-b border-[#c0b3a0] pb-2 mb-4 font-bold text-[13px]">
          <div>
            <div className="text-[#800000]">Current Period</div>
            <div>{cp.range.from} to {cp.range.to}</div>
          </div>
          <div className="text-right">
            <div className="text-[#800000]">Current Date</div>
            <div>{new Date().toISOString().slice(0, 10)}</div>
          </div>
        </div>
        
        <div className="flex justify-between font-bold text-[13px] border-b border-[#c0b3a0] pb-2 text-[#800000]">
          <div>Name of Company</div>
          <div>Date of Last Entry</div>
        </div>
        
        <div className="flex justify-between mt-2 font-bold text-[14px]">
          <div>{activeCompany?.name || 'Loading...'}</div>
          <div className="font-normal text-[12px] italic">No Vouchers Entered</div>
        </div>
      </div>

      {/* Right Pane: Gateway Menu */}
      <div className="w-[400px] flex flex-col items-center justify-center p-8 bg-[var(--tally-blue)]">
        <div className="tally-gateway-menu">
        <div className="tally-gateway-title">Gateway of Tally</div>
        {MENU_ITEMS.map((section, sIdx) => (
          <div key={sIdx} className="tally-gateway-section">
            <div className="tally-gateway-section-title">{section.section}</div>
            {section.items.map((item) => {
              const isActive = globalIndex === selectedIndex
              const currentIndex = globalIndex++
              
              // Split label to highlight hotkey
              const hotkeyIndex = item.label.toLowerCase().indexOf(item.hotkey.toLowerCase())
              const before = item.label.substring(0, hotkeyIndex)
              const char = item.label.substring(hotkeyIndex, hotkeyIndex + 1)
              const after = item.label.substring(hotkeyIndex + 1)

              return (
                <div 
                  key={item.label} 
                  className={`tally-menu-item ${isActive ? 'active' : ''}`}
                  onMouseEnter={() => setSelectedIndex(currentIndex)}
                  onClick={() => navigate(item.path)}
                >
                  {hotkeyIndex >= 0 ? (
                    <><span>{before}</span><span className="hotkey">{char}</span><span>{after}</span></>
                  ) : (
                    item.label
                  )}
                </div>
              )
            })}
          </div>
        ))}
      </div>
      </div>
    </div>
  )
}
