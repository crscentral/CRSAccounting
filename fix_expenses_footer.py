import re

with open('src/pages/HotelExpenses.jsx', 'r') as f:
    code = f.read()

# Fix Expense Entries footer
old_entries_head = """      <div className="flex justify-between items-end mb-3 mt-8">
        <div>
          <h3 className="font-semibold text-slate-700 flex items-center gap-3">
            <span>Expense Entries</span>
            {can(['owner', 'admin', 'accountant']) && (
              <button onClick={() => { setEditingRow(null); setNewHeadModalOpen(true); }} className="text-xs text-navy-600 hover:text-navy-800 font-medium">+ Add Expense Head</button>
            )}
          </h3>
        </div>
        <div className="text-sm text-slate-500 font-medium">
          Total Heads: {new Set(entries.map(e => e.account_id)).size} &bull; Total Amount: {cp.fmt(entriesTotalUsd)}
        </div>
      </div>"""

new_entries_head = """      <h3 className="font-semibold text-slate-700 mb-3 mt-8 flex items-center gap-3">
        <span>Expense Entries</span>
        {can(['owner', 'admin', 'accountant']) && (
          <button onClick={() => { setEditingRow(null); setNewHeadModalOpen(true); }} className="text-xs text-navy-600 hover:text-navy-800 font-medium">+ Add Expense Head</button>
        )}
      </h3>"""
code = code.replace(old_entries_head, new_entries_head)

old_entries_table = """        emptyMessage="No expense entries in this range."
      />"""
new_entries_table = """        emptyMessage="No expense entries in this range."
        footer={<span>Total Heads: {new Set(entries.map(e => e.account_id)).size} &nbsp;&bull;&nbsp; Total Amount: {cp.fmt(entriesTotalUsd)}</span>}
      />"""
code = code.replace(old_entries_table, new_entries_table)

# Fix AMC Contracts footer
old_amc_head = """      <div className="flex justify-between items-end mb-3 mt-10">
        <h3 className="font-semibold text-slate-700">AMC Contracts (auto-split across 12 months)</h3>
        <div className="text-sm text-slate-500 font-medium">
          Total Contracts: {amcContracts.length} &bull; Annual: {cp.fmt(amcContracts.reduce((s, r) => s + Number(r.annual_amount_usd), 0))} &bull; Monthly: {cp.fmt(amcMonthlyTotalUsd)}
        </div>
      </div>"""
new_amc_head = """      <h3 className="font-semibold text-slate-700 mb-3 mt-10">AMC Contracts (auto-split across 12 months)</h3>"""
code = code.replace(old_amc_head, new_amc_head)

old_amc_table = """        emptyMessage="No AMC contracts created yet."
      />"""
new_amc_table = """        emptyMessage="No AMC contracts created yet."
        footer={<span>Total Contracts: {amcContracts.length} &nbsp;&bull;&nbsp; Annual: {cp.fmt(amcContracts.reduce((s, r) => s + Number(r.annual_amount_usd), 0))} &nbsp;&bull;&nbsp; Monthly: {cp.fmt(amcMonthlyTotalUsd)}</span>}
      />"""
code = code.replace(old_amc_table, new_amc_table)


with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(code)
