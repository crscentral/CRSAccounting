import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# 1. Change startYear mapping from 5 years to just 1 year
content = re.sub(r'const years = Array\.from\(\{ length: 5 \}, \(_, i\) => startYear \+ i\)', 'const years = [startYear]', content)

# 2. Change the "Starting Year:" label to "Select Year:" and update hint text
content = content.replace('Starting Year:', 'Select Year:')
content = content.replace('Shows this year + next 4 (5 years total)', 'Select year for Room & Ancillary Revenue')

# 3. Change "startYear" state to just control the entire page, 
# so we can remove "ancillaryYear" and just use "startYear" (which acts as selectedYear)
# Remove ancillaryYear definition:
content = re.sub(r'const \[ancillaryYear, setAncillaryYear\] = useState\(new Date\(\)\.getFullYear\(\)\)\n', '', content)

# 4. Replace `ancillaryYear` with `startYear` throughout the file
content = content.replace('ancillaryYear', 'startYear')

# 5. Remove the redundant Select Year block for ancillary revenue (since top one controls it)
content = re.sub(r'<div className="flex items-center gap-3 mb-6 bg-slate-50 p-3 rounded-xl border border-slate-200">.*?</div>\n\n\s*<div className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-10">', '<div className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-10">', content, flags=re.DOTALL)

# 6. Change the table headers to match user request
content = content.replace('<div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{year}</div>', '<div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{year} - Room Revenue with ADR & Occ% vs Actual</div>')
content = content.replace('<div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{startYear} Annual Ancillary Summary</div>', '<div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{startYear} - Other Revenue vs Actuals</div>')
content = content.replace('<h2 className="text-2xl font-bold text-slate-800 font-[var(--font-display)] mb-6">Ancillary Revenue Budget</h2>', '')

# 7. Add the new summary boxes logic
new_summary_logic = """
  const revenueSummary = useMemo(() => {
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

    for (let m = 1; m <= 12; m++) {
      for (const a of ancillaryAccounts) {
        const k = `${a.code}-${m}`
        const amt = ancillaryBudgets[k] ? (Number(ancillaryBudgets[k].amount_usd) || 0) : 0
        if (a.subtype === 'Front Office') frontOffice += amt
        else if (a.subtype === 'F&B Service') fbService += amt
        else otherRev += amt
      }
    }
    return { frontOffice, fbService, otherRev }
  }, [rows, ancillaryBudgets, ancillaryAccounts, startYear])
"""

content = content.replace("const grandTotalRevenueActual =", new_summary_logic + "\n  const grandTotalRevenueActual =")

# 8. Update KPI Cards in the render block
new_kpi_cards = """
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <KpiCard label={`${startYear} Front Office Revenue`} value={fmt(revenueSummary.frontOffice)} icon={TrendingUp} tone="gold" sublabel="Room Revenue + Front Office" />
        <KpiCard label={`${startYear} F&B Service Revenue`} value={fmt(revenueSummary.fbService)} icon={TrendingUp} tone="blue" sublabel="F&B Service Accounts" />
        <KpiCard label={`${startYear} Other Revenue`} value={fmt(revenueSummary.otherRev)} icon={TrendingUp} tone="emerald" sublabel="Other Operating Income" />
      </div>
"""
content = re.sub(r'<div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">.*?</div>', new_kpi_cards, content, flags=re.DOTALL)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)

