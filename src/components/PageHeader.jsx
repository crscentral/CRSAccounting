import CurrencySwitcher from './CurrencySwitcher'
import PeriodSelector from './PeriodSelector'

export default function PageHeader({ title, subtitle, currencyProps, periodProps, actions }) {
  return (
    <div className="sticky top-0 z-[10] bg-slate-50 py-4 -mt-4 mb-2 sm:mb-3">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between flex-wrap">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-navy-700 font-[var(--font-display)]">{title}</h1>
          {subtitle && <p className="text-sm text-slate-500 mt-1">{subtitle}</p>}
        </div>
        <div className="flex flex-col sm:flex-row gap-1.5 sm:items-center flex-wrap justify-end">
          {currencyProps && <CurrencySwitcher {...currencyProps} />}
          {periodProps && <PeriodSelector {...periodProps} />}
          {actions}
        </div>
      </div>
    </div>
  )
}
