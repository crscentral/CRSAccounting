import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { resolveReportPeriod } from '../lib/fiscalYear'
import { Printer } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'

export default function Reports() {
  const { activeCompany } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [report, setReport] = useState('balance_sheet')
  const [accounts, setAccounts] = useState([])
  const [balances, setBalances] = useState({})
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadData() }, [activeCompany, cp.range.from, cp.range.to])

  async function loadData() {
    const { data: accs } = await supabase.from('accounts').select('*').eq('company_id', activeCompany.id).order('code')
    // Balance Sheet (Assets/Liabilities/Equity) is always as-of-today (cumulative since
    // inception) -- that's what a balance sheet means. Income Statement / Trial Balance
    // respect the selected period, since those are period-scoped by nature.
    const { data: entries } = await supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd, entry_date, accounts!inner(type)').eq('company_id', activeCompany.id)
    const bal = {}
    ;(entries || []).forEach(e => {
      const isBalanceSheetAccount = ['Assets', 'Liabilities', 'Equity'].includes(e.accounts?.type)
      const inPeriod = e.entry_date >= cp.range.from && e.entry_date <= cp.range.to
      if (isBalanceSheetAccount || inPeriod) {
        bal[e.account_id] = (bal[e.account_id] || 0) + Number(e.debit_usd) - Number(e.credit_usd)
      }
    })
    setAccounts(accs || [])
    setBalances(bal)
  }

  if (!activeCompany) return null

  const byType = (type) => accounts.filter(a => a.type === type)
  const sumType = (type) => byType(type).reduce((s, a) => s + (balances[a.id] || 0), 0)

  const totalRevenue = -sumType('Revenue') // credit-normal, stored as negative debit
  const totalExpenses = sumType('Expenses')
  const totalAssets = sumType('Assets')
  const totalLiabilities = -sumType('Liabilities')
  const retainedEarnings = totalRevenue - totalExpenses

  const reportTitles = { balance_sheet: 'Balance Sheet', income_statement: 'Income Statement', trial_balance: 'Trial Balance' }

  async function generateFinancialReport(selections, format) {
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const fmt = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)
    const range = resolveReportPeriod(selections.period, activeCompany.fiscal_year_start_month || 1, selections.customFrom, selections.customTo)

    const { data: entries } = await supabase.from('ledger_entries').select('account_id, debit_usd, credit_usd, entry_date, accounts!inner(type)').eq('company_id', activeCompany.id)
    const bal = {}
    ;(entries || []).forEach(e => {
      const isBalanceSheetAccount = ['Assets', 'Liabilities', 'Equity'].includes(e.accounts?.type)
      const inPeriod = e.entry_date >= range.from && e.entry_date <= range.to
      if (isBalanceSheetAccount || inPeriod) {
        bal[e.account_id] = (bal[e.account_id] || 0) + Number(e.debit_usd) - Number(e.credit_usd)
      }
    })
    const by = (type) => accounts.filter(a => a.type === type)
    const sum = (type) => by(type).reduce((s, a) => s + (bal[a.id] || 0), 0)
    const rev = -sum('Revenue'), exp = sum('Expenses'), assets = sum('Assets'), liab = -sum('Liabilities')

    let sections = []
    const reportKey = selections.reportType
    if (reportKey === 'trial_balance') {
      sections = [{
        heading: 'Trial Balance',
        columns: ['Code', 'Account', 'Debit', 'Credit'],
        rows: accounts.map(a => { const b = bal[a.id] || 0; return [a.code, a.name, b > 0 ? fmt(b) : '—', b < 0 ? fmt(-b) : '—'] }),
      }]
    } else if (reportKey === 'income_statement') {
      sections = [{
        heading: 'Income Statement',
        columns: ['Item', 'Amount'],
        rows: [
          ...by('Revenue').map(a => [a.name, fmt(-(bal[a.id] || 0))]),
          ['Total Revenue', fmt(rev)],
          ...by('Expenses').map(a => [a.name, fmt(bal[a.id] || 0)]),
          ['Total Expenses', fmt(exp)],
          ['Net Income', fmt(rev - exp)],
        ],
      }]
    } else {
      sections = [
        { heading: 'Assets', columns: ['Account', 'Amount'], rows: [...by('Assets').map(a => [`${a.code} - ${a.name}`, fmt(Math.abs(bal[a.id] || 0))]), ['Total Assets', fmt(assets)]] },
        { heading: 'Liabilities & Equity', columns: ['Account', 'Amount'], rows: [...[...by('Liabilities'), ...by('Equity')].map(a => [`${a.code} - ${a.name}`, fmt(Math.abs(bal[a.id] || 0))]), ['Total Liabilities & Equity', fmt(liab + sum('Equity') * -1)]] },
      ]
    }

    const title = reportTitles[reportKey]
    const subtitle = reportKey === 'balance_sheet'
      ? `${activeCompany.name} • As of today • ${selections.currency}`
      : `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: reportKey })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: reportKey })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: reportKey })
  }

  return (
    <div>
      <PageHeader
        title="Financial Reports"
        subtitle={`${activeCompany.name} • ${accounts.length} accounts`}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
      />

      <div className="bg-blue-50 border border-blue-100 rounded-lg px-4 py-2.5 text-xs text-blue-700 mb-5">
        Balance Sheet always shows your cumulative position as of today (that's what a balance sheet means). The period selector above scopes the Income Statement and Trial Balance to the range you choose.
      </div>

      <div className="grid sm:grid-cols-3 gap-4 mb-6">
        {[
          { key: 'balance_sheet', label: 'Balance Sheet', desc: 'Assets, Liabilities & Equity' },
          { key: 'income_statement', label: 'Income Statement', desc: 'Revenue & Expenses' },
          { key: 'trial_balance', label: 'Trial Balance', desc: 'Account Balances Verification' },
        ].map(r => (
          <button key={r.key} onClick={() => setReport(r.key)}
            className={`text-left rounded-xl border p-5 ${report === r.key ? 'border-navy-400 bg-navy-50' : 'border-slate-200 bg-white'}`}>
            <div className="font-semibold text-slate-800">{r.label}</div>
            <div className="text-xs text-slate-400 mt-1">{r.desc}</div>
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-lg text-navy-700">{activeCompany.name}</h3>
            <p className="text-xs text-slate-400">All values in {cp.displayCurrency}{report !== 'balance_sheet' ? ` • ${cp.range.from} to ${cp.range.to}` : ' • as of today'}</p>
          </div>
          <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
            Download Report
          </button>
        </div>

        {report === 'balance_sheet' && (
          <div>
            <div className="bg-blue-50 text-blue-700 text-sm rounded-lg px-3 py-2 mb-4">
              Retained Earnings include: Total Revenue {cp.fmt(totalRevenue)} − Total Expenses {cp.fmt(totalExpenses)} = {cp.fmt(retainedEarnings)}
            </div>
            <div className="grid sm:grid-cols-2 gap-6">
              <AccountBlock title="ASSETS" color="emerald" accounts={byType('Assets')} balances={balances} fmt={cp.fmt} total={totalAssets} />
              <AccountBlock title="LIABILITIES & EQUITY" color="rose"
                accounts={[...byType('Liabilities'), ...byType('Equity')]} balances={balances} fmt={cp.fmt}
                total={totalLiabilities + sumType('Equity') * -1} />
            </div>
          </div>
        )}

        {report === 'income_statement' && (
          <div className="space-y-5">
            <div>
              <div className="bg-emerald-600 text-white text-sm font-semibold px-3 py-2 rounded-t-lg">REVENUE</div>
              <div className="border border-t-0 border-slate-100 rounded-b-lg divide-y divide-slate-50">
                {byType('Revenue').map(a => (
                  <Row key={a.id} label={a.name} value={cp.fmt(-(balances[a.id] || 0))} />
                ))}
                <Row label="Total Revenue" value={cp.fmt(totalRevenue)} bold />
              </div>
            </div>
            <div>
              <div className="bg-rose-600 text-white text-sm font-semibold px-3 py-2 rounded-t-lg">EXPENSES</div>
              <div className="border border-t-0 border-slate-100 rounded-b-lg divide-y divide-slate-50">
                {byType('Expenses').map(a => (
                  <Row key={a.id} label={a.name} value={cp.fmt(balances[a.id] || 0)} />
                ))}
                <Row label="Total Expenses" value={cp.fmt(totalExpenses)} bold />
              </div>
            </div>
            <Row label="Net Income" value={cp.fmt(retainedEarnings)} bold large />
          </div>
        )}

        {report === 'trial_balance' && (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b border-slate-100 text-slate-400">
                <th className="py-2">Code</th><th className="py-2">Account</th><th className="py-2">Debit</th><th className="py-2">Credit</th>
              </tr>
            </thead>
            <tbody>
              {accounts.map(a => {
                const bal = balances[a.id] || 0
                return (
                  <tr key={a.id} className="border-b border-slate-50">
                    <td className="py-2">{a.code}</td>
                    <td className="py-2">{a.name}</td>
                    <td className="py-2">{bal > 0 ? cp.fmt(bal) : '—'}</td>
                    <td className="py-2">{bal < 0 ? cp.fmt(-bal) : '—'}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {reportModalOpen && (
        <ReportOptionsModal
          title="Financial Reports"
          fields={[
            { type: 'radio', key: 'reportType', label: 'Report', options: [{ value: 'balance_sheet', label: 'Balance Sheet' }, { value: 'income_statement', label: 'Income Statement' }, { value: 'trial_balance', label: 'Trial Balance' }], default: report },
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
          ]}
          onGenerate={generateFinancialReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}

function AccountBlock({ title, color, accounts, balances, fmt, total }) {
  const bg = color === 'emerald' ? 'bg-emerald-600' : 'bg-rose-600'
  return (
    <div>
      <div className={`${bg} text-white text-sm font-semibold px-3 py-2 rounded-t-lg`}>{title}</div>
      <div className="border border-t-0 border-slate-100 rounded-b-lg divide-y divide-slate-50">
        {accounts.map(a => (
          <Row key={a.id} label={`${a.code} - ${a.name}`} value={fmt(Math.abs(balances[a.id] || 0))} />
        ))}
        <Row label={`Total ${title.split(' ')[0]}`} value={fmt(Math.abs(total))} bold />
      </div>
    </div>
  )
}

function Row({ label, value, bold, large }) {
  return (
    <div className={`flex items-center justify-between px-3 py-2 ${bold ? 'font-bold text-slate-800' : 'text-slate-600'} ${large ? 'text-lg py-3' : 'text-sm'}`}>
      <span>{label}</span>
      <span>{value}</span>
    </div>
  )
}
