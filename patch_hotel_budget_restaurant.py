import re

with open('src/pages/HotelBudget.jsx', 'r') as f:
    content = f.read()

# Fix fetchAncillaryAccounts
old_fetch = "const { data } = await supabase.from('accounts').select('code, name, subtype').eq('company_id', activeCompany.id).eq('product', 'hotel').eq('type', 'Revenue').neq('code', '4010').order('subtype', { ascending: true }).order('code', { ascending: true })"
new_fetch = """      let query = supabase.from('accounts').select('code, name, subtype').eq('company_id', activeCompany.id).eq('product', activeProduct).eq('type', 'Revenue').order('subtype', { ascending: true }).order('code', { ascending: true })
      if (activeProduct === 'hotel') query = query.neq('code', '4010')
      const { data } = await query"""
content = content.replace(old_fetch, new_fetch)

# Fix loadAncillary ledger fetch
old_ledger = "supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue').neq('accounts.code', '4010')"
new_ledger = """supabase.from('ledger_entries').select('debit_usd, credit_usd, entry_date, accounts!inner(code, type)').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('entry_date', `${startYear}-01-01`).lte('entry_date', `${startYear}-12-31`).eq('accounts.type', 'Revenue')"""
content = content.replace(old_ledger, new_ledger)
# But wait, if I remove neq 4010, then for Hotel, it will fetch 4010 into ancillaryActuals? But we filter by aMap matching ancillaryAccounts, and 4010 is not in ancillaryAccounts for Hotel. So it's safe.

# Fix revenueSummary to include 4010 if restaurant
old_rev_summary = """    for (let m = 1; m <= 12; m++) {
      for (const a of ancillaryAccounts) {
        const k = `${a.code}-${m}`
        const amt = ancillaryBudgets[k] ? (Number(ancillaryBudgets[k].amount_usd) || 0) : 0
        if (a.subtype === 'Front Office') frontOffice += amt
        else if (a.subtype === 'F&B Service') fbService += amt
        else otherRev += amt
      }
    }"""
new_rev_summary = """    for (let m = 1; m <= 12; m++) {
      for (const a of ancillaryAccounts) {
        const k = `${a.code}-${m}`
        const amt = ancillaryBudgets[k] ? (Number(ancillaryBudgets[k].amount_usd) || 0) : 0
        if (a.subtype === 'Front Office' || (activeProduct === 'restaurant' && (a.code === '4010' || a.subtype === 'F&B Revenue' || a.subtype === 'Sales'))) frontOffice += amt
        else if (a.subtype === 'F&B Service') fbService += amt
        else otherRev += amt
      }
    }"""
content = content.replace(old_rev_summary, new_rev_summary)

# Hide Seat Inventory if restaurant
content = content.replace(
    """<div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6">
        <h3 className="font-semibold text-slate-800 mb-2">{activeProduct === "restaurant" ? "Seat Inventory" : "Room Inventory"}</h3>""",
    """{activeProduct === 'hotel' && (<div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6">
        <h3 className="font-semibold text-slate-800 mb-2">{activeProduct === "restaurant" ? "Seat Inventory" : "Room Inventory"}</h3>"""
)
content = content.replace(
    """<button disabled={savingRooms} onClick={saveTotalRooms} className="bg-navy-600 hover:bg-navy-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2">
            <Save size={16} /> Save
          </button>
        </div>
      </div>""",
    """<button disabled={savingRooms} onClick={saveTotalRooms} className="bg-navy-600 hover:bg-navy-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2">
            <Save size={16} /> Save
          </button>
        </div>
      </div>)}"""
)

# Hide the Top Table if restaurant
content = content.replace(
    """<div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mb-8">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">""",
    """{activeProduct === 'hotel' && (<div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mb-8">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">"""
)
content = content.replace(
    """</tbody>
          </table>
        </div>
      </div>

      <div className="mb-4">
        <div className="flex items-center gap-3">""",
    """</tbody>
          </table>
        </div>
      </div>)}

      <div className="mb-4">
        <div className="flex items-center gap-3">"""
)

# Rename the bottom table heading
content = content.replace(
    """<h2 className="text-lg font-bold text-slate-800">{startYear} Other Revenue vs Actuals</h2>""",
    """<h2 className="text-lg font-bold text-slate-800">{activeProduct === 'restaurant' ? `${startYear} - F&B Revenue & Actual` : `${startYear} Other Revenue vs Actuals`}</h2>"""
)


with open('src/pages/HotelBudget.jsx', 'w') as f:
    f.write(content)
