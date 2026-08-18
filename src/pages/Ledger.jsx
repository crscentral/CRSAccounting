import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { resolveReportPeriod } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

export default function Ledger() {
  const { activeCompany } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [accounts, setAccounts] = useState([])
  const [accountId, setAccountId] = useState('')
  const [entries, setEntries] = useState([])
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadAccounts() }, [activeCompany])
  useEffect(() => { if (accountId) loadEntries() }, [accountId, cp.range.from, cp.range.to])

  async function loadAccounts() {
    const { data } = await supabase.from('accounts').select('*').eq('company_id', activeCompany.id).order('code')
    setAccounts(data || [])
    if (data && data.length > 0) setAccountId(data.find(a => a.code === '4010')?.id || data[0].id)
  }

  async function loadEntries() {
    const { data } = await supabase
      .from('ledger_entries')
      .select('*')
      .eq('company_id', activeCompany.id)
      .eq('account_id', accountId)
      .gte('entry_date', cp.range.from)
      .lte('entry_date', cp.range.to)
      .order('entry_date')
    setEntries(data || [])
  }

  async function generateLedgerReport(selections, format) {
    const range = resolveReportPeriod(selections.period, activeCompany.fiscal_year_start_month || 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const fmt = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const account = accounts.find(a => a.id === selections.account)
    const { data } = await supabase.from('ledger_entries').select('*').eq('company_id', activeCompany.id).eq('account_id', selections.account)
      .gte('entry_date', range.from).lte('entry_date', range.to).order('entry_date')

    let running = 0
    const rows = (data || []).map(e => {
      running += Number(e.debit_usd) - Number(e.credit_usd)
      return [e.entry_date, e.description, e.currency, Number(e.debit_usd) ? fmt(e.debit_usd) : '—', Number(e.credit_usd) ? fmt(e.credit_usd) : '—', fmt(running)]
    })
    const totalDebit = (data || []).reduce((s, e) => s + Number(e.debit_usd), 0)
    const totalCredit = (data || []).reduce((s, e) => s + Number(e.credit_usd), 0)

    const sections = [{
      heading: account ? `${account.code} - ${account.name}` : 'Account Ledger',
      columns: ['Date', 'Description', 'Orig. Currency', `Debit (${selections.currency})`, `Credit (${selections.currency})`, `Balance (${selections.currency})`],
      rows,
    }, {
      heading: 'Totals',
      keyValuePairs: [[`Total Debit (${selections.currency})`, fmt(totalDebit)], [`Total Credit (${selections.currency})`, fmt(totalCredit)]],
    }]

    const title = 'Account Ledger'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'account_ledger_report' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'account_ledger_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'account_ledger_report' })
  }

  if (!activeCompany) return null

  let running = 0
  const withBalance = entries.map(e => {
    running += Number(e.debit_usd) - Number(e.credit_usd)
    return { ...e, balance: running }
  })
  const totalDebit = entries.reduce((s, e) => s + Number(e.debit_usd), 0)
  const totalCredit = entries.reduce((s, e) => s + Number(e.credit_usd), 0)

  return (
    <div>
      <PageHeader
        title="Account Ledger"
        subtitle={activeCompany.name}
        currencyProps={cp.currencyProps}
        actions={
          <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
            Download Report
          </button>
        }
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 mb-5 grid sm:grid-cols-3 gap-3">
        <div>
          <label className="text-xs font-medium text-slate-500">Select Account</label>
          <select value={accountId} onChange={e => setAccountId(e.target.value)}
            className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
            {accounts.map(a => <option key={a.id} value={a.id}>{a.code} - {a.name}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs font-medium text-slate-500">From Date</label>
          <input type="date" value={cp.periodProps.customFrom || cp.range.from} onChange={e => cp.periodProps.onCustomChange({ from: e.target.value, to: cp.range.to })}
            className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="text-xs font-medium text-slate-500">To Date</label>
          <input type="date" value={cp.periodProps.customTo || cp.range.to} onChange={e => cp.periodProps.onCustomChange({ from: cp.range.from, to: e.target.value })}
            className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
        </div>
      </div>

      <DataTable
        columns={[
          { key: 'entry_date', label: 'Date' },
          { key: 'description', label: 'Description' },
          { key: 'currency', label: 'Orig. Currency' },
          { key: 'debit_usd', label: `Debit (${cp.displayCurrency})`, render: r => Number(r.debit_usd) ? cp.fmt(r.debit_usd) : '—' },
          { key: 'credit_usd', label: `Credit (${cp.displayCurrency})`, render: r => Number(r.credit_usd) ? cp.fmt(r.credit_usd) : '—' },
          { key: 'balance', label: `Balance (${cp.displayCurrency})`, render: r => cp.fmt(r.balance) },
        ]}
        rows={withBalance}
        emptyMessage="No ledger entries in this range."
      />

      {entries.length > 0 && (
        <div className="flex justify-end gap-8 mt-4 px-2 text-sm font-semibold text-slate-600">
          <span>Total Debit: {cp.fmt(totalDebit)}</span>
          <span>Total Credit: {cp.fmt(totalCredit)}</span>
        </div>
      )}

      {reportModalOpen && (
        <ReportOptionsModal
          title="Account Ledger"
          fields={[
            { type: 'select', key: 'account', label: 'Account', options: accounts.map(a => ({ value: a.id, label: `${a.code} - ${a.name}` })), default: accountId },
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
          ]}
          onGenerate={generateLedgerReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
