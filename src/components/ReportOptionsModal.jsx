import { useState } from 'react'
import { X, FileText, FileSpreadsheet, FileType } from 'lucide-react'
import { CURRENCY_LIST } from '../lib/currencies'
import { MONTH_NAMES } from '../lib/fiscalYear'
import { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord } from '../lib/exportUtils'

const PERIOD_OPTIONS = [
  { value: 'MTD', label: 'This Month (MTD)' },
  { value: 'YTD', label: 'Year to Date (YTD)' },
  { value: 'LAST_1_YEAR', label: 'Last 1 Year' },
  { value: 'LAST_3_YEARS', label: 'Last 3 Years' },
  { value: 'CUSTOM', label: 'Custom Range' },
  { value: 'ALL_TIME', label: 'All Time' },
]

/**
 * fields: array of field configs, each one of:
 *   { type: 'currency', key: 'currency', default: 'USD' }
 *   { type: 'period', key: 'period', default: 'MTD', fiscalYearStartMonth }
 *   { type: 'radio', key: 'accountType', label: 'Account Type', options: ['All','Assets',...], default: 'All' }
 *   { type: 'checkboxGroup', key: 'sections', label: 'Include Sections', options: [...], default: [...] (all checked) }
 *
 * onGenerate(values, format) is called with the resolved field values plus the chosen
 * export format ('pdf' | 'excel' | 'word'); the calling page builds the actual report
 * sections from `values` and calls the matching exportMultiSection* function.
 */
export default function ReportOptionsModal({ title, fields, onGenerate, onClose }) {
  const initial = {}
  fields.forEach(f => { initial[f.key] = f.default })
  const [values, setValues] = useState(initial)
  const [customFrom, setCustomFrom] = useState('')
  const [customTo, setCustomTo] = useState('')
  const [generating, setGenerating] = useState(false)

  function update(key, val) { setValues(v => ({ ...v, [key]: val })) }

  function toggleCheckbox(key, option) {
    setValues(v => {
      const current = v[key] || []
      const next = current.includes(option) ? current.filter(o => o !== option) : [...current, option]
      return { ...v, [key]: next }
    })
  }

  async function handleGenerate(format) {
    setGenerating(true)
    try {
      const resolved = { ...values }
      if (resolved.period === 'CUSTOM') {
        resolved.customFrom = customFrom
        resolved.customTo = customTo
      }
      await onGenerate(resolved, format)
      onClose()
    } catch (err) {
      alert('Could not generate report: ' + err.message)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="bg-white rounded-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 sticky top-0 bg-white z-10">
          <h2 className="font-semibold text-slate-800">Download Report — {title}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600"><X size={20} /></button>
        </div>

        <div className="p-5 space-y-5">
          {fields.map(field => {
            if (field.type === 'currency') {
              return (
                <div key={field.key}>
                  <label className="text-xs font-medium text-slate-500">Currency</label>
                  <select value={values[field.key]} onChange={e => update(field.key, e.target.value)}
                    className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                    {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code} — {c.name}</option>)}
                  </select>
                </div>
              )
            }
            if (field.type === 'period') {
              return (
                <div key={field.key}>
                  <label className="text-xs font-medium text-slate-500">Period</label>
                  <select value={values[field.key]} onChange={e => update(field.key, e.target.value)}
                    className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                    {PERIOD_OPTIONS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
                  </select>
                  {values[field.key] === 'CUSTOM' && (
                    <div className="grid grid-cols-2 gap-2 mt-2">
                      <input type="date" value={customFrom} onChange={e => setCustomFrom(e.target.value)} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm" placeholder="From" />
                      <input type="date" value={customTo} onChange={e => setCustomTo(e.target.value)} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm" placeholder="To" />
                    </div>
                  )}
                </div>
              )
            }
            if (field.type === 'radio') {
              return (
                <div key={field.key}>
                  <label className="text-xs font-medium text-slate-500">{field.label}</label>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {field.options.map(opt => {
                      const optValue = typeof opt === 'string' ? opt : opt.value
                      const optLabel = typeof opt === 'string' ? opt : opt.label
                      return (
                        <button key={optValue} type="button" onClick={() => update(field.key, optValue)}
                          className={`px-3 py-1.5 rounded-full text-xs font-medium border ${values[field.key] === optValue ? 'bg-navy-600 text-white border-navy-600' : 'bg-white text-slate-600 border-slate-200'}`}>
                          {optLabel}
                        </button>
                      )
                    })}
                  </div>
                </div>
              )
            }
            if (field.type === 'checkboxGroup') {
              return (
                <div key={field.key}>
                  <label className="text-xs font-medium text-slate-500">{field.label}</label>
                  <div className="space-y-1.5 mt-1">
                    {field.options.map(opt => (
                      <label key={opt} className="flex items-center gap-2 text-sm text-slate-700">
                        <input type="checkbox" checked={(values[field.key] || []).includes(opt)} onChange={() => toggleCheckbox(field.key, opt)} />
                        {opt}
                      </label>
                    ))}
                  </div>
                </div>
              )
            }
            if (field.type === 'select') {
              return (
                <div key={field.key}>
                  <label className="text-xs font-medium text-slate-500">{field.label}</label>
                  <select value={values[field.key]} onChange={e => update(field.key, e.target.value)}
                    className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                    {field.options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>
              )
            }
            return null
          })}
        </div>

        <div className="p-5 border-t border-slate-100 grid grid-cols-3 gap-2 sticky bottom-0 bg-white">
          <button disabled={generating} onClick={() => handleGenerate('pdf')} className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg py-2.5 text-xs font-medium text-slate-600 hover:border-navy-400 disabled:opacity-50">
            <FileText size={18} className="text-red-500" /> PDF
          </button>
          <button disabled={generating} onClick={() => handleGenerate('excel')} className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg py-2.5 text-xs font-medium text-slate-600 hover:border-navy-400 disabled:opacity-50">
            <FileSpreadsheet size={18} className="text-emerald-600" /> Excel
          </button>
          <button disabled={generating} onClick={() => handleGenerate('word')} className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg py-2.5 text-xs font-medium text-slate-600 hover:border-navy-400 disabled:opacity-50">
            <FileType size={18} className="text-blue-600" /> Word
          </button>
        </div>
      </div>
    </div>
  )
}

export { exportMultiSectionPDF, exportMultiSectionExcel, exportMultiSectionWord }
