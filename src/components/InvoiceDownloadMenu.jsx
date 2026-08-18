import { useState, useRef, useEffect } from 'react'
import { Download, FileText, FileSpreadsheet, FileType, Loader2 } from 'lucide-react'
import { exportInvoicePDF, exportInvoiceExcel, exportInvoiceWord } from '../lib/exportUtils'

/**
 * Renders invoice download options, gated by role:
 * - owner / admin: dropdown with PDF, Excel, and Word
 * - accountant / viewer: a single button, PDF only (no dropdown needed)
 *
 * `getData` is an async function returning { invoice, items, contact } -- items are
 * fetched lazily on click so list pages don't need to preload them for every row.
 */
export default function InvoiceDownloadMenu({ type, company, role, getData, iconOnly = false, triggerClassName }) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const ref = useRef(null)
  const pdfOnly = role === 'accountant' || role === 'viewer'

  useEffect(() => {
    function onClick(e) { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  async function run(fn) {
    setLoading(true)
    setOpen(false)
    try {
      const { invoice, items, contact } = await getData()
      await fn({ type, invoice, items, company, contact })
    } catch (err) {
      alert('Download failed: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  if (pdfOnly) {
    return (
      <button onClick={() => run(exportInvoicePDF)} disabled={loading} className={triggerClassName || 'text-slate-400 hover:text-navy-600 disabled:opacity-50'} title="Download PDF">
        {loading ? <Loader2 size={15} className="animate-spin" /> : <Download size={15} />}
      </button>
    )
  }

  return (
    <div className="relative" ref={ref}>
      <button onClick={() => setOpen(o => !o)} disabled={loading} className={triggerClassName || 'text-slate-400 hover:text-navy-600 disabled:opacity-50'} title="Download">
        {loading ? <Loader2 size={15} className="animate-spin" /> : (iconOnly ? <Download size={15} /> : <span className="flex items-center gap-1 text-xs font-medium"><Download size={15} /> Download</span>)}
      </button>
      {open && (
        <div className="absolute z-30 mt-1 right-0 w-44 bg-white border border-slate-200 rounded-lg shadow-lg py-1">
          <button onClick={() => run(exportInvoicePDF)} className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-navy-50">
            <FileText size={15} className="text-red-500" /> PDF
          </button>
          <button onClick={() => run(exportInvoiceExcel)} className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-navy-50">
            <FileSpreadsheet size={15} className="text-emerald-600" /> Excel
          </button>
          <button onClick={() => run(exportInvoiceWord)} className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-navy-50">
            <FileType size={15} className="text-blue-600" /> Word
          </button>
        </div>
      )}
    </div>
  )
}
