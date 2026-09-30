export default function KpiCard({ label, value, sublabel, icon: Icon, tone = 'slate' }) {
  const tones = {
    green: 'bg-emerald-100 text-emerald-600',
    red: 'bg-rose-100 text-rose-600',
    blue: 'bg-blue-100 text-blue-600',
    gold: 'bg-gold-100 text-gold-700',
    slate: 'bg-slate-100 text-slate-600',
  }

  const len = String(value).length
  let content = value
  const valStr = String(value)
  const m = valStr.match(/^([^\d]*)([\d,.]+)([^\d]*)$/)
  
  // If it's a long number (e.g., LAK 1,384,584)
  if (m && len > 11) {
    const prefix = m[1].trim()
    const suffix = m[3].trim()
    // Avoid splitting percentages like "100.0%"
    if (suffix !== '%' && prefix !== '%') {
        const currencyStr = [prefix, suffix].filter(Boolean).join(' ')
        if (currencyStr) {
          content = (
            <div className="flex flex-col items-center justify-center w-full mt-1">
              <span className="text-sm font-bold text-slate-400 mb-0.5">{currencyStr}</span>
              <span className="whitespace-nowrap">{m[2]}</span>
            </div>
          )
        }
    }
  }

  const sizeClass = len > 16 ? 'text-lg sm:text-xl' : len > 12 ? 'text-xl sm:text-2xl' : 'text-2xl sm:text-3xl'


  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 flex flex-col gap-2 min-w-0">
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-500 line-clamp-2 leading-snug break-words">{label}</span>
        {Icon && (
          <span className={`h-8 w-8 rounded-lg flex items-center justify-center shrink-0 ${tones[tone]}`}>
            <Icon size={16} />
          </span>
        )}
      </div>
      <div className={`flex items-center ${content !== value ? 'justify-center' : ''} ${sizeClass} font-bold text-slate-800 break-words`} title={String(value)}>
        {content}
      </div>
      {sublabel && <div className="text-xs text-slate-400">{sublabel}</div>}
    </div>
  )
}
