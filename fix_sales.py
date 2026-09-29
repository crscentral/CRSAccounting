import re

def patch():
    with open('src/pages/SalesInvoices.jsx', 'r') as f:
        content = f.read()

    summary_block = """
          <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 mt-6">
            <h3 className="font-semibold text-slate-700 mb-4">Invoice Currency Summary</h3>
            <div className="space-y-3">
              {Object.entries(byCurrency).map(([code, v]) => (
                <div key={code} className="flex items-center justify-between text-sm">
                  <div>
                    <span className="inline-block px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-medium mr-2">{code}</span>
                    <span className="text-slate-500">{v.native.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} • {v.count} invoice(s)</span>
                  </div>
                  <span className="font-semibold text-slate-700">{cp.fmt(v.usd)}</span>
                </div>
              ))}
              <div className="flex items-center justify-between pt-3 border-t border-slate-100 font-bold text-emerald-700">
                <span>Grand Total ({cp.displayCurrency})</span>
                <span>{cp.fmt(totalUsd)}</span>
              </div>
            </div>
          </div>
"""

    if summary_block in content:
        content = content.replace(summary_block, "")
        
        # We want to insert it right after the StatBox grid, inside the tab === 'invoices' condition
        insert_target = """      {tab === 'invoices' ? (
        <>"""
        
        new_summary_block = summary_block.replace('mt-6', 'mb-6').replace('\n          <div', '\n          <div')
        
        content = content.replace(insert_target, insert_target + new_summary_block)
        
        with open('src/pages/SalesInvoices.jsx', 'w') as f:
            f.write(content)
        print("Patched SalesInvoices.jsx")
    else:
        print("Could not find summary block")

patch()
