import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    code = f.read()

old_code = """      {years.map(year => (
        <div key={year} className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-5">
          <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{year}</div>
          <table className="w-full text-sm min-w-[720px]">"""

new_code = """      {years.map(year => (
        <div key={year} className="bg-white rounded-xl border border-slate-200 overflow-x-auto mb-5">
          <div className="min-w-[900px] w-full">
            <div className="px-4 py-2.5 bg-navy-700 text-white font-semibold text-sm">{year}</div>
            <table className="w-full text-sm">"""

code = code.replace(old_code, new_code)
code = code.replace('<table className="w-full text-sm min-w-[720px]">', '<table className="w-full text-sm">')

# close the div
old_close = """              </tbody>
            </table>
          </div>
        )
      })}"""

new_close = """              </tbody>
            </table>
            </div>
          </div>
        )
      })}"""
code = code.replace(old_close, new_close)

with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(code)
