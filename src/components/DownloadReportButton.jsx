import { useState, useRef, useEffect } from 'react'
import { Download, FileText, FileSpreadsheet, FileType } from 'lucide-react'
import { exportTableToPDF, exportTableToExcel, exportTableToWord } from '../lib/exportUtils'

/**
 * columns: [{ label, key }] -- key used to pull the value out of each row (supports dot-less flat values only；
 *          pass already-formatted display strings for money/dates so exports match what's on screen).
 * rows: array of plain objects
 */
export default function DownloadReportButton({ title, subtitle, columns, rows, filename }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    function onClick(e) { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  function getRows() {
    return rows.map(r => columns.map(c => r[c.key]))
  }
  function getCols() {
    return columns.map(c => c.label)
  }
  const safeFilename = (filename || title || 'report').replace(/[^a-z0-9-_]+/gi, '_')

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400"
      >
        <Download size={15} /> Download Report
      </button>
      {open && (
        <div className="absolute z-30 mt-1 right-0 w-52 bg-white border border-slate-200 rounded-lg shadow-lg py-1">
          <button
            onClick={() => { exportTableToPDF({ title, subtitle, columns: getCols(), rows: getRows(), filename: safeFilename }); setOpen(false) }}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-navy-50"
          >
            <FileText size={15} className="text-red-500" /> Download as PDF
          </button>
          <button
            onClick={() => { exportTableToExcel({ title, columns: getCols(), rows: getRows(), filename: safeFilename }); setOpen(false) }}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-navy-50"
          >
            <FileSpreadsheet size={15} className="text-emerald-600" /> Download as Excel
          </button>
          <button
            onClick={() => { exportTableToWord({ title, subtitle, columns: getCols(), rows: getRows(), filename: safeFilename }); setOpen(false) }}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-navy-50"
          >
            <FileType size={15} className="text-blue-600" /> Download as Word
          </button>
        </div>
      )}
    </div>
  )
}
