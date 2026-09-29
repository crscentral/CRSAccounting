import re

def patch(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # 1. Daily Expenses
    old_daily = """          { key: 'amount_usd', label: 'Amount', render: r => (
            <div className="flex flex-col">
              <span className="text-black font-medium">{cp.fmt(r.amount_usd)}</span>
              <span className="text-green-600 text-xs mt-0.5">Paid: {cp.fmt(r.paid_amount_usd || 0)}</span>
              <span className="text-red-600 text-xs">Pending: {cp.fmt(Number(r.amount_usd) - Number(r.paid_amount_usd || 0))}</span>
            </div>
          ) },"""
    new_daily = """          { key: 'amount_usd', label: 'Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.amount_usd)}</span> },
          { key: 'paid', label: 'Paid', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(r.paid_amount_usd || 0)}</span> },
          { key: 'pending', label: 'Pending', render: r => <span className="text-rose-600 font-medium">{cp.fmt(Number(r.amount_usd) - Number(r.paid_amount_usd || 0))}</span> },"""

    if old_daily in content:
        content = content.replace(old_daily, new_daily)
        print("Patched Daily Expenses in", filepath)
    else:
        print("Could not find Daily Expenses block in", filepath)

    # 2. AMC Contracts
    old_amc = """          { key: 'annual_amount_usd', label: 'Annual Amount', render: r => (
            <div className="flex flex-col">
              <span className="text-black font-medium">{cp.fmt(r.annual_amount_usd)}</span>
              <span className="text-green-600 text-xs mt-0.5">Paid: {cp.fmt(r.paid_amount_usd || 0)}</span>
              <span className="text-red-600 text-xs">Pending: {cp.fmt(Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0))}</span>
            </div>
          ) }, 
          { key: 'monthly', label: 'Monthly', render: r => (
            <div className="flex flex-col">
              <span className="text-black font-medium">{cp.fmt(r.annual_amount_usd / 12)}</span>
              <span className="text-green-600 text-xs mt-0.5">Paid: {cp.fmt((r.paid_amount_usd || 0) / 12)}</span>
              <span className="text-red-600 text-xs">Pending: {cp.fmt((Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0)) / 12)}</span>
            </div>
          ) },"""
    new_amc = """          { key: 'annual_amount_usd', label: 'Annual Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.annual_amount_usd)}</span> },
          { key: 'annual_paid', label: 'Paid (Yr)', render: r => <span className="text-emerald-600 font-medium">{cp.fmt(r.paid_amount_usd || 0)}</span> },
          { key: 'annual_pending', label: 'Pending (Yr)', render: r => <span className="text-rose-600 font-medium">{cp.fmt(Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0))}</span> },
          { key: 'monthly', label: 'Monthly', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.annual_amount_usd / 12)}</span> },
          { key: 'monthly_paid', label: 'Paid (Mo)', render: r => <span className="text-emerald-600 font-medium">{cp.fmt((r.paid_amount_usd || 0) / 12)}</span> },
          { key: 'monthly_pending', label: 'Pending (Mo)', render: r => <span className="text-rose-600 font-medium">{cp.fmt((Number(r.annual_amount_usd) - Number(r.paid_amount_usd || 0)) / 12)}</span> },"""

    if old_amc in content:
        content = content.replace(old_amc, new_amc)
        print("Patched AMC Contracts in", filepath)
    else:
        print("Could not find AMC block in", filepath)

    # 3. Purchase Invoices
    old_pi = """              return (
                <div className="flex flex-col">
                  <span className="text-black font-medium">{cp.fmt(r.amount_usd)}</span>
                  <span className="text-green-600 text-xs mt-0.5">Paid: {cp.fmt(paid)}</span>
                  <span className="text-red-600 text-xs">Pending: {cp.fmt(pending)}</span>
                </div>
              )
            } },"""
    
    # Wait, the Purchase Invoice one is inside a render function block
    # Let's replace the whole column definition for PI
    old_pi_full = """          { key: 'amount_usd', label: 'Amount', render: r => {
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
    new_pi_full = """          { key: 'amount_usd', label: 'Amount', render: r => <span className="font-medium text-slate-700">{cp.fmt(r.amount_usd)}</span> },
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
