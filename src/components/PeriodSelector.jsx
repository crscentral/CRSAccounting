import { useState, useRef, useEffect } from 'react'
import { ChevronDown } from 'lucide-react'
import { PERIOD_TYPES, MONTH_NAMES } from '../lib/fiscalYear'

export default function PeriodSelector({
  periodType, onPeriodTypeChange,
  n, onNChange,
  fiscalYearStartMonth, onFiscalYearStartMonthChange,
  customFrom, customTo, onCustomChange,
  selectedYear, selectedMonth, onYearMonthChange,
}) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    function onClick(e) { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  const current = PERIOD_TYPES.find(p => p.value === periodType)
  const now = new Date()
  const curYear = selectedYear || now.getFullYear()
  const curMonth = selectedMonth || (now.getMonth() + 1)
  const yearOptions = Array.from({ length: 7 }, (_, i) => now.getFullYear() - 5 + i)

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center justify-between gap-2 w-full sm:w-auto min-w-[160px] px-3 py-2 rounded-lg border border-slate-300 bg-white text-sm font-medium text-slate-700 hover:border-navy-400"
      >
        <span>{periodType === 'MTD' ? `${MONTH_NAMES[curMonth - 1].slice(0, 3)} ${curYear}` : current?.label}{(periodType === 'LAST_N_YEARS' || periodType === 'NEXT_N_YEARS') ? ` (${n})` : ''}</span>
        <ChevronDown size={16} className="text-slate-400 shrink-0" />
      </button>

      {open && (
        <div className="absolute z-30 mt-1 w-80 max-w-[92vw] bg-white border border-slate-200 rounded-lg shadow-lg right-0 p-3 space-y-3">
          <div>
            <div className="text-[11px] font-semibold text-slate-400 uppercase mb-1">Period</div>
            <div className="grid grid-cols-2 gap-1">
              {PERIOD_TYPES.map(p => (
                <button
                  key={p.value}
                  onClick={() => onPeriodTypeChange(p.value)}
                  className={`text-left text-sm px-2 py-1.5 rounded-md ${periodType === p.value ? 'bg-navy-600 text-white' : 'hover:bg-slate-100 text-slate-700'}`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {periodType === 'MTD' && (
            <div>
              <div className="text-[11px] font-semibold text-slate-400 uppercase mb-1">Year</div>
              <select
                value={curYear}
                onChange={e => onYearMonthChange({ year: Number(e.target.value), month: curMonth })}
                className="w-full border border-slate-300 rounded-md px-2 py-1.5 text-sm mb-2"
              >
                {yearOptions.map(y => <option key={y} value={y}>{y}</option>)}
              </select>
              <div className="text-[11px] font-semibold text-slate-400 uppercase mb-1">Month</div>
              <div className="grid grid-cols-4 gap-1">
                {MONTH_NAMES.map((m, i) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => onYearMonthChange({ year: curYear, month: i + 1 })}
                    className={`text-xs px-1.5 py-1.5 rounded-md ${curMonth === i + 1 ? 'bg-navy-600 text-white' : 'hover:bg-slate-100 text-slate-700'}`}
                  >
                    {m.slice(0, 3)}
                  </button>
                ))}
              </div>
            </div>
          )}

          {(periodType === 'LAST_N_YEARS' || periodType === 'NEXT_N_YEARS') && (
            <div>
              <div className="text-[11px] font-semibold text-slate-400 uppercase mb-1">Number of years</div>
              <input
                type="number" min={1} max={10} value={n}
                onChange={e => onNChange(Number(e.target.value))}
                className="w-full border border-slate-300 rounded-md px-2 py-1 text-sm"
              />
            </div>
          )}

          {periodType === 'CUSTOM' && (
            <div className="grid grid-cols-2 gap-2">
              <div>
                <div className="text-[11px] font-semibold text-slate-400 uppercase mb-1">From</div>
                <input type="date" value={customFrom || ''} onChange={e => onCustomChange({ from: e.target.value, to: customTo })}
                  className="w-full border border-slate-300 rounded-md px-2 py-1 text-sm" />
              </div>
              <div>
                <div className="text-[11px] font-semibold text-slate-400 uppercase mb-1">To</div>
                <input type="date" value={customTo || ''} onChange={e => onCustomChange({ from: customFrom, to: e.target.value })}
                  className="w-full border border-slate-300 rounded-md px-2 py-1 text-sm" />
              </div>
            </div>
          )}

          {periodType === 'YTD' && (
            <div>
              <div className="text-[11px] font-semibold text-slate-400 uppercase mb-1">
                YTD start month (fiscal year)
              </div>
              <select
                value={fiscalYearStartMonth}
                onChange={e => onFiscalYearStartMonthChange(Number(e.target.value))}
                className="w-full border border-slate-300 rounded-md px-2 py-1.5 text-sm"
              >
                {MONTH_NAMES.map((m, i) => (
                  <option key={m} value={i + 1}>{m} (e.g. {i === 0 ? 'calendar year' : i === 3 ? 'India-style Apr–Mar' : i === 8 ? 'Sept–Aug' : `${m}–${MONTH_NAMES[(i + 11) % 12]}`})</option>
                ))}
              </select>
              <p className="text-[11px] text-slate-400 mt-1">This is a one-off override for this view. Change the default in Settings.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
