import sys, re

def process(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # 1. ExpenseEntryFormModal: Add paid_amount state and input
    content = re.sub(
        r'(const \[amount, setAmount\] = useState\(editingRow\?\.amount \|\| \'\'\))',
        r'\1\n  const [paidAmount, setPaidAmount] = useState(editingRow?.paid_amount || \'\')',
        content
    )
    
    content = re.sub(
        r'(amount_usd: Math\.round\(Number\(amount\) / fxRate \* 100\) / 100,)',
        r'\1\n        paid_amount: Number(paidAmount || 0), paid_amount_usd: Math.round(Number(paidAmount || 0) / fxRate * 100) / 100,',
        content
    )
    
    content = re.sub(
        r'(<div className="grid grid-cols-2 gap-3">\s*<Field label="Currency">.*?</Field>\s*<Field label="Amount \*">.*?<input.*?value={amount}.*?/>\s*</Field>\s*</div>)',
        r'<div className="grid grid-cols-3 gap-3">\n          <Field label="Currency">\n            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">\n              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}\n            </select>\n          </Field>\n          <Field label="Amount *">\n            <input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />\n          </Field>\n          <Field label="Paid Amount">\n            <input type="number" step="0.01" min="0" value={paidAmount} onChange={e => setPaidAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />\n          </Field>\n        </div>',
        content,
        flags=re.DOTALL
    )

    # 2. AmcContractFormModal
    content = re.sub(
        r'(const \[annualAmount, setAnnualAmount\] = useState\(editingRow\?\.annual_amount \|\| \'\'\))',
        r'\1\n  const [paidAmount, setPaidAmount] = useState(editingRow?.paid_amount || \'\')',
        content
    )
    
    content = re.sub(
        r'(annual_amount_usd: Math\.round\(Number\(annualAmount\) / fxRate \* 100\) / 100,)',
        r'\1\n        paid_amount: Number(paidAmount || 0), paid_amount_usd: Math.round(Number(paidAmount || 0) / fxRate * 100) / 100,',
        content
    )
    
    content = re.sub(
        r'(<div className="grid grid-cols-2 gap-3">\s*<Field label="Currency">.*?</Field>\s*<Field label="Annual Amount \*">.*?<input.*?value={annualAmount}.*?/>\s*</Field>\s*</div>)',
        r'<div className="grid grid-cols-3 gap-3">\n          <Field label="Currency">\n            <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">\n              {CURRENCY_LIST.slice(0, 30).map(c => <option key={c.code} value={c.code}>{c.code}</option>)}\n            </select>\n          </Field>\n          <Field label="Annual Amount *">\n            <input type="number" step="0.01" min="0" required value={annualAmount} onChange={e => setAnnualAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />\n          </Field>\n          <Field label="Paid Amount">\n            <input type="number" step="0.01" min="0" value={paidAmount} onChange={e => setPaidAmount(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />\n          </Field>\n        </div>',
        content,
        flags=re.DOTALL
    )

    # 3. KPI Calculations
    kpi_calc = """
  const entriesTotalPaidUsd = entries.reduce((s, r) => s + Number(r.paid_amount_usd || 0), 0)
  const amcMonthlyPaidUsd = amcContracts.reduce((s, r) => s + (Number(r.paid_amount_usd || 0) / 12), 0)
  const amcTotalPaidForView = amcMonthlyPaidUsd * monthsInView
  const piTotalPaidUsd = purchaseInvoices.reduce((s, r) => s + (r.status === 'Paid' ? Number(r.amount_usd) : 0), 0)

  const totalBilled = totalExpenses
  const totalPaid = entriesTotalPaidUsd + amcTotalPaidForView + piTotalPaidUsd
  const totalPending = totalBilled - totalPaid

  const byHead"""
    content = content.replace("  const byHead", kpi_calc)
    
    kpis = """      <div className="grid grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Billed" value={cp.fmt(totalBilled)} tone="slate" />
        <KpiCard label="Total Paid" value={cp.fmt(totalPaid)} tone="green" />
        <KpiCard label="Total Pending" value={cp.fmt(totalPending)} tone="red" />
      </div>
      <div className="grid lg:grid-cols-2"""
    content = content.replace('      <div className="grid lg:grid-cols-2', kpis)
    
    # 4. Data Tables Amounts (Amount column 3 lines)
    daily_amount_col = """{ key: 'amount_usd', label: 'Amount', render: r => (
            <div className="flex flex-col">
              <span className="text-black font-medium">{cp.fmt(r.amount_usd)}</span>
              <span className="text-green-600 text-xs mt-0.5">Paid: {cp.fmt(r.paid_amount_usd || 0)}</span>
              <span className="text-red-600 text-xs">Pending: {cp.fmt(Number(r.amount_usd) - Number(r.paid_amount_usd || 0))}</span>
            </div>
          ) }, """
    content = re.sub(r"\{\s*key:\s*'amount_usd',\s*label:\s*'Amount',\s*render:\s*r\s*=>\s*cp\.fmt\(r\.amount_usd\)\s*\},", daily_amount_col, content)
    
    amc_amount_col = """{ key: 'annual_amount_usd', label: 'Annual Amount', render: r => (
            <div className="flex flex-col">
              <span className="text-black font-medium">{cp.fmt(r.annual_amount_usd)}</span>
              <span className="text-green-600 text-xs mt-0.5">Paid: {cp.fmt(r.paid_amount_usd || 0)}</span>
              <span className="text-red-600 text-xs">Pending: {cp.fmt(Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0))}</span>
            </div>
          ) }, """
    content = re.sub(r"\{\s*key:\s*'annual_amount_usd',\s*label:\s*'Annual Amount',\s*render:\s*r\s*=>\s*cp\.fmt\(r\.annual_amount_usd\)\s*\},", amc_amount_col, content)

    amc_monthly_col = """{ key: 'monthly', label: 'Monthly', render: r => (
            <div className="flex flex-col">
              <span className="text-black font-medium">{cp.fmt(r.annual_amount_usd / 12)}</span>
              <span className="text-green-600 text-xs mt-0.5">Paid: {cp.fmt((r.paid_amount_usd || 0) / 12)}</span>
              <span className="text-red-600 text-xs">Pending: {cp.fmt((Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0)) / 12)}</span>
            </div>
          ) }, """
    content = re.sub(r"\{\s*key:\s*'monthly',\s*label:\s*'Monthly',\s*render:\s*r\s*=>\s*cp\.fmt\(r\.annual_amount_usd\s*/\s*12\)\s*\},", amc_monthly_col, content)

    pi_amount_col = """{ key: 'amount', label: 'Amount', render: r => {
              const paid = r.status === 'Paid' ? r.amount_usd : 0;
              const pending = r.status === 'Paid' ? 0 : r.amount_usd;
              return (
                <div className="flex flex-col">
                  <span className="text-black font-medium">{cp.fmt(r.amount_usd)}</span>
                  <span className="text-green-600 text-xs mt-0.5">Paid: {cp.fmt(paid)}</span>
                  <span className="text-red-600 text-xs">Pending: {cp.fmt(pending)}</span>
                </div>
              )
            } }, """
    content = re.sub(r"\{\s*key:\s*'amount',\s*label:\s*'Amount',\s*render:\s*r\s*=>\s*cp\.fmt\(r\.amount_usd\)\s*\},", pi_amount_col, content)

    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"Processed {filepath}")

process('src/pages/HotelExpenses.jsx')
process('src/pages/RestaurantExpenses.jsx')
