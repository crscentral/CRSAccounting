import re

def patch(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    old_pi_full = """              { key: 'amount', label: 'Amount', render: r => {
              const paid = r.status === 'Paid' ? r.amount_usd : 0;
              const pending = r.status === 'Paid' ? 0 : r.amount_usd;
              return (
                <div className="flex flex-col">
                  <span className="text-black font-medium">{cp.fmt(r.amount_usd)}</span>
                  <span className="text-green-600 text-xs mt-0.5">Paid: {cp.fmt(paid)}</span>
                  <span className="text-red-600 text-xs">Pending: {cp.fmt(pending)}</span>
                </div>
              )
            } },"""
            
    new_pi_full = """              { key: 'amount', label: 'Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.amount_usd)}</span> },
              { key: 'paid', label: 'Paid', render: r => { const paid = r.status === 'Paid' ? r.amount_usd : 0; return <span className="text-emerald-600 font-medium">{cp.fmt(paid)}</span> } },
              { key: 'pending', label: 'Pending', render: r => { const pending = r.status === 'Paid' ? 0 : r.amount_usd; return <span className="text-rose-600 font-medium">{cp.fmt(pending)}</span> } },"""

    if old_pi_full in content:
        content = content.replace(old_pi_full, new_pi_full)
        print("Patched PI in", filepath)
    else:
        print("Could not find PI block in", filepath)

    with open(filepath, 'w') as f:
        f.write(content)

patch('src/pages/HotelExpenses.jsx')
patch('src/pages/RestaurantExpenses.jsx')
