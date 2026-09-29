with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

old_logic = """  const thisMonthRow = rows[thisMonthKey] || { revenue_usd: 0 }
  
  const daysElapsed = isCurrentMonth ? now.getDate() : daysInMonth(startYear, activeMonth)
  const daysInActiveMonth = daysInMonth(startYear, activeMonth)
  
  const dailyUsd = Number(thisMonthRow.revenue_usd) || 0
  const paceExpected = dailyUsd * daysElapsed
  const mtdActual = actuals[thisMonthKey] || 0
  const mtdPaceVariance = mtdActual - paceExpected"""

new_logic = """  const thisMonthRow = rows[thisMonthKey] || { revenue_usd: 0 }
  
  const daysElapsed = isCurrentMonth ? now.getDate() : daysInMonth(startYear, activeMonth)
  const daysInActiveMonth = daysInMonth(startYear, activeMonth)
  
  let monthlyBudgetUsd = 0
  let mtdActualUsd = 0
  if (activeProduct === 'hotel') {
    monthlyBudgetUsd = (Number(thisMonthRow.revenue_usd) || 0) * daysInActiveMonth
    mtdActualUsd = actuals[thisMonthKey] || 0
  } else {
    for (const a of ancillaryAccounts) {
      monthlyBudgetUsd += Number(ancillaryBudgets[`${a.code}-${activeMonth}`]?.amount_usd || 0)
      mtdActualUsd += Number(ancillaryActuals[`${a.code}-${activeMonth}`] || 0)
    }
  }
  
  const dailyExpectedUsd = monthlyBudgetUsd / daysInActiveMonth
  const paceExpected = dailyExpectedUsd * daysElapsed
  const mtdPaceVariance = mtdActualUsd - paceExpected"""

content = content.replace(old_logic, new_logic)

# Now update the widgets to use monthlyBudgetUsd and mtdActualUsd
old_widgets = """      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label={`${MONTH_NAMES[activeMonth - 1]} Budget`} value={fmt(dailyUsd * daysInActiveMonth)} icon={TrendingUp} tone="gold" />
        <KpiCard label={`${MONTH_NAMES[activeMonth - 1]} ${isCurrentMonth ? 'MTD ' : ''}Actual`} value={fmt(mtdActual)} icon={TrendingUp} tone="green" />"""

new_widgets = """      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label={`${MONTH_NAMES[activeMonth - 1]} Budget`} value={fmt(monthlyBudgetUsd)} icon={TrendingUp} tone="gold" />
        <KpiCard label={`${MONTH_NAMES[activeMonth - 1]} ${isCurrentMonth ? 'MTD ' : ''}Actual`} value={fmt(mtdActualUsd)} icon={TrendingUp} tone="green" />"""

content = content.replace(old_widgets, new_widgets)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)

