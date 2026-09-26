import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# 1. Add startMonth state
content = content.replace("  const [startYear, setStartYear] = useState(new Date().getFullYear())", 
                          "  const [startYear, setStartYear] = useState(new Date().getFullYear())\n  const [startMonth, setStartMonth] = useState('all')")

# 2. Update revenueSummary and pace logic
old_summary = """  const revenueSummary = useMemo(() => {
    let roomRev = 0
    for (let m = 1; m <= 12; m++) {
      const r = rows[`${startYear}-${m}`]
      if (r) {
        roomRev += (Number(r.revenue_usd) || 0) * new Date(startYear, m, 0).getDate()
      }
    }
    
    let frontOffice = roomRev
    let fbService = 0
    let otherRev = 0
    
    ancillaryAccounts.forEach(a => {
      let bUsd = 0
      for (let m = 1; m <= 12; m++) {
        const k = `${a.code}-${m}`
        if (ancillaryBudgets[k]) bUsd += Number(ancillaryBudgets[k].amount_usd) || 0
      }
      if (a.code.startsWith('40')) frontOffice += bUsd
      else if (a.code.startsWith('41')) fbService += bUsd
      else otherRev += bUsd
    })
    
    return { frontOffice, fbService, otherRev }
  }, [rows, ancillaryAccounts, ancillaryBudgets, startYear])"""

new_summary = """  const revenueSummary = useMemo(() => {
    let roomRev = 0
    const mStart = startMonth === 'all' ? 1 : Number(startMonth)
    const mEnd = startMonth === 'all' ? 12 : Number(startMonth)

    for (let m = mStart; m <= mEnd; m++) {
      const r = rows[`${startYear}-${m}`]
      if (r) {
        roomRev += (Number(r.revenue_usd) || 0) * new Date(startYear, m, 0).getDate()
      }
    }
    
    let frontOffice = roomRev
    let fbService = 0
    let otherRev = 0
    
    ancillaryAccounts.forEach(a => {
      let bUsd = 0
      for (let m = mStart; m <= mEnd; m++) {
        const k = `${a.code}-${m}`
        if (ancillaryBudgets[k]) bUsd += Number(ancillaryBudgets[k].amount_usd) || 0
      }
      if (a.code.startsWith('40')) frontOffice += bUsd
      else if (a.code.startsWith('41')) fbService += bUsd
      else otherRev += bUsd
    })
    
    return { frontOffice, fbService, otherRev }
  }, [rows, ancillaryAccounts, ancillaryBudgets, startYear, startMonth])"""
content = content.replace(old_summary, new_summary)

# Update Pace calculation based on startMonth if it's the current month/year.
# The pace block currently hardcodes to the ACTUAL current date. If they select a past month, pace makes no sense (it should just be actual variance).
old_pace = """  const now = new Date()
  const thisMonthKey = `${now.getFullYear()}-${now.getMonth() + 1}`
  const thisMonthRow = rows[thisMonthKey]
  const daysElapsed = now.getDate()
  const daysInCurrentMonth = daysInMonth(now.getFullYear(), now.getMonth() + 1)
  const paceExpected = thisMonthRow ? (Number(thisMonthRow.revenue) || 0) * (daysElapsed / daysInCurrentMonth) : 0
  const mtdActual = actuals[thisMonthKey] || 0
  const mtdPaceVariance = mtdActual - paceExpected"""

new_pace = """  const now = new Date()
  const activeMonth = startMonth === 'all' ? (now.getFullYear() === startYear ? now.getMonth() + 1 : 12) : Number(startMonth)
  const isCurrentMonth = startYear === now.getFullYear() && activeMonth === now.getMonth() + 1
  const thisMonthKey = `${startYear}-${activeMonth}`
  const thisMonthRow = rows[thisMonthKey]
  
  const daysElapsed = isCurrentMonth ? now.getDate() : daysInMonth(startYear, activeMonth)
  const daysInActiveMonth = daysInMonth(startYear, activeMonth)
  
  const paceExpected = thisMonthRow ? (Number(thisMonthRow.revenue) || 0) * (daysElapsed / daysInActiveMonth) : 0
  const mtdActual = actuals[thisMonthKey] || 0
  const mtdPaceVariance = mtdActual - paceExpected"""
content = content.replace(old_pace, new_pace)

# 3. Update Period dropdowns in PageHeader
old_header = """            <div className="flex items-center gap-1 bg-white border border-slate-300 rounded-lg px-2 py-1">
              <span className="text-sm text-slate-500 ml-1">Period:</span>
              <select value={startYear} onChange={e => setStartYear(Number(e.target.value))} className="bg-transparent text-sm font-medium focus:outline-none">
                {Array.from({ length: 8 }, (_, i) => now.getFullYear() - 2 + i).map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>"""

new_header = """            <div className="flex items-center gap-1 bg-white border border-slate-300 rounded-lg px-2 py-1">
              <span className="text-sm text-slate-500 ml-1">Period:</span>
              <select value={startYear} onChange={e => setStartYear(Number(e.target.value))} className="bg-transparent text-sm font-medium focus:outline-none pr-1">
                {Array.from({ length: 8 }, (_, i) => new Date().getFullYear() - 2 + i).map(y => <option key={y} value={y}>{y}</option>)}
              </select>
              <span className="text-slate-300">/</span>
              <select value={startMonth} onChange={e => setStartMonth(e.target.value)} className="bg-transparent text-sm font-medium focus:outline-none pl-1">
                <option value="all">Full Year</option>
                {MONTH_NAMES.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
              </select>
            </div>"""
content = content.replace(old_header, new_header)

# 4. Update the Pace cards labels
old_pace_cards = """      {thisMonthRow && (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
          <KpiCard label="This Month Budget" value={fmt(Number(thisMonthRow.revenue) || 0)} icon={TrendingUp} tone="gold" />
          <KpiCard label="MTD Actual" value={fmt(mtdActual)} icon={TrendingUp} tone="green" />
          <KpiCard
            label={`Pace Variance (Day ${daysElapsed}/${daysInCurrentMonth})`}
            value={fmtRoundedAbs(mtdPaceVariance)}
            icon={mtdPaceVariance >= 0 ? TrendingUp : AlertTriangle}
            tone={mtdPaceVariance >= 0 ? 'green' : 'red'}
            sublabel="Actual vs. where you should be by today"
          />
        </div>
      )}"""

new_pace_cards = """      {thisMonthRow && (
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
content = content.replace(old_pace_cards, new_pace_cards)

# 5. Update KPI Cards and replace "Front Office" with "FO"
# We also want the label to be dynamic (e.g. Sept 2026 or 2026)
old_kpi_cards = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${startYear} ${activeProduct === "restaurant" ? "Food Sales Budget" : "Front Office Revenue Budget"}`} value={fmt(revenueSummary.frontOffice)} icon={TrendingUp} tone="gold" sublabel={activeProduct === "restaurant" ? "Food Sales Account" : "Room Revenue + Front Office"} />
        <KpiCard label={`${startYear} ${activeProduct === "restaurant" ? "Beverage Sales Budget" : "F&B Service Budget"}`} value={fmt(revenueSummary.fbService)} icon={TrendingUp} tone="blue" sublabel={activeProduct === "restaurant" ? "Beverage Sales Account" : "F&B Service Accounts"} />
        <KpiCard label={`${startYear} Other Revenue Budget`} value={fmt(revenueSummary.otherRev)} icon={TrendingUp} tone="emerald" sublabel="Other Operating Income" />
        <KpiCard label={`Total ${startYear} Budget`} value={fmt(revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev)} icon={TrendingUp} tone="indigo" sublabel="Combined Total Budget" />
      </div>"""

new_kpi_cards = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} ${activeProduct === "restaurant" ? "Food Sales Budget" : "FO Revenue Budget"}`} value={fmt(revenueSummary.frontOffice)} icon={TrendingUp} tone="gold" sublabel={activeProduct === "restaurant" ? "Food Sales Account" : "Room Revenue + FO Accounts"} />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} ${activeProduct === "restaurant" ? "Beverage Sales Budget" : "F&B Service Budget"}`} value={fmt(revenueSummary.fbService)} icon={TrendingUp} tone="blue" sublabel={activeProduct === "restaurant" ? "Beverage Sales Account" : "F&B Service Accounts"} />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} Other Revenue Budget`} value={fmt(revenueSummary.otherRev)} icon={TrendingUp} tone="emerald" sublabel="Other Operating Income" />
        <KpiCard label={`${startMonth === 'all' ? startYear : MONTH_NAMES[Number(startMonth)-1] + ' ' + startYear} Total Budget`} value={fmt(revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev)} icon={TrendingUp} tone="indigo" sublabel="Combined Total Budget" />
      </div>"""
content = content.replace(old_kpi_cards, new_kpi_cards)

# 6. Make the tables respect startMonth
old_table_months = """                    <tbody>
                      {MONTH_NAMES.map((m, i) => {"""
new_table_months = """                    <tbody>
                      {MONTH_NAMES.map((m, i) => {
                        if (startMonth !== 'all' && (i + 1) !== Number(startMonth)) return null;"""
content = content.replace(old_table_months, new_table_months)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)

