export default function KpiCard({ label, value, sublabel, icon: Icon, tone = 'slate' }) {
  const tones = {
    green: 'bg-emerald-100 text-emerald-600',
    red: 'bg-rose-100 text-rose-600',
    blue: 'bg-blue-100 text-blue-600',
    gold: 'bg-gold-100 text-gold-700',
    slate: 'bg-slate-100 text-slate-600',
  }

  const len = String(value).length
  const sizeClass = len > 18 ? 'text-[11px] sm:text-xs' : len > 15 ? 'text-sm sm:text-base' : len > 12 ? 'text-base sm:text-lg' : len > 9 ? 'text-lg sm:text-xl' : 'text-xl sm:text-2xl'

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
      <div className={`${sizeClass} font-bold text-slate-800 whitespace-nowrap overflow-hidden text-ellipsis`} title={String(value)}>
        {value}
      </div>
      {sublabel && <div className="text-xs text-slate-400">{sublabel}</div>}
    </div>
  )
}
