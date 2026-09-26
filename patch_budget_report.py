import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# 1. Update the ReportOptionsModal fields
old_modal = """      {reportModalOpen && (
        <ReportOptionsModal
          title={activeProduct === "restaurant" ? "F&B Revenue Budget" : "Room Revenue Budget"}
          fields={[
            { type: 'currency', key: 'currency', default: displayCurrency },
            { 
              type: 'select', 
              key: 'startYear', 
              label: 'Select Year', 
              default: startYear,
              options: Array.from({ length: 8 }, (_, i) => { const y = new Date().getFullYear() - 2 + i; return { value: y, label: String(y) } }) 
            }
          ]}
          onGenerate={generateBudgetReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}"""

new_modal = """      {reportModalOpen && (
        <ReportOptionsModal
          title={activeProduct === "restaurant" ? "F&B Revenue Budget" : "Room Revenue Budget"}
          fields={[
            { type: 'currency', key: 'currency', default: displayCurrency },
            { 
              type: 'select', 
              key: 'period', 
              label: 'Select Period', 
              default: String(startYear),
              options: [
                { value: 'all', label: 'All Available Years' },
                ...Array.from({ length: 8 }, (_, i) => { const y = new Date().getFullYear() - 2 + i; return { value: String(y), label: `${y} (Full Year)` } }),
                ...Array.from({ length: 12 }, (_, i) => { return { value: `${startYear}-${i + 1}`, label: `${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i]} ${startYear}` } })
              ]
            }
          ]}
          onGenerate={generateBudgetReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}"""
content = content.replace(old_modal, new_modal)

# 2. Update generateBudgetReport to handle 'all', 'YYYY', or 'YYYY-M'
old_gen = """  async function generateBudgetReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    const sy = Number(selections.startYear || startYear)
    const years = [sy]
    const tableRows = []
    years.forEach(y => MONTH_NAMES.forEach((m, i) => {
      const key = `${y}-${i + 1}`
      const row = rows[key]"""

new_gen = """  async function generateBudgetReport(selections, format) {
    const rrate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const f = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rrate }), selections.currency)
    
    const p = selections.period || String(startYear)
    let periodKeys = []
    
    if (p === 'all') {
      const allYears = Array.from({ length: 8 }, (_, i) => new Date().getFullYear() - 2 + i)
      allYears.forEach(y => MONTH_NAMES.forEach((_, i) => periodKeys.push(`${y}-${i + 1}`)))
    } else if (p.includes('-')) {
      periodKeys.push(p)
    } else {
      MONTH_NAMES.forEach((_, i) => periodKeys.push(`${p}-${i + 1}`))
    }

    const tableRows = []
    periodKeys.forEach(key => {
      const [y, mStr] = key.split('-')
      const mIdx = Number(mStr) - 1
      const mName = MONTH_NAMES[mIdx]
      const row = rows[key]"""
content = content.replace(old_gen, new_gen)

old_gen2 = """        const days = daysInMonth(y, i + 1)
        const monthlyRevUsd = (row.revenue_usd || 0) * days
        const roomsOcc = Math.round(totalRooms * (Number(row.occ) || 0) / 100)
        const adrUsd = roomsOcc > 0 ? (row.revenue_usd / roomsOcc) : 0
        tableRows.push([
          `${m} ${y}`, """

new_gen2 = """        const days = daysInMonth(Number(y), mIdx + 1)
        const monthlyRevUsd = (row.revenue_usd || 0) * days
        const roomsOcc = Math.round(totalRooms * (Number(row.occ) || 0) / 100)
        const adrUsd = roomsOcc > 0 ? (row.revenue_usd / roomsOcc) : 0
        tableRows.push([
          `${mName} ${y}`, """
content = content.replace(old_gen2, new_gen2)

# 3. Add Total YTD to KPI cards and move Select Year to PageHeader actions
old_kpi = """      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <KpiCard label={`${startYear} ${activeProduct === "restaurant" ? "Food Sales Budget" : "Front Office Revenue Budget"}`} value={fmt(revenueSummary.frontOffice)} icon={TrendingUp} tone="gold" sublabel={activeProduct === "restaurant" ? "Food Sales Account" : "Room Revenue + Front Office"} />
        <KpiCard label={`${startYear} ${activeProduct === "restaurant" ? "Beverage Sales Budget" : "F&B Service Budget"}`} value={fmt(revenueSummary.fbService)} icon={TrendingUp} tone="blue" sublabel={activeProduct === "restaurant" ? "Beverage Sales Account" : "F&B Service Accounts"} />
        <KpiCard label={`${startYear} Other Revenue Budget`} value={fmt(revenueSummary.otherRev)} icon={TrendingUp} tone="emerald" sublabel="Other Operating Income" />
      </div>


      <div className="flex items-center gap-2 mb-4">
        <label className="text-sm text-slate-500">Select Year:</label>
        <select value={startYear} onChange={e => setStartYear(Number(e.target.value))} className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm">
          {Array.from({ length: 8 }, (_, i) => now.getFullYear() - 2 + i).map(y => <option key={y} value={y}>{y}</option>)}
        </select>
        <span className="text-xs text-slate-400">Select year for Revenue Budget</span>
      </div>"""

new_kpi = """      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label={`${startYear} ${activeProduct === "restaurant" ? "Food Sales Budget" : "Front Office Revenue Budget"}`} value={fmt(revenueSummary.frontOffice)} icon={TrendingUp} tone="gold" sublabel={activeProduct === "restaurant" ? "Food Sales Account" : "Room Revenue + Front Office"} />
        <KpiCard label={`${startYear} ${activeProduct === "restaurant" ? "Beverage Sales Budget" : "F&B Service Budget"}`} value={fmt(revenueSummary.fbService)} icon={TrendingUp} tone="blue" sublabel={activeProduct === "restaurant" ? "Beverage Sales Account" : "F&B Service Accounts"} />
        <KpiCard label={`${startYear} Other Revenue Budget`} value={fmt(revenueSummary.otherRev)} icon={TrendingUp} tone="emerald" sublabel="Other Operating Income" />
        <KpiCard label={`Total ${startYear} Budget`} value={fmt(revenueSummary.frontOffice + revenueSummary.fbService + revenueSummary.otherRev)} icon={TrendingUp} tone="indigo" sublabel="Combined Total Budget" />
      </div>"""
content = content.replace(old_kpi, new_kpi)

old_header = """          <div className="flex flex-wrap items-center gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            <select value={displayCurrency} onChange={e => setDisplayCurrency(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code} - {c.name}</option>)}
            </select>
          </div>"""

new_header = """          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1 bg-white border border-slate-300 rounded-lg px-2 py-1">
              <span className="text-sm text-slate-500 ml-1">Period:</span>
              <select value={startYear} onChange={e => setStartYear(Number(e.target.value))} className="bg-transparent text-sm font-medium focus:outline-none">
                {Array.from({ length: 8 }, (_, i) => now.getFullYear() - 2 + i).map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            <select value={displayCurrency} onChange={e => setDisplayCurrency(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code} - {c.name}</option>)}
            </select>
          </div>"""
content = content.replace(old_header, new_header)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)

