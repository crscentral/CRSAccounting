import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

old_pace = """  const now = new Date()
  const activeMonth = startMonth === 'all' ? (now.getFullYear() === startYear ? now.getMonth() + 1 : 12) : Number(startMonth)
  const isCurrentMonth = startYear === now.getFullYear() && activeMonth === now.getMonth() + 1
  const thisMonthKey = `${startYear}-${activeMonth}`
  const thisMonthRow = rows[thisMonthKey]
  
  const daysElapsed = isCurrentMonth ? now.getDate() : daysInMonth(startYear, activeMonth)
  const daysInActiveMonth = daysInMonth(startYear, activeMonth)
  
  const paceExpected = thisMonthRow ? (Number(thisMonthRow.revenue) || 0) * (daysElapsed / daysInActiveMonth) : 0
  const mtdActual = actuals[thisMonthKey] || 0
  const mtdPaceVariance = mtdActual - paceExpected"""

new_pace = """  const now = new Date()
  const activeMonth = startMonth === 'all' ? (now.getFullYear() === startYear ? now.getMonth() + 1 : 12) : Number(startMonth)
  const isCurrentMonth = startYear === now.getFullYear() && activeMonth === now.getMonth() + 1
  const thisMonthKey = `${startYear}-${activeMonth}`
  const thisMonthRow = rows[thisMonthKey] || { revenue_usd: 0 }
  
  const daysElapsed = isCurrentMonth ? now.getDate() : daysInMonth(startYear, activeMonth)
  const daysInActiveMonth = daysInMonth(startYear, activeMonth)
  
  const dailyUsd = Number(thisMonthRow.revenue_usd) || 0
  const paceExpected = dailyUsd * daysElapsed
  const mtdActual = actuals[thisMonthKey] || 0
  const mtdPaceVariance = mtdActual - paceExpected"""

content = content.replace(old_pace, new_pace)

old_cards = """      {thisMonthRow && (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
          <KpiCard label={`${MONTH_NAMES[activeMonth - 1]} Budget`} value={fmt((Number(thisMonthRow.revenue) || 0) * daysInActiveMonth)} icon={TrendingUp} tone="gold" />
          <KpiCard label={`${MONTH_NAMES[activeMonth - 1]} ${isCurrentMonth ? 'MTD ' : ''}Actual`} value={fmt(mtdActual)} icon={TrendingUp} tone="green" />
          <KpiCard
            label={isCurrentMonth ? `Pace Variance (Day ${daysElapsed}/${daysInActiveMonth})` : `${MONTH_NAMES[activeMonth - 1]} Variance`}
            value={fmtRoundedAbs(mtdPaceVariance)}
            icon={mtdPaceVariance >= 0 ? TrendingUp : AlertTriangle}
            tone={mtdPaceVariance >= 0 ? 'green' : 'red'}
            sublabel={isCurrentMonth ? "Actual vs. where you should be by today" : "Actual vs. Full Month Budget"}
          />
        </div>
      )}"""

new_cards = """      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label={`${MONTH_NAMES[activeMonth - 1]} Budget`} value={fmt(dailyUsd * daysInActiveMonth)} icon={TrendingUp} tone="gold" />
        <KpiCard label={`${MONTH_NAMES[activeMonth - 1]} ${isCurrentMonth ? 'MTD ' : ''}Actual`} value={fmt(mtdActual)} icon={TrendingUp} tone="green" />
        <KpiCard
          label={isCurrentMonth ? `Pace Variance (Day ${daysElapsed}/${daysInActiveMonth})` : `${MONTH_NAMES[activeMonth - 1]} Variance`}
          value={fmtRoundedAbs(mtdPaceVariance)}
          icon={mtdPaceVariance >= 0 ? TrendingUp : AlertTriangle}
          tone={mtdPaceVariance >= 0 ? 'green' : 'red'}
          sublabel={isCurrentMonth ? "Actual vs. where you should be by today" : "Actual vs. Full Month Budget"}
        />
      </div>"""

content = content.replace(old_cards, new_cards)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)

