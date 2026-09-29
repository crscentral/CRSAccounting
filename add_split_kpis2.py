with open('src/pages/HotelExpenses.jsx', 'r') as f:
    content = f.read()

anchor_kpi = """        <KpiCard label="Total Expenses" value={cp.fmt(totalExpenses)} tone="red" />
        {topHeads.map(([name, usd]) => <KpiCard key={name} label={name} value={cp.fmt(usd)} tone="slate" />)}"""

new_kpi = """        <KpiCard label="Total Expenses" value={cp.fmt(totalExpenses)} tone="red" />
        <KpiCard label="Total Hotel Expenses" value={cp.fmt(totalHotelExpenses)} tone="slate" />
        <KpiCard label="Total Restaurant Expenses" value={cp.fmt(totalRestExpenses)} tone="slate" />
        {topHeads.slice(0, 1).map(([name, usd]) => <KpiCard key={name} label={name} value={cp.fmt(usd)} tone="slate" />)}"""

content = content.replace(anchor_kpi, new_kpi)

# Also let's change "Total Amount" to "Total Daily Amount" in the footers to be clearer
content = content.replace("Total Amount: {cp.fmt(hotelEntriesTotal)}", "Total Daily Amount: {cp.fmt(hotelEntriesTotal)}")
content = content.replace("Total Amount: {cp.fmt(restEntriesTotal)}", "Total Daily Amount: {cp.fmt(restEntriesTotal)}")

with open('src/pages/HotelExpenses.jsx', 'w') as f:
    f.write(content)
