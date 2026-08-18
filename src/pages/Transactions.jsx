import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'
import { resolveReportPeriod } from '../lib/fiscalYear'
import { getLatestRate, convertFromUsd, formatMoney } from '../lib/fx'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

export default function Transactions() {
  const { activeCompany } = useAuth()
  const cp = useCurrencyAndPeriod()
  const [rows, setRows] = useState([])
  const [reportModalOpen, setReportModalOpen] = useState(false)

  useEffect(() => { if (activeCompany) loadData() }, [activeCompany, cp.range.from, cp.range.to])

  async function loadData() {
    const [{ data: si }, { data: pi }, { data: pr }] = await Promise.all([
      supabase.from('sales_invoices').select('id, invoice_number, invoice_date, amount_usd, currency, amount, contact:contacts(name)')
        .eq('company_id', activeCompany.id).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('purchase_invoices').select('id, invoice_number, invoice_date, amount_usd, currency, amount, supplier_name_freeform, contact:contacts(name)')
        .eq('company_id', activeCompany.id).gte('invoice_date', cp.range.from).lte('invoice_date', cp.range.to),
      supabase.from('payment_receipts').select('id, receipt_date, amount_usd, currency, amount')
        .eq('company_id', activeCompany.id).gte('receipt_date', cp.range.from).lte('receipt_date', cp.range.to),
    ])

    const combined = [
      ...(si || []).map(r => ({ id: `si-${r.id}`, date: r.invoice_date, type: 'Sales Invoice', desc: `${r.invoice_number} — ${r.contact?.name || ''}`, amount_usd: r.amount_usd, direction: 'in' })),
      ...(pi || []).map(r => ({ id: `pi-${r.id}`, date: r.invoice_date, type: 'Purchase Invoice', desc: `${r.invoice_number} — ${r.contact?.name || r.supplier_name_freeform || ''}`, amount_usd: r.amount_usd, direction: 'out' })),
      ...(pr || []).map(r => ({ id: `pr-${r.id}`, date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount_usd: r.amount_usd, direction: 'in' })),
    ].sort((a, b) => b.date.localeCompare(a.date))

    setRows(combined)
  }

  async function generateTransactionsReport(selections, format) {
    const range = resolveReportPeriod(selections.period, activeCompany.fiscal_year_start_month || 1, selections.customFrom, selections.customTo)
    const rate = selections.currency === 'USD' ? 1 : (await getLatestRate(selections.currency)) || 1
    const fmt = (usd) => formatMoney(convertFromUsd(usd, selections.currency, { [selections.currency]: rate }), selections.currency)

    const wantSales = selections.txType.includes('Sales Invoices')
    const wantPurchase = selections.txType.includes('Purchase Invoices')
    const wantReceipts = selections.txType.includes('Payment Receipts')

    const [{ data: si }, { data: pi }, { data: pr }] = await Promise.all([
      wantSales ? supabase.from('sales_invoices').select('invoice_number, invoice_date, amount_usd, contact:contacts(name)').eq('company_id', activeCompany.id).gte('invoice_date', range.from).lte('invoice_date', range.to) : Promise.resolve({ data: [] }),
      wantPurchase ? supabase.from('purchase_invoices').select('invoice_number, invoice_date, amount_usd, supplier_name_freeform, contact:contacts(name)').eq('company_id', activeCompany.id).gte('invoice_date', range.from).lte('invoice_date', range.to) : Promise.resolve({ data: [] }),
      wantReceipts ? supabase.from('payment_receipts').select('receipt_date, amount_usd').eq('company_id', activeCompany.id).gte('receipt_date', range.from).lte('receipt_date', range.to) : Promise.resolve({ data: [] }),
    ])

    const combined = [
      ...(si || []).map(r => ({ date: r.invoice_date, type: 'Sales Invoice', desc: `${r.invoice_number} — ${r.contact?.name || ''}`, amount: fmt(r.amount_usd), direction: '+' })),
      ...(pi || []).map(r => ({ date: r.invoice_date, type: 'Purchase Invoice', desc: `${r.invoice_number} — ${r.contact?.name || r.supplier_name_freeform || ''}`, amount: fmt(r.amount_usd), direction: '-' })),
      ...(pr || []).map(r => ({ date: r.receipt_date, type: 'Payment Receipt', desc: 'Payment received', amount: fmt(r.amount_usd), direction: '+' })),
    ].sort((a, b) => b.date.localeCompare(a.date))

    const sections = [{
      heading: 'Transactions',
      columns: ['Date', 'Type', 'Description', `Amount (${selections.currency})`],
      rows: combined.map(t => [t.date, t.type, t.desc, `${t.direction}${t.amount}`]),
    }]

    const title = 'Transactions'
    const subtitle = `${activeCompany.name} • ${range.from} to ${range.to} • ${selections.currency}`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'transactions_report' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'transactions_report' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'transactions_report' })
  }

  if (!activeCompany) return null

  return (
    <div>
      <PageHeader
        title="Transactions"
        subtitle={activeCompany.name}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
            Download Report
          </button>
        }
      />
      <DataTable
        columns={[
          { key: 'date', label: 'Date' },
          { key: 'type', label: 'Type' },
          { key: 'desc', label: 'Description' },
          {
            key: 'amount_usd', label: 'Amount', render: r => (
              <span className={r.direction === 'in' ? 'text-emerald-600 font-medium' : 'text-red-600 font-medium'}>
                {r.direction === 'in' ? '+' : '−'}{cp.fmt(r.amount_usd)}
              </span>
            )
          },
        ]}
        rows={rows}
      />

      {reportModalOpen && (
        <ReportOptionsModal
          title="Transactions"
          fields={[
            { type: 'checkboxGroup', key: 'txType', label: 'Transaction Types', options: ['Sales Invoices', 'Purchase Invoices', 'Payment Receipts'], default: ['Sales Invoices', 'Purchase Invoices', 'Payment Receipts'] },
            { type: 'currency', key: 'currency', default: cp.displayCurrency },
            { type: 'period', key: 'period', default: 'ALL_TIME' },
          ]}
          onGenerate={generateTransactionsReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
