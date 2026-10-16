/**
 * columns: [{ key, label, render?(row), className? }]
 * rows: array of objects
 * Below `md` breakpoint, renders each row as a labeled card instead of a horizontally-scrolling table.
 */
export default function DataTable({ columns, rows, keyField = 'id', emptyMessage = 'No records found.', footer, footerRow, compact = false, filterRow }) {
  if (!filterRow && (!rows || rows.length === 0)) {
    return <div className="text-center text-slate-400 text-sm py-10 bg-white rounded-xl border border-slate-200">{emptyMessage}</div>
  }

  const padClass = compact ? 'px-2.5 py-2 text-xs' : 'px-4 py-3'
  const isEmpty = !rows || rows.length === 0

  return (
    <>
      {/* Desktop / tablet table */}
      <div className="hidden md:block overflow-x-auto bg-white rounded-xl border border-slate-200">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              {columns.map(col => (
                <th
                  key={col.key}
                  className={`font-semibold text-slate-500 whitespace-nowrap ${padClass} ${col.align === 'right' ? 'text-right' : 'text-left'} ${col.className || ''}`}
                >
                  {col.label}
                </th>
              ))}
            </tr>
            {filterRow && (
              <tr className="border-b border-slate-200 bg-slate-50/70">
                {filterRow}
              </tr>
            )}
          </thead>
          <tbody>
            {isEmpty ? (
              <tr>
                <td colSpan={columns.length} className="text-center text-slate-400 text-sm py-12 bg-white">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              rows.map(row => (
                <tr key={row[keyField]} className="border-b border-slate-100 last:border-0 hover:bg-slate-50">
                  {columns.map(col => (
                    <td
                      key={col.key}
                      className={`align-middle ${padClass} ${col.align === 'right' ? 'text-right' : ''} ${col.className || ''}`}
                    >
                      {col.render ? col.render(row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
          {(footerRow || footer) && !isEmpty && (
            <tfoot>
              <tr className="border-t-2 border-slate-200 bg-slate-50 font-semibold text-slate-700">
                {footerRow || (
                  <td colSpan={columns.length} className={`${padClass} text-right`}>
                    {footer}
                  </td>
                )}
              </tr>
            </tfoot>
          )}
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
        {footer && !isEmpty && (
          <div className="bg-slate-50 rounded-xl border border-slate-200 p-4 text-right font-semibold text-slate-700 text-sm">
            {footer}
          </div>
        )}
      </div>
    </>
  )
}
