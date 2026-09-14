import re

with open('src/pages/Dashboard.jsx', 'r') as f:
    code = f.read()

# Update calculations
calc_str = """  const totalBilled = sales.reduce((sum, i) => sum + Number(i.amount_usd), 0)
  const totalExpenses = purchases.reduce((sum, i) => sum + Number(i.amount_usd), 0)
  const netProfit = totalBilled - totalExpenses
  const outstanding = sales.reduce((sum, i) => sum + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
  const collected = totalBilled - outstanding
  const expensesMade = purchases.reduce((sum, i) => sum + (i.status === 'Paid' ? Number(i.amount_usd) : 0), 0)
  const actualProfit = collected - expensesMade
"""
code = re.sub(
    r"  const totalBilled = .*?  const outstanding = .*?  const collected = totalBilled - outstanding\n",
    calc_str,
    code,
    flags=re.DOTALL
)

# Replace the KpiCards block
cards_repl = """      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Revenue" value={cp.fmt(totalBilled)} sublabel="sales invoices" icon={TrendingUp} tone="green" />
        <KpiCard label="Total Expenses" value={cp.fmt(totalExpenses)} sublabel="purchase invoices" icon={TrendingDown} tone="red" />
        <KpiCard label="Expected Net Profit" value={cp.fmt(netProfit)} sublabel="billed minus expenses" icon={DollarSign} tone={netProfit >= 0 ? 'green' : 'red'} />
        <KpiCard label="Outstanding" value={cp.fmt(outstanding)} sublabel="pending + overdue" icon={AlertCircle} tone="slate" />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Revenue Collected" value={cp.fmt(collected)} sublabel="actual paid revenue" icon={Receipt} tone="gold" />
        <KpiCard label="Total Expenses Made" value={cp.fmt(expensesMade)} sublabel="actual paid expenses" icon={TrendingDown} tone="orange" />
        <KpiCard label="Actual Profit" value={cp.fmt(actualProfit)} sublabel="collected minus made" icon={DollarSign} tone={actualProfit >= 0 ? 'green' : 'red'} />
      </div>"""
code = re.sub(
    r"      <div className=\"grid grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4 mb-6\">.*?      </div>",
    cards_repl,
    code,
    flags=re.DOTALL
)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(code)
