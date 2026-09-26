with open('src/pages/Dashboard.jsx', 'r') as f:
    content = f.read()

# Fix the sublabels for the KPI cards
old_cards = """      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
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

new_cards = """      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Revenue" value={cp.fmt(totalBilled)} sublabel={['hotel', 'restaurant'].includes(activeProduct) ? 'total accrued revenue' : 'sales invoices'} icon={TrendingUp} tone="green" />
        <KpiCard label="Total Expenses" value={cp.fmt(totalExpenses)} sublabel={['hotel', 'restaurant'].includes(activeProduct) ? 'total accrued expenses' : 'purchase invoices'} icon={TrendingDown} tone="red" />
        <KpiCard label="Expected Net Profit" value={cp.fmt(netProfit)} sublabel="revenue minus expenses" icon={DollarSign} tone={netProfit >= 0 ? 'green' : 'red'} />
        <KpiCard label="Outstanding" value={cp.fmt(outstanding)} sublabel={['hotel', 'restaurant'].includes(activeProduct) ? 'unpaid invoices' : 'pending + overdue'} icon={AlertCircle} tone="slate" />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <KpiCard label="Total Revenue Collected" value={cp.fmt(collected)} sublabel="actual paid revenue" icon={Receipt} tone="gold" />
        <KpiCard label="Total Expenses Paid" value={cp.fmt(expensesMade)} sublabel="actual paid expenses" icon={TrendingDown} tone="orange" />
        <KpiCard label="Actual Profit" value={cp.fmt(actualProfit)} sublabel="collected minus paid" icon={DollarSign} tone={actualProfit >= 0 ? 'green' : 'red'} />
      </div>"""

content = content.replace(old_cards, new_cards)

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(content)
