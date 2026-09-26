import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const MENU_ITEMS = [
  { section: 'Masters', items: [{ label: 'Create', hotkey: 'C', path: '/tally-mode/create' }, { label: 'Alter', hotkey: 'A', path: '/tally-mode/alter' }] },
  { section: 'Transactions', items: [{ label: 'Vouchers', hotkey: 'V', path: '/tally-mode/vouchers' }] },
  { section: 'Utilities', items: [{ label: 'Banking', hotkey: 'B', path: '/tally-mode/banking' }] },
  { section: 'Reports', items: [{ label: 'Balance Sheet', hotkey: 'B', path: '/tally-mode/balance-sheet' }, { label: 'Profit & Loss A/c', hotkey: 'P', path: '/tally-mode/pnl' }, { label: 'Ratio Analysis', hotkey: 'R', path: '/tally-mode/ratios' }, { label: 'Display More Reports', hotkey: 'D', path: '/tally-mode/display' }] },
]

export default function TallyGateway() {
  const navigate = useNavigate()
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
    <div className="tally-gateway-container">
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
  )
}
