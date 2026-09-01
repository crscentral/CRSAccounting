import { useEffect, useRef, useState } from 'react'
import * as XLSX from 'xlsx'
import { Upload, Download, CheckCircle2, AlertTriangle, Trash2 } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { getLatestRate } from '../lib/fx'
import PageHeader from '../components/PageHeader'
import DataTable from '../components/DataTable'
import ReportOptionsModal, { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../components/ReportOptionsModal'

const TEMPLATE_HEADERS = ['Date (YYYY-MM-DD)', 'Account Code', 'Debit Amount', 'Credit Amount', 'Currency', 'Description']

export default function HistoricalImport() {
  const { activeCompany, activeProduct, user, can } = useAuth()
  const [accounts, setAccounts] = useState([])
  const [imports, setImports] = useState([])
  const [parsedRows, setParsedRows] = useState([])
  const [errors, setErrors] = useState([])
  const [fileName, setFileName] = useState('')
  const [importing, setImporting] = useState(false)
  const [result, setResult] = useState(null)
  const [reportModalOpen, setReportModalOpen] = useState(false)
  const fileInputRef = useRef(null)

  useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct])

  function generateImportsReport(selections, format) {
    const sections = [{
      heading: 'Import History',
      columns: ['Imported', 'File', 'Entries'],
      rows: imports.map(i => [new Date(i.created_at).toLocaleDateString(), i.filename || '—', i.row_count]),
    }]
    const title = 'Historical Data Imports'
    const subtitle = `${activeCompany.name} • ${imports.length} import(s) on record`
    if (format === 'pdf') exportMultiSectionPDF({ title, subtitle, sections, filename: 'historical_imports_log' })
    if (format === 'excel') exportMultiSectionExcel({ title, sections, filename: 'historical_imports_log' })
    if (format === 'word') exportMultiSectionWord({ title, subtitle, sections, filename: 'historical_imports_log' })
  }

  async function loadAll() {
    const [{ data: acc }, { data: imp }] = await Promise.all([
      supabase.from('accounts').select('id, code, name, type, subtype').eq('company_id', activeCompany.id).eq('product', activeProduct).order('code'),
      supabase.from('historical_imports').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).order('created_at', { ascending: false }),
    ])
    setAccounts(acc || [])
    setImports(imp || [])
  }

  function downloadTemplate() {
    const wb = XLSX.utils.book_new()
    const templateSheet = XLSX.utils.aoa_to_sheet([TEMPLATE_HEADERS, ['2025-04-01', accounts[0]?.code || '4010', '', '15000', 'USD', 'Example: April revenue']])
    XLSX.utils.book_append_sheet(wb, templateSheet, 'Import Data')

    const refSheet = XLSX.utils.aoa_to_sheet([
      ['Code', 'Name', 'Type', 'Subtype'],
      ...accounts.map(a => [a.code, a.name, a.type, a.subtype || '']),
    ])
    XLSX.utils.book_append_sheet(wb, refSheet, 'Your Chart of Accounts')
    XLSX.writeFile(wb, `historical_import_template_${activeProduct}.xlsx`)
  }

  function handleFileChange(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setFileName(file.name)
    setResult(null)
    const reader = new FileReader()
    reader.onload = (evt) => {
      const wb = XLSX.read(evt.target.result, { type: 'array' })
      const sheet = wb.Sheets[wb.SheetNames[0]]
      const rows = XLSX.utils.sheet_to_json(sheet, { header: 1, raw: false })
      parseRows(rows)
    }
    reader.readAsArrayBuffer(file)
  }

  function parseRows(rows) {
    const accountByCode = {}
    accounts.forEach(a => { accountByCode[String(a.code).trim()] = a })

    const dataRows = rows.slice(1) // skip header row
    const valid = []
    const rowErrors = []

    dataRows.forEach((row, i) => {
      const rowNum = i + 2 // account for header + 1-indexing
      const [dateRaw, codeRaw, debitRaw, creditRaw, currencyRaw, description] = row
      if (!dateRaw && !codeRaw && !debitRaw && !creditRaw) return // blank row, skip silently

      const date = normalizeDate(dateRaw)
      const code = String(codeRaw || '').trim()
      const debit = parseFloat(debitRaw) || 0
      const credit = parseFloat(creditRaw) || 0
      const currency = String(currencyRaw || 'USD').trim().toUpperCase() || 'USD'

      if (!date) { rowErrors.push(`Row ${rowNum}: invalid or missing date.`); return }
      if (!accountByCode[code]) { rowErrors.push(`Row ${rowNum}: account code "${code}" not found in your Chart of Accounts.`); return }
      if (debit === 0 && credit === 0) { rowErrors.push(`Row ${rowNum}: needs a Debit or Credit amount.`); return }

      valid.push({ date, account: accountByCode[code], debit, credit, currency, description: description || '' })
    })

    setParsedRows(valid)
    setErrors(rowErrors)
  }

  function normalizeDate(raw) {
    if (!raw) return null
    const s = String(raw).trim()
    if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s
    const d = new Date(s)
    if (isNaN(d.getTime())) return null
    return d.toISOString().slice(0, 10)
  }

  async function confirmImport() {
    if (parsedRows.length === 0) return
    setImporting(true)
    try {
      const { data: batch, error: batchErr } = await supabase.from('historical_imports').insert({
        company_id: activeCompany.id, product: activeProduct, filename: fileName, row_count: parsedRows.length, imported_by: user?.id,
      }).select().single()
      if (batchErr) throw batchErr

      const rateCache = { USD: 1 }
      const entries = []
      for (const row of parsedRows) {
        if (!(row.currency in rateCache)) rateCache[row.currency] = (await getLatestRate(row.currency)) || 1
        const rate = rateCache[row.currency]
        entries.push({
          company_id: activeCompany.id, product: activeProduct, account_id: row.account.id,
          entry_date: row.date, description: row.description || `Historical import - ${row.account.name}`,
          currency: row.currency, fx_rate_locked: rate,
          debit_usd: Math.round((row.debit / rate) * 100) / 100,
          credit_usd: Math.round((row.credit / rate) * 100) / 100,
          source_type: 'historical_import', source_id: batch.id,
        })
      }

      const chunkSize = 200
      for (let i = 0; i < entries.length; i += chunkSize) {
        const { error: insertErr } = await supabase.from('ledger_entries').insert(entries.slice(i, i + chunkSize))
        if (insertErr) throw insertErr
      }

      setResult({ success: true, count: entries.length })
      setParsedRows([]); setErrors([]); setFileName('')
      if (fileInputRef.current) fileInputRef.current.value = ''
      loadAll()
    } catch (err) {
      setResult({ success: false, message: err.message })
    } finally {
      setImporting(false)
    }
  }

  async function handleDeleteImport(imp) {
    if (!confirm(`Delete this import (${imp.row_count} entries from ${imp.filename})? This removes all its ledger entries too. This cannot be undone.`)) return
    const { error } = await supabase.from('historical_imports').delete().eq('id', imp.id)
    if (error) { alert('Could not delete: ' + error.message); return }
    loadAll()
  }

  if (!activeCompany) return null

  return (
    <div>
      <PageHeader
        title="Import Historical Data"
        subtitle={`${activeCompany.name} • Bring in past-year figures so you can compare them against current and future data`}
        actions={
          <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
            Download Report
          </button>
        }
      />

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
        <h3 className="font-semibold text-slate-700 mb-2">1. Download the template</h3>
        <p className="text-sm text-slate-500 mb-4">
          The template includes a second sheet listing your current Chart of Accounts codes, so you know exactly what to type in the "Account Code" column. One row = one amount against one account, on one date.
        </p>
        <button onClick={downloadTemplate} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
          <Download size={15} /> Download Template
        </button>
      </div>

      {can(['owner', 'admin', 'accountant']) && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
          <h3 className="font-semibold text-slate-700 mb-2">2. Upload your filled-in file</h3>
          <input ref={fileInputRef} type="file" accept=".xlsx,.xls" onChange={handleFileChange}
            className="block w-full text-sm text-slate-600 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-navy-600 file:text-white file:text-sm file:font-medium hover:file:bg-navy-700" />

          {errors.length > 0 && (
            <div className="mt-4 bg-red-50 border border-red-100 rounded-lg p-3">
              <div className="flex items-center gap-2 text-red-700 text-sm font-medium mb-1"><AlertTriangle size={15} /> {errors.length} row(s) had problems and were skipped:</div>
              <ul className="text-xs text-red-600 space-y-0.5 max-h-32 overflow-y-auto">
                {errors.map((e, i) => <li key={i}>{e}</li>)}
              </ul>
            </div>
          )}

          {parsedRows.length > 0 && (
            <div className="mt-4">
              <div className="flex items-center gap-2 text-emerald-700 text-sm font-medium mb-3">
                <CheckCircle2 size={15} /> {parsedRows.length} row(s) ready to import
              </div>
              <div className="max-h-64 overflow-y-auto border border-slate-200 rounded-lg mb-3">
                <table className="w-full text-xs">
                  <thead className="bg-slate-50 sticky top-0"><tr>
                    <th className="text-left px-3 py-2">Date</th><th className="text-left px-3 py-2">Account</th>
                    <th className="text-left px-3 py-2">Debit</th><th className="text-left px-3 py-2">Credit</th><th className="text-left px-3 py-2">Currency</th>
                  </tr></thead>
                  <tbody>
                    {parsedRows.slice(0, 50).map((r, i) => (
                      <tr key={i} className="border-t border-slate-100">
                        <td className="px-3 py-1.5">{r.date}</td>
                        <td className="px-3 py-1.5">{r.account.code} - {r.account.name}</td>
                        <td className="px-3 py-1.5">{r.debit || '—'}</td>
                        <td className="px-3 py-1.5">{r.credit || '—'}</td>
                        <td className="px-3 py-1.5">{r.currency}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {parsedRows.length > 50 && <p className="text-center text-xs text-slate-400 py-2">…and {parsedRows.length - 50} more</p>}
              </div>
              <button onClick={confirmImport} disabled={importing} className="bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-60">
                {importing ? 'Importing…' : `Import ${parsedRows.length} Entries`}
              </button>
            </div>
          )}

          {result && (
            <div className={`mt-4 rounded-lg p-3 text-sm ${result.success ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
              {result.success ? `Imported ${result.count} entries successfully.` : `Import failed: ${result.message}`}
            </div>
          )}
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6">
        <h3 className="font-semibold text-slate-700 mb-4">Past Imports</h3>
        <DataTable
          columns={[
            { key: 'created_at', label: 'Imported', render: r => new Date(r.created_at).toLocaleDateString() },
            { key: 'filename', label: 'File', render: r => r.filename || '—' },
            { key: 'row_count', label: 'Entries' },
            ...(can(['owner', 'admin', 'accountant']) ? [{
              key: 'actions', label: '', render: r => <button onClick={() => handleDeleteImport(r)} className="text-slate-400 hover:text-red-600"><Trash2 size={15} /></button>
            }] : []),
          ]}
          rows={imports}
          emptyMessage="No historical data imported yet."
        />
      </div>

      {reportModalOpen && (
        <ReportOptionsModal
          title="Historical Data Imports"
          fields={[]}
          onGenerate={generateImportsReport}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  )
}
