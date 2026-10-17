import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip as RechartsTooltip } from 'recharts'

export const REVENUE_PIE_COLORS = [
  '#1e293b', // slate-800
  '#3b82f6', // blue-500
  '#10b981', // emerald-500
  '#f59e0b', // amber-500
  '#6366f1', // indigo-500
  '#ec4899', // pink-500
  '#8b5cf6', // purple-500
  '#14b8a6', // teal-500
  '#ef4444', // red-500
  '#64748b', // slate-500
  '#06b6d4', // cyan-500
  '#84cc16', // lime-500
  '#d946ef', // fuchsia-500
  '#f97316', // orange-500
  '#0ea5e9', // sky-500
  '#a855f7', // purple-400
]

export default function RevenueBreakdownPie({
  title = 'Revenue Breakdown by Account / Head',
  subtitle = 'Ranked from highest to lowest revenue contribution for the selected period',
  totalLabel = 'Total Revenue',
  totalFormatted,
  items = [],
  fmt = (v) => v,
  emptyMessage = 'No revenue recorded for this period',
}) {
  const chartItems = items.filter(i => (i.valueUsd !== undefined ? i.valueUsd : i.value) > 0.0001)

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 sm:p-6 mb-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-100 gap-2">
        <div>
          <h3 className="text-sm sm:text-base font-bold text-slate-800">
            {title}
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            {subtitle}
          </p>
        </div>
        {totalFormatted && (
          <span className="text-xs font-bold text-navy-800 bg-navy-50 border border-navy-100 px-3 py-1.5 rounded-lg shrink-0 self-start sm:self-auto">
            {totalLabel}: {totalFormatted}
          </span>
        )}
      </div>

      <div className="flex flex-col md:flex-row items-center gap-6">
        {/* Left: Donut Chart */}
        <div className="w-full md:w-[260px] h-64 shrink-0 flex items-center justify-center">
          {chartItems.length === 0 ? (
            <div className="text-xs text-slate-400 text-center py-10">
              {emptyMessage}
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartItems}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={88}
                  paddingAngle={chartItems.length > 1 ? 2 : 0}
                >
                  {chartItems.map((entry, index) => {
                    const originalIndex = items.findIndex(it => it.name === entry.name)
                    const colorIndex = originalIndex >= 0 ? originalIndex : index
                    return (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.color || REVENUE_PIE_COLORS[colorIndex % REVENUE_PIE_COLORS.length]}
                      />
                    )
                  })}
                </Pie>
                <RechartsTooltip
                  formatter={(val, name, props) => [
                    `${fmt(props?.payload?.valueUsd !== undefined ? props.payload.valueUsd : val)} (${props?.payload?.percentStr || ''})`,
                    props?.payload?.name || name,
                  ]}
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    borderColor: '#e2e8f0',
                    borderRadius: '0.5rem',
                    fontSize: '12px',
                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Right: Ranked List from Top to Bottom */}
        <div className="flex-1 w-full max-h-64 overflow-y-auto pr-2 border-t md:border-t-0 md:border-l border-slate-100 pt-4 md:pt-0 md:pl-6">
          {items.length === 0 ? (
            <div className="text-xs text-slate-400 py-16 text-center">
              {emptyMessage}
            </div>
          ) : (
            <ul className="text-xs space-y-2.5 w-full">
              {items.map((entry, index) => (
                <li
                  key={`head-${index}`}
                  className="flex items-center justify-between text-slate-700 gap-3 py-1 hover:bg-slate-50/80 px-2 rounded-lg transition-colors"
                >
                  <div className="flex items-center min-w-0 flex-1">
                    <span className="w-12 text-right mr-3 text-slate-500 font-semibold text-xs shrink-0">
                      {entry.percentStr}
                    </span>
                    <span
                      className="w-3 h-3 mr-2.5 rounded-[3px] shrink-0"
                      style={{ backgroundColor: REVENUE_PIE_COLORS[index % REVENUE_PIE_COLORS.length] }}
                    />
                    <span
                      className="truncate font-semibold text-slate-800 text-xs sm:text-sm"
                      title={entry.name}
                    >
                      {entry.name}
                    </span>
                  </div>
                  <span className="text-xs sm:text-sm font-bold text-slate-900 shrink-0">
                    {fmt(entry.valueUsd !== undefined ? entry.valueUsd : entry.value)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
