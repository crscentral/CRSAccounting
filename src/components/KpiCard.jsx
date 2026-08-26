export default function KpiCard({ label, value, sublabel, icon: Icon, tone = 'slate' }) {
  const tones = {
    green: 'bg-emerald-100 text-emerald-600',
    red: 'bg-rose-100 text-rose-600',
    blue: 'bg-blue-100 text-blue-600',
    gold: 'bg-gold-100 text-gold-700',
    slate: 'bg-slate-100 text-slate-600',
  }

  const len = String(value).length
  const sizeClass = len > 15 ? 'text-base sm:text-lg' : len > 11 ? 'text-lg sm:text-xl' : len > 8 ? 'text-xl sm:text-2xl' : 'text-2xl sm:text-3xl'

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 flex flex-col gap-2 min-w-0">
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-500 truncate">{label}</span>
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
