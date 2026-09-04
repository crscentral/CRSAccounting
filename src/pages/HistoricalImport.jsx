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

  // Hotel-only: 5-year Room Revenue actuals + Budget bulk import (separate template
  // and target tables from the generic ledger importer above -- these feed
  // hotel_room_stats and hotel_room_revenue_budget directly, not ledger_entries).
  const [hotelParsedActuals, setHotelParsedActuals] = useState([])
  const [hotelParsedBudget, setHotelParsedBudget] = useState([])
  const [hotelErrors, setHotelErrors] = useState([])
  const [hotelFileName, setHotelFileName] = useState('')
  const [hotelImporting, setHotelImporting] = useState(false)
  const [hotelResult, setHotelResult] = useState(null)
  const hotelFileInputRef = useRef(null)

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

  function downloadHotelTemplate() {
    const wb = XLSX.utils.book_new()
    const actualsSheet = XLSX.utils.aoa_to_sheet([
      ['Date (YYYY-MM-DD)', 'Rooms Occupied', 'Room Revenue', 'Amount Collected', 'Currency'],
      ['2025-04-01', 42, 5600, 5600, 'USD'],
    ])
    XLSX.utils.book_append_sheet(wb, actualsSheet, 'Room Revenue Actuals')
    const budgetSheet = XLSX.utils.aoa_to_sheet([
      ['Year', 'Month (1-12)', 'Budgeted Occupancy %', 'Budgeted ADR', 'Budgeted Room Revenue', 'Currency'],
      [2025, 4, 75, 130, 117000, 'USD'],
    ])
    XLSX.utils.book_append_sheet(wb, budgetSheet, 'Room Revenue Budget')
    XLSX.writeFile(wb, `hotel_5yr_import_template.xlsx`)
  }

  function handleHotelFileChange(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setHotelFileName(file.name)
    setHotelResult(null)
    const reader = new FileReader()
    reader.onload = (evt) => {
      const wb = XLSX.read(evt.target.result, { type: 'array' })
      const errors = []
      const actuals = []
      const budgetRows = []

      const actualsSheet = wb.Sheets['Room Revenue Actuals']
      if (actualsSheet) {
        const rows = XLSX.utils.sheet_to_json(actualsSheet, { header: 1, raw: false }).slice(1)
        rows.forEach((row, i) => {
          const [dateRaw, occRaw, revRaw, collectedRaw, currencyRaw] = row
          if (!dateRaw && !occRaw && !revRaw) return
          const date = normalizeDate(dateRaw)
          if (!date) { errors.push(`Room Revenue Actuals row ${i + 2}: invalid date.`); return }
          const revenue = parseFloat(revRaw)
          if (!revenue || revenue <= 0) { errors.push(`Room Revenue Actuals row ${i + 2}: Room Revenue must be a positive number.`); return }
          actuals.push({
            date, roomsOccupied: parseInt(occRaw) || 0, revenue,
            collected: parseFloat(collectedRaw) || revenue,
            currency: String(currencyRaw || 'USD').trim().toUpperCase() || 'USD',
          })
        })
      }

      const budgetSheet = wb.Sheets['Room Revenue Budget']
      if (budgetSheet) {
        const rows = XLSX.utils.sheet_to_json(budgetSheet, { header: 1, raw: false }).slice(1)
        rows.forEach((row, i) => {
          const [yearRaw, monthRaw, occRaw, adrRaw, revRaw, currencyRaw] = row
          if (!yearRaw && !monthRaw && !revRaw) return
          const year = parseInt(yearRaw), month = parseInt(monthRaw)
          if (!year || !month || month < 1 || month > 12) { errors.push(`Room Revenue Budget row ${i + 2}: invalid year/month.`); return }
          budgetRows.push({
            year, month, occ: parseFloat(occRaw) || 0, adr: parseFloat(adrRaw) || 0, revenue: parseFloat(revRaw) || 0,
            currency: String(currencyRaw || 'USD').trim().toUpperCase() || 'USD',
          })
        })
      }

      if (!actualsSheet && !budgetSheet) errors.push('No "Room Revenue Actuals" or "Room Revenue Budget" sheet found -- use the downloaded template as-is.')
      setHotelParsedActuals(actuals)
      setHotelParsedBudget(budgetRows)
      setHotelErrors(errors)
    }
    reader.readAsArrayBuffer(file)
  }

  async function confirmHotelImport() {
    setHotelImporting(true)
    try {
      const rateCache = { USD: 1 }
      const rateFor = async (c) => { if (!(c in rateCache)) rateCache[c] = (await getLatestRate(c)) || 1; return rateCache[c] }

      for (const row of hotelParsedActuals) {
        const rate = await rateFor(row.currency)
        await supabase.from('hotel_room_stats').upsert({
          company_id: activeCompany.id, product: activeProduct, stat_date: row.date, rooms_occupied: row.roomsOccupied,
          currency: row.currency, fx_rate_locked: rate,
          room_revenue: row.revenue, room_revenue_collected: row.collected,
          room_revenue_usd: Math.round(row.revenue / rate * 100) / 100,
          room_revenue_collected_usd: Math.round(row.collected / rate * 100) / 100,
        }, { onConflict: 'company_id,product,stat_date' })
      }

      for (const row of hotelParsedBudget) {
        const rate = await rateFor(row.currency)
        await supabase.from('hotel_room_revenue_budget').upsert({
          company_id: activeCompany.id, product: activeProduct, budget_year: row.year, budget_month: row.month,
          budgeted_occupancy_pct: row.occ, budgeted_adr: row.adr, budgeted_room_revenue: row.revenue,
          currency: row.currency, fx_rate_locked: rate, budgeted_room_revenue_usd: Math.round(row.revenue / rate * 100) / 100,
        }, { onConflict: 'company_id,product,budget_year,budget_month' })
      }

      setHotelResult({ success: true, actualsCount: hotelParsedActuals.length, budgetCount: hotelParsedBudget.length })
      setHotelParsedActuals([]); setHotelParsedBudget([]); setHotelErrors([]); setHotelFileName('')
      if (hotelFileInputRef.current) hotelFileInputRef.current.value = ''
    } catch (err) {
      setHotelResult({ success: false, message: err.message })
    } finally {
      setHotelImporting(false)
    }
  }

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

      {activeProduct === 'hotel' && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mb-6">
          <h3 className="font-semibold text-slate-700 mb-2">Hotel: 5-Year Room Revenue &amp; Budget Import</h3>
          <p className="text-sm text-slate-500 mb-4">
            Separate from the generic import above — this template has two sheets: "Room Revenue Actuals" (day-by-day Rooms Occupied, Room Revenue, Amount Collected) and "Room Revenue Budget" (month-by-month Occupancy %, ADR, Budgeted Revenue). Fill in up to 5 years of history in either or both sheets.
          </p>
          <button onClick={downloadHotelTemplate} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400 mb-4">
            <Download size={15} /> Download Hotel Template
          </button>

          {can(['owner', 'admin', 'accountant']) && (
            <>
              <input ref={hotelFileInputRef} type="file" accept=".xlsx,.xls" onChange={handleHotelFileChange}
                className="block w-full text-sm text-slate-600 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-navy-600 file:text-white file:text-sm file:font-medium hover:file:bg-navy-700" />

              {hotelErrors.length > 0 && (
                <div className="mt-4 bg-red-50 border border-red-100 rounded-lg p-3">
                  <div className="flex items-center gap-2 text-red-700 text-sm font-medium mb-1"><AlertTriangle size={15} /> {hotelErrors.length} row(s) had problems and were skipped:</div>
                  <ul className="text-xs text-red-600 space-y-0.5 max-h-32 overflow-y-auto">
                    {hotelErrors.map((e, i) => <li key={i}>{e}</li>)}
                  </ul>
                </div>
              )}

              {(hotelParsedActuals.length > 0 || hotelParsedBudget.length > 0) && (
                <div className="mt-4">
                  <div className="flex items-center gap-2 text-emerald-700 text-sm font-medium mb-3">
                    <CheckCircle2 size={15} /> {hotelParsedActuals.length} day(s) of actuals and {hotelParsedBudget.length} budget month(s) ready to import
                  </div>
                  <button onClick={confirmHotelImport} disabled={hotelImporting} className="bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-60">
                    {hotelImporting ? 'Importing…' : 'Import Hotel Data'}
                  </button>
                </div>
              )}

              {hotelResult && (
                <div className={`mt-4 rounded-lg p-3 text-sm ${hotelResult.success ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
                  {hotelResult.success ? `Imported ${hotelResult.actualsCount} day(s) of actuals and ${hotelResult.budgetCount} budget month(s).` : `Import failed: ${hotelResult.message}`}
                </div>
              )}
            </>
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
