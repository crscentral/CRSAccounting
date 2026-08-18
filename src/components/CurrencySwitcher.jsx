import { useState, useMemo, useRef, useEffect } from 'react'
import { ChevronDown, Search } from 'lucide-react'
import { CURRENCY_LIST } from '../lib/currencies'

export default function CurrencySwitcher({ value, onChange, favorites = ['USD', 'THB', 'INR'] }) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const ref = useRef(null)

  useEffect(() => {
    function onClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  const favList = CURRENCY_LIST.filter(c => favorites.includes(c.code))
  const filtered = useMemo(() => {
    if (!query) return CURRENCY_LIST
    const q = query.toLowerCase()
    return CURRENCY_LIST.filter(c => c.code.toLowerCase().includes(q) || c.name.toLowerCase().includes(q))
  }, [query])

  const current = CURRENCY_LIST.find(c => c.code === value)

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center justify-between gap-2 w-full sm:w-auto min-w-[140px] px-3 py-2 rounded-lg border border-slate-300 bg-white text-sm font-medium text-slate-700 hover:border-navy-400"
      >
        <span>{current ? `${current.code} — ${current.name}` : value}</span>
        <ChevronDown size={16} className="text-slate-400 shrink-0" />
      </button>
      {open && (
        <div className="absolute z-30 mt-1 w-72 max-w-[90vw] bg-white border border-slate-200 rounded-lg shadow-lg right-0">
          <div className="p-2 border-b border-slate-100 flex items-center gap-2">
            <Search size={14} className="text-slate-400" />
            <input
              autoFocus
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search currency..."
              className="w-full text-sm outline-none"
            />
          </div>
          {!query && favList.length > 0 && (
            <div className="border-b border-slate-100">
              <div className="px-3 pt-2 pb-1 text-[11px] font-semibold text-slate-400 uppercase">Favorites</div>
              {favList.map(c => (
                <CurrencyRow key={c.code} c={c} selected={c.code === value} onClick={() => { onChange(c.code); setOpen(false) }} />
              ))}
            </div>
          )}
          <div className="max-h-64 overflow-y-auto">
            {filtered.map(c => (
              <CurrencyRow key={c.code} c={c} selected={c.code === value} onClick={() => { onChange(c.code); setOpen(false) }} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function CurrencyRow({ c, selected, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-3 py-2 text-sm hover:bg-navy-50 flex items-center justify-between ${selected ? 'bg-navy-50 font-semibold text-navy-700' : 'text-slate-700'}`}
    >
      <span>{c.code} — {c.name}</span>
      {selected && <span className="text-navy-600">✓</span>}
    </button>
  )
}
