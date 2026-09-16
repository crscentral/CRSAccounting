import re

with open('src/components/DataTable.jsx', 'r') as f:
    code = f.read()

# Add footer prop
code = code.replace(
    "export default function DataTable({ columns, rows, keyField = 'id', emptyMessage = 'No records found.' }) {",
    "export default function DataTable({ columns, rows, keyField = 'id', emptyMessage = 'No records found.', footer }) {"
)

# Add footer rendering
old_desktop = """          </tbody>
        </table>
      </div>"""

new_desktop = """          </tbody>
          {footer && (
            <tfoot>
              <tr className="border-t-2 border-slate-200 bg-slate-50 font-semibold text-slate-700">
                <td colSpan={columns.length} className="px-4 py-3 text-right">
                  {footer}
                </td>
              </tr>
            </tfoot>
          )}
        </table>
      </div>"""
code = code.replace(old_desktop, new_desktop)

old_mobile = """            ))}
          </div>
        ))}
      </div>
    </>"""

new_mobile = """            ))}
          </div>
        ))}
        {footer && (
          <div className="bg-slate-50 rounded-xl border border-slate-200 p-4 text-right font-semibold text-slate-700 text-sm">
            {footer}
          </div>
        )}
      </div>
    </>"""
code = code.replace(old_mobile, new_mobile)

with open('src/components/DataTable.jsx', 'w') as f:
    f.write(code)
