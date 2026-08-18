/**
 * columns: [{ key, label, render?(row), className? }]
 * rows: array of objects
 * Below `md` breakpoint, renders each row as a labeled card instead of a horizontally-scrolling table.
 */
export default function DataTable({ columns, rows, keyField = 'id', emptyMessage = 'No records found.' }) {
  if (!rows || rows.length === 0) {
    return <div className="text-center text-slate-400 text-sm py-10 bg-white rounded-xl border border-slate-200">{emptyMessage}</div>
  }

  return (
    <>
      {/* Desktop / tablet table */}
      <div className="hidden md:block overflow-x-auto bg-white rounded-xl border border-slate-200">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              {columns.map(col => (
                <th key={col.key} className={`text-left font-semibold text-slate-500 px-4 py-3 whitespace-nowrap ${col.className || ''}`}>
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map(row => (
              <tr key={row[keyField]} className="border-b border-slate-100 last:border-0 hover:bg-slate-50">
                {columns.map(col => (
                  <td key={col.key} className={`px-4 py-3 align-middle ${col.className || ''}`}>
                    {col.render ? col.render(row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile stacked cards */}
      <div className="md:hidden space-y-3">
        {rows.map(row => (
          <div key={row[keyField]} className="bg-white rounded-xl border border-slate-200 p-4 space-y-2">
            {columns.map(col => (
              <div key={col.key} className="flex items-start justify-between gap-3 text-sm">
                <span className="text-slate-400 shrink-0">{col.label}</span>
                <span className="text-slate-700 text-right">{col.render ? col.render(row) : row[col.key]}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </>
  )
}
