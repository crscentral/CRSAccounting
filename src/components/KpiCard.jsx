export default function KpiCard({
  label,
  value,
  sublabel,
  icon: Icon,
  tone = 'slate',
  badge,
  badgeTone = 'slate',
  badgeTitle,
}) {
  const tones = {
    green: 'bg-emerald-100 text-emerald-600',
    red: 'bg-rose-100 text-rose-600',
    blue: 'bg-blue-100 text-blue-600',
    gold: 'bg-gold-100 text-gold-700',
    slate: 'bg-slate-100 text-slate-600',
    orange: 'bg-orange-100 text-orange-600',
  }

  const badgeTones = {
    green: 'bg-emerald-50 text-emerald-700 border-emerald-200/70',
    red: 'bg-rose-50 text-rose-700 border-rose-200/70',
    blue: 'bg-blue-50 text-blue-700 border-blue-200/70',
    gold: 'bg-amber-50 text-amber-700 border-amber-200/70',
    orange: 'bg-orange-50 text-orange-700 border-orange-200/70',
    slate: 'bg-slate-100 text-slate-700 border-slate-200/70',
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 flex flex-col gap-2 min-w-0">
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-500 line-clamp-2 leading-snug break-words">{label}</span>
        {Icon && (
          <span className={`h-8 w-8 rounded-lg flex items-center justify-center shrink-0 ${tones[tone] || tones.slate}`}>
            <Icon size={16} />
          </span>
        )}
      </div>
      <div className="text-xl sm:text-2xl font-bold text-slate-800 whitespace-nowrap overflow-hidden text-ellipsis" title={String(value)}>
        {value}
      </div>
      {(sublabel || badge) && (
        <div className="flex items-center justify-between text-xs text-slate-400 gap-2 mt-auto pt-0.5">
          <span className="truncate">{sublabel}</span>
          {badge && (
            <span
              className={`shrink-0 font-semibold text-[11px] leading-tight px-1.5 py-0.5 rounded border ${badgeTones[badgeTone] || badgeTones.slate}`}
              title={badgeTitle || String(badge)}
            >
              {badge}
            </span>
          )}
        </div>
      )}
    </div>
  )
}
