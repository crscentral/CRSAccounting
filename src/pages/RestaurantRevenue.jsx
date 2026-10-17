import { useEffect, useState, useMemo } from 'react'
import { Plus, Pencil, Trash2, Users, DollarSign, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid } from 'recharts'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { resolveReportPeriod } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney, formatReportMoney } from '../lib/fx'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import KpiCard from '../components/KpiCard'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'
import RestaurantRevenueFormModal from '../components/RestaurantRevenueFormModal'
import RevenueBreakdownPie from '../components/RevenueBreakdownPie'

export default function RestaurantRevenue() {
  const { activeCompany, activeProduct, can } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [entries, setEntries] = useState([])
  const [accounts, setAccounts] = useState([])
  const [modalOpen, setModalOpen] = useState(false)
  const [editingEntry, setEditingEntry] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadData() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  async function loadData() {
    const [{ data: revData }, { data: accData }] = await Promise.all([
      supabase.from('restaurant_daily_revenue').select('*')
        .eq('company_id', activeCompany.id).eq('product', activeProduct)
        .gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
        .order('revenue_date', { ascending: false }),
      supabase.from('accounts')
        .select('id, code, name, type, product')
        .eq('company_id', activeCompany.id)
    ])
    setEntries(revData || [])
    setAccounts(accData || [])
  }

  async function handleDelete(entry) {
    if (!confirm('Delete this revenue entry? This cannot be undone.')) return
    const { error } = await supabase.from('restaurant_daily_revenue').delete().eq('id', entry.id)
    if (error) { alert('Could not delete: ' + error.message); return }
    loadData()
  }

  async function generateRevenueReport(selections, format) {
    const range = resolveReportPeriod(selections.period, activeCompany.fiscal_year_start_month || 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const fmt = selections.f || ((usd) => formatReportMoney(usd, selections.currency, rate))

    const { data } = await supabase.from('restaurant_daily_revenue').select('*')
      .eq('company_id', activeCompany.id).eq('product', activeProduct)
      .gte('revenue_date', range.from).lte('revenue_date', range.to)
      .order('revenue_date', { ascending: false })
    const rows = data || []

    const sections = []

    if (selections.sections.includes('Entries')) {
      const totCovers = rows.reduce((s, r) => s + Number(r.covers || 0), 0)
      const totFood = rows.reduce((s, r) => s + Number(r.food_amount_usd || 0), 0)
      const totBev = rows.reduce((s, r) => s + Number(r.beverage_amount_usd || 0), 0)
      const totOth = rows.reduce((s, r) => s + Number(r.other_amount_usd || 0), 0)
      const totAll = rows.reduce((s, r) => s + Number(r.amount_usd || 0), 0)
      const entryRows = rows.map(r => {
        const total = fmt(r.amount_usd)
        const perCover = r.covers > 0 ? fmt(r.amount_usd / r.covers) : '—'
        return [r.revenue_date, r.meal_period || '—', r.table_or_section || '—', r.covers, fmt(r.food_amount_usd), fmt(r.beverage_amount_usd), fmt(r.other_amount_usd), total, perCover]
      })
      if (entryRows.length > 0) {
        entryRows.push(['Total', '', '', totCovers, fmt(totFood), fmt(totBev), fmt(totOth), fmt(totAll), totCovers > 0 ? fmt(totAll / totCovers) : '—'])
      }
      sections.push({
        heading: 'Table Revenue Entries',
        columns: ['Date', 'Meal Period', 'Table/Section', 'Covers', 'Food', 'Beverage', 'Other', selections.currency === 'USD' ? 'Total (USD)' : `Total (${selections.currency} & USD)`, 'Rev/Cover'],
        rows: entryRows,
      })
    }

    if (selections.sections.includes('Daily Bifurcation (Chart)')) {
      const dailyMap = {}
      rows.forEach(r => {
        dailyMap[r.revenue_date] = dailyMap[r.revenue_date] || { food: 0, beverage: 0, other: 0 }
        dailyMap[r.revenue_date].food += Number(r.food_amount_usd)
        dailyMap[r.revenue_date].beverage += Number(r.beverage_amount_usd)
        dailyMap[r.revenue_date].other += Number(r.other_amount_usd)
      })
      const days = Object.keys(dailyMap).sort()
      sections.push({
        heading: 'Daily Revenue Bifurcation',
        chart: {
          categories: days,
          valueFormatter: v => formatMoney(v, selections.currency),
          series: [
            { name: 'Food', color: '#10b981', values: days.map(d => convertFromUsd(dailyMap[d].food, selections.currency, { [selections.currency]: rate })) },
            { name: 'Beverage', color: '#3b82f6', values: days.map(d => convertFromUsd(dailyMap[d].beverage, selections.currency, { [selections.currency]: rate })) },
            { name: 'Other', color: '#f59e0b', values: days.map(d => convertFromUsd(dailyMap[d].other, selections.currency, { [selections.currency]: rate })) },
          ],
        },
      })
    }

    const totalRevenue = rows.reduce((s, r) => s + Number(r.amount_usd), 0)
    const totalCovers = rows.reduce((s, r) => s + Number(r.covers), 0)
    sections.push({
      heading: 'Summary',
      keyValuePairs: [
        ['Total Revenue', fmt(totalRevenue)],
        ['Total Covers', totalCovers],
        ['Average Revenue / Cover', totalCovers > 0 ? fmt(totalRevenue / totalCovers) : '—'],
        ['Food Revenue', fmt(rows.reduce((s, r) => s + Number(r.food_amount_usd), 0))],
        ['Beverage Revenue', fmt(rows.reduce((s, r) => s + Number(r.beverage_amount_usd), 0))],
        ['Other Revenue', fmt(rows.reduce((s, r) => s + Number(r.other_amount_usd), 0))],
      ],
    })

    const title = 'Table Revenue Report'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    const logoUrl = activeCompany.logo_url
    if (format === 'pdf' || format === 'preview') exportMultiSectionPDF({ title, subtitle, sections, preview: format === 'preview', filename: 'restaurant_revenue_report', logoUrl })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'restaurant_revenue_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'restaurant_revenue_report', logoUrl })
  }

  if (!activeCompany) return null

  const totalRevenue = entries.reduce((s, e) => s + Number(e.amount_usd), 0)
  const totalCovers = entries.reduce((s, e) => s + Number(e.covers), 0)
  const avgPerCover = totalCovers > 0 ? totalRevenue / totalCovers : 0
  const totalFood = entries.reduce((s, e) => s + Number(e.food_amount_usd), 0)
  const totalBeverage = entries.reduce((s, e) => s + Number(e.beverage_amount_usd), 0)
  const totalOther = entries.reduce((s, e) => s + Number(e.other_amount_usd), 0)

  const dailyMap = {}
  entries.forEach(e => {
    dailyMap[e.revenue_date] = dailyMap[e.revenue_date] || { date: e.revenue_date, Food: 0, Beverage: 0, Other: 0 }
    dailyMap[e.revenue_date].Food += Number(e.food_amount_usd)
    dailyMap[e.revenue_date].Beverage += Number(e.beverage_amount_usd)
    dailyMap[e.revenue_date].Other += Number(e.other_amount_usd)
  })
  const dailyChartData = Object.values(dailyMap).sort((a, b) => a.date.localeCompare(b.date))

  const revenuePieData = useMemo(() => {
    const headTotalsUsd = {}

    // Revenue accounts from Chart of Accounts
    const revAccounts = accounts.filter(a => a.type === 'Revenue' || a.product === 'restaurant' || a.code?.startsWith('4'))

    const foodAcc = revAccounts.find(a => a.code === '4104' || a.code === '4010' || a.name?.toLowerCase().includes('food'))
    const bevAcc = revAccounts.find(a => a.code === '4105' || a.code === '4011' || a.name?.toLowerCase().includes('beverage'))
    const otherAcc = revAccounts.find(a => a.code === '4019' || a.code === '4012' || a.name?.toLowerCase().includes('other'))

    const foodLabel = foodAcc ? `${foodAcc.code ? `${foodAcc.code} - ` : ''}${foodAcc.name}` : '4104 - Food Sales'
    const bevLabel = bevAcc ? `${bevAcc.code ? `${bevAcc.code} - ` : ''}${bevAcc.name}` : '4105 - Beverage Sales'
    const otherLabel = otherAcc ? `${otherAcc.code ? `${otherAcc.code} - ` : ''}${otherAcc.name}` : '4019 - Other Operating Income'

    headTotalsUsd[foodLabel] = 0
    headTotalsUsd[bevLabel] = 0
    headTotalsUsd[otherLabel] = 0

    entries.forEach(e => {
      const foodUsd = Number(e.food_amount_usd) || 0
      const bevUsd = Number(e.beverage_amount_usd) || 0
      const otherUsd = Number(e.other_amount_usd) || 0

      headTotalsUsd[foodLabel] = (headTotalsUsd[foodLabel] || 0) + foodUsd
      headTotalsUsd[bevLabel] = (headTotalsUsd[bevLabel] || 0) + bevUsd
      headTotalsUsd[otherLabel] = (headTotalsUsd[otherLabel] || 0) + otherUsd
    })

    const totalRevenueUsd = Object.values(headTotalsUsd).reduce((s, v) => s + v, 0)
    const totalDisplayVal = cp.convert(totalRevenueUsd)

    // Sort top-to-bottom: highest revenue account remains on top and lowest at the bottom
    const items = Object.entries(headTotalsUsd)
      .filter(([_, usd]) => usd > 0.0001)
      .map(([name, usd]) => {
        const displayVal = cp.convert(usd)
        const percent = totalDisplayVal > 0 ? (displayVal / totalDisplayVal) * 100 : 0
        return {
          name,
          valueUsd: usd,
          value: displayVal,
          percent,
          percentStr: `${percent.toFixed(1)}%`,
        }
      })
      .sort((a, b) => b.value - a.value)

    return {
      items,
      totalRevenueUsd,
      totalDisplayVal,
    }
  }, [accounts, entries, cp.convert])

  return (
    <div>
      <PageHeader
        title="Table Revenue"
        subtitle={`${activeCompany.name} • Per-table revenue & covers`}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <div className="flex flex-wrap gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin', 'accountant']) && (
              <button onClick={() => { setEditingEntry(null); setModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
                <Plus size={16} /> New Entry
              </button>
            )}
          </div>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-4">
        <KpiCard label="Total Revenue" value={cp.fmt(totalRevenue)} icon={DollarSign} tone="green" />
        <KpiCard label="Total Covers" value={totalCovers} icon={Users} tone="blue" />
        <KpiCard label="Avg Revenue / Cover" value={cp.fmt(avgPerCover)} icon={TrendingUp} tone="gold" />
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Food Revenue" value={cp.fmt(totalFood)} icon={TrendingUp} tone="emerald" />
        <KpiCard label="Total Beverage Revenue" value={cp.fmt(totalBeverage)} icon={TrendingUp} tone="indigo" />
        <KpiCard label="Total Other Revenue" value={cp.fmt(totalOther)} icon={TrendingUp} tone="slate" />
      </div>

      <RevenueBreakdownPie
        title="Revenue Breakdown by Account / Head"
        subtitle="Ranked from highest to lowest revenue contribution for the selected period"
        totalLabel="Total Revenue"
        totalFormatted={cp.fmt(revenuePieData.totalRevenueUsd)}
        items={revenuePieData.items}
        fmt={cp.fmt}
        emptyMessage="No table revenue recorded for this period"
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
        <h3 className="font-semibold text-slate-700 mb-4">Daily Revenue Bifurcation</h3>
        <div className="h-64 sm:h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dailyChartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={v => cp.fmt(v)} />
              <Legend />
              <Bar dataKey="Food" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Beverage" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Other" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <DataTable
        columns={[
          { key: 'revenue_date', label: 'Date' },
          { key: 'meal_period', label: 'Meal Period', render: r => r.meal_period || '—' },
          { key: 'table_or_section', label: 'Table/Section', render: r => r.table_or_section || '—' },
          { key: 'covers', label: 'Covers' },
          { key: 'food_amount_usd', label: 'Food', render: r => cp.fmt(r.food_amount_usd) },
          { key: 'beverage_amount_usd', label: 'Beverage', render: r => cp.fmt(r.beverage_amount_usd) },
          { key: 'other_amount_usd', label: 'Other', render: r => cp.fmt(r.other_amount_usd) },
          { key: 'amount_usd', label: 'Total', render: r => cp.fmt(r.amount_usd) },
          { key: 'collected_usd', label: 'Collected', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(r.collected_usd || 0)}</span> },
          { key: 'balance', label: 'Balance', render: r => {
              const bal = Number(r.amount_usd) - (Number(r.collected_usd) || 0)
              return <span className={bal > 0 ? "text-red-600 font-medium" : "text-slate-500"}>{cp.fmt(bal)}</span>
          } },
          ...(can(['owner', 'admin', 'accountant']) ? [{
            key: 'actions', label: '', render: r => (
              <div className="flex gap-2 justify-end md:justify-start">
                <button onClick={() => { setEditingEntry(r); setModalOpen(true) }} className="text-slate-400 hover:text-navy-600"><Pencil size={15} /></button>
                <button onClick={() => handleDelete(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
              </div>
            )
          }] : []),
        ]}
        rows={entries}
        emptyMessage="No table revenue entries in this range."
      />

      {modalOpen && (
        <RestaurantRevenueFormModal
          companyId={activeCompany.id}
          product={activeProduct}
          company={activeCompany}
          entry={editingEntry}
          onClose={() => setModalOpen(false)}
          onSaved={loadData}
        />
      )}

      {reportModalOpen && (
        <ReportOptionsModal
          title="Table Revenue"
          fields={[
            { type: 'checkboxGroup', key: 'sections', label: 'Include Sections', options: ['Entries', 'Daily Bifurcation (Chart)'], default: ['Entries', 'Daily Bifurcation (Chart)'] },
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
          ]}
          onGenerate={generateRevenueReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
