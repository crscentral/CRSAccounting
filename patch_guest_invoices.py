import re

with open('src/pages/HotelGuestInvoices.jsx', 'r') as f:
    content = f.read()

# 1. Add useCurrencyAndPeriod
content = content.replace(
    "const { activeCompany, activeProduct, can } = useAuth()",
    "const { activeCompany, activeProduct, can } = useAuth()\n  const cp = useCurrencyAndPeriod('YTD')"
)

# 2. Remove manual displayCurrency and rate
content = re.sub(r"  const \[displayCurrency, setDisplayCurrency\] = useState\('USD'\)\n", "", content)
content = re.sub(r"  const \[rate, setRate\] = useState\(1\)\n", "", content)
content = re.sub(r"  useEffect\(\(\) => \{ if \(displayCurrency === 'USD'\) \{ setRate\(1\); return \} getLatestRate\(displayCurrency\).then\(r => setRate\(r \|\| 1\)\) \}, \[displayCurrency\]\)\n", "", content)

# 3. Update useEffect for loadAll to depend on cp.range
content = content.replace(
    "useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct])",
    "useEffect(() => { if (activeCompany) loadAll() }, [activeCompany, activeProduct, cp.range.from, cp.range.to])"
)

# 4. Update fmt function
content = content.replace(
    "function fmt(usd) { return formatMoney(convertFromUsd(usd, displayCurrency, { [displayCurrency]: rate }), displayCurrency) }",
    "const fmt = cp.fmt"
)

# 5. Update loadAll to fetch expanded bounds
old_loadall = """  async function loadAll() {
    const { data } = await supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', ytd.from).order('invoice_date', { ascending: false })
    setRows(data || [])
  }"""
new_loadall = """  async function loadAll() {
    const minFrom = cp.range.from < ytd.from ? cp.range.from : ytd.from
    const maxTo = cp.range.to > ytd.to ? cp.range.to : (cp.range.to === '9999-12-31' ? today : ytd.to)
    const { data } = await supabase.from('hotel_guest_invoices').select('*').eq('company_id', activeCompany.id).eq('product', activeProduct).gte('invoice_date', minFrom).lte('invoice_date', maxTo).order('invoice_date', { ascending: false })
    setRows(data || [])
  }"""
content = content.replace(old_loadall, new_loadall)

# 6. Update table rendering to use cpRows
old_filter = """  const todayRows = rows.filter(r => r.invoice_date === today)
  const mtdRows = rows.filter(r => r.invoice_date >= mtd.from && r.invoice_date <= mtd.to)
  const ytdRows = rows.filter(r => r.invoice_date >= ytd.from && r.invoice_date <= ytd.to)"""
new_filter = """  const todayRows = rows.filter(r => r.invoice_date === today)
  const mtdRows = rows.filter(r => r.invoice_date >= mtd.from && r.invoice_date <= mtd.to)
  const ytdRows = rows.filter(r => r.invoice_date >= ytd.from && r.invoice_date <= ytd.to)
  const cpRows = rows.filter(r => r.invoice_date >= cp.range.from && r.invoice_date <= cp.range.to)"""
content = content.replace(old_filter, new_filter)

# 7. Update report generation to use cpRows
content = content.replace(
    "rows: rows.map(r =>",
    "rows: cpRows.map(r =>"
)
content = content.replace(
    "const subtitle = `${activeCompany.name} • Year to date`",
    "const subtitle = `${activeCompany.name} • ${cp.range.from} to ${cp.range.to}`"
)

# 8. Update PageHeader
old_pageheader = """      <PageHeader
        title="Guest Invoices"
        subtitle={`${activeCompany.name} • Daily front-desk invoice log`}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            <select value={displayCurrency} onChange={e => setDisplayCurrency(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}
            </select>
            {can(['owner', 'admin', 'accountant']) && (
              <button onClick={() => { setEditingRow(null); setModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg">
                <Plus size={15} /> New Invoice
              </button>
            )}
          </div>
        }
      />"""
new_pageheader = """      <PageHeader
        title="Guest Invoices"
        subtitle={`${activeCompany.name} • Daily front-desk invoice log`}
        currencyProps={cp.currencyProps}
        periodProps={cp.periodProps}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <button onClick={() => setReportModalOpen(true)} className="flex items-center gap-1.5 border border-slate-300 bg-white text-slate-700 text-sm font-medium px-3 py-2 rounded-lg hover:border-navy-400">
              Download Report
            </button>
            {can(['owner', 'admin', 'accountant']) && (
              <button onClick={() => { setEditingRow(null); setModalOpen(true) }} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-3 py-2 rounded-lg">
                <Plus size={15} /> New Invoice
              </button>
            )}
          </div>
        }
      />"""
content = content.replace(old_pageheader, new_pageheader)

# 9. Update DataTable to use cpRows
content = content.replace(
    "        rows={rows}",
    "        rows={cpRows}"
)

# 10. Fix displayCurrency in report modal
content = content.replace(
    "fields={[{ type: 'currency', key: 'currency', default: displayCurrency }]}",
    "fields={[{ type: 'currency', key: 'currency', default: cp.displayCurrency }]}"
)

# 11. Add useCurrencyAndPeriod import if missing
if "import { useCurrencyAndPeriod }" not in content:
    content = content.replace(
        "import { useAuth } from '../lib/AuthContext'",
        "import { useAuth } from '../lib/AuthContext'\nimport { useCurrencyAndPeriod } from '../lib/useCurrencyAndPeriod'"
    )

with open('src/pages/HotelGuestInvoices.jsx', 'w') as f:
    f.write(content)
