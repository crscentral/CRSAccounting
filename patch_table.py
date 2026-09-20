import re

with open('src/pages/RestaurantRevenue.jsx', 'r') as f:
    content = f.read()

old_table = """          { key: 'other_amount_usd', label: 'Other', render: r => cp.fmt(r.other_amount_usd) },
          { key: 'amount_usd', label: 'Total', render: r => cp.fmt(r.amount_usd) },
          { key: 'per_cover', label: 'Rev/Cover', render: r => r.covers > 0 ? cp.fmt(r.amount_usd / r.covers) : '—' },"""
new_table = """          { key: 'other_amount_usd', label: 'Other', render: r => cp.fmt(r.other_amount_usd) },
          { key: 'amount_usd', label: 'Total', render: r => cp.fmt(r.amount_usd) },
          { key: 'collected_usd', label: 'Collected', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(r.collected_usd || 0)}</span> },
          { key: 'balance', label: 'Balance', render: r => {
              const bal = Number(r.amount_usd) - (Number(r.collected_usd) || 0)
              return <span className={bal > 0 ? "text-red-600 font-medium" : "text-slate-500"}>{cp.fmt(bal)}</span>
          } },"""
content = content.replace(old_table, new_table)

with open('src/pages/RestaurantRevenue.jsx', 'w') as f:
    f.write(content)
