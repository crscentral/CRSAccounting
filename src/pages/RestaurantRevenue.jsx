import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2, Users, DollarSign, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid } from 'recharts'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { resolveReportPeriod } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import KpiCard from '../components/KpiCard'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'
import RestaurantRevenueFormModal from '../components/RestaurantRevenueFormModal'

export default function RestaurantRevenue() {
  const { activeCompany, activeProduct, can } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [entries, setEntries] = useState([])
  const [modalOpen, setModalOpen] = useState(false)
  const [editingEntry, setEditingEntry] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadData() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])

  async function loadData() {
    const { data } = await supabase.from('restaurant_daily_revenue').select('*')
      .eq('company_id', activeCompany.id).eq('product', activeProduct)
      .gte('revenue_date', cp.range.from).lte('revenue_date', cp.range.to)
      .order('revenue_date', { ascending: false })
    setEntries(data || [])
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
    const fmt = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const { data } = await supabase.from('restaurant_daily_revenue').select('*')
      .eq('company_id', activeCompany.id).eq('product', activeProduct)
      .gte('revenue_date', range.from).lte('revenue_date', range.to)
      .order('revenue_date', { ascending: false })
    const rows = data || []

    const sections = []

    if (selections.sections.includes('Entries')) {
      sections.push({
        heading: 'Table Revenue Entries',
        columns: ['Date', 'Meal Period', 'Table/Section', 'Covers', 'Food', 'Beverage', 'Other', 'Total', 'Rev/Cover'],
        rows: rows.map(r => {
          const total = fmt(r.amount_usd)
          const perCover = r.covers > 0 ? fmt(r.amount_usd / r.covers) : '—'
          return [r.revenue_date, r.meal_period || '—', r.table_or_section || '—', r.covers, fmt(r.food_amount_usd), fmt(r.beverage_amount_usd), fmt(r.other_amount_usd), total, perCover]
        }),
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
      ],
    })

    const title = 'Table Revenue Report'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'restaurant_revenue_report' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'restaurant_revenue_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'restaurant_revenue_report' })
  }

  if (!activeCompany) return null

  const totalRevenue = entries.reduce((s, e) => s + Number(e.amount_usd), 0)
  const totalCovers = entries.reduce((s, e) => s + Number(e.covers), 0)
  const avgPerCover = totalCovers > 0 ? totalRevenue / totalCovers : 0

  const dailyMap = {}
  entries.forEach(e => {
    dailyMap[e.revenue_date] = dailyMap[e.revenue_date] || { date: e.revenue_date, Food: 0, Beverage: 0, Other: 0 }
    dailyMap[e.revenue_date].Food += Number(e.food_amount_usd)
    dailyMap[e.revenue_date].Beverage += Number(e.beverage_amount_usd)
    dailyMap[e.revenue_date].Other += Number(e.other_amount_usd)
  })
  const dailyChartData = Object.values(dailyMap).sort((a, b) => a.date.localeCompare(b.date))

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

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Revenue" value={cp.fmt(totalRevenue)} icon={DollarSign} tone="green" />
        <KpiCard label="Total Covers" value={totalCovers} icon={Users} tone="blue" />
        <KpiCard label="Avg Revenue / Cover" value={cp.fmt(avgPerCover)} icon={TrendingUp} tone="gold" />
      </div>

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
          { key: 'per_cover', label: 'Rev/Cover', render: r => r.covers > 0 ? cp.fmt(r.amount_usd / r.covers) : '—' },
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
