import re

def patch_file():
    with open('src/pages/Reports.jsx', 'r') as f:
        content = f.read()

    # 1. Fix AccountBlock
    old_account_block = """function AccountBlock({ title, color, accounts, balances, fmt, total }) {
  const bg = color === 'emerald' ? 'bg-emerald-600' : 'bg-rose-600'
  return (
    <div>
      <div className={`${bg} text-white text-sm font-semibold px-3 py-2 rounded-t-lg`}>{title}</div>
      <div className="border border-t-0 border-slate-100 rounded-b-lg divide-y divide-slate-50">
        {accounts.map(a => (
          <Row key={a.id} label={`${a.code} - ${a.name}`} value={fmt(Math.abs(balances[a.id] || 0))} />
        ))}
        <Row label={`Total ${title.split(' ')[0]}`} value={fmt(Math.abs(total))} bold />
      </div>
    </div>
  )
}"""

    new_account_block = """function AccountBlock({ title, color, accounts, balances, fmt, total }) {
  const bg = color === 'emerald' ? 'bg-emerald-600' : 'bg-rose-600'
  return (
    <div>
      <div className={`${bg} text-white text-sm font-semibold px-3 py-2 rounded-t-lg`}>{title}</div>
      <div className="border border-t-0 border-slate-100 rounded-b-lg divide-y divide-slate-50">
        {accounts.map(a => {
          let val = balances[a.id] || 0
          if (a.type === 'Liabilities' || a.type === 'Equity' || a.type === 'Revenue') val = -val
          return <Row key={a.id} label={`${a.code} - ${a.name}`} value={fmt(val)} />
        })}
        <Row label={`Total ${title.split(' ')[0]}`} value={fmt(total)} bold />
      </div>
    </div>
  )
}"""

    content = content.replace(old_account_block, new_account_block)

    # 2. Fix generateFinancialReport PDF export logic
    # Assets PDF row
    old_assets_pdf = "rows: [...by('Assets').map(a => [`${a.code} - ${a.name}`, fmt(Math.abs(bal[a.id] || 0))]), ['Total Assets', fmt(assets)]]"
    new_assets_pdf = "rows: [...by('Assets').map(a => [`${a.code} - ${a.name}`, fmt(bal[a.id] || 0)]), ['Total Assets', fmt(assets)]]"
    content = content.replace(old_assets_pdf, new_assets_pdf)

    # Liabilities PDF row
    old_liab_pdf = "rows: [...[...by('Liabilities'), ...by('Equity')].map(a => [`${a.code} - ${a.name}`, fmt(Math.abs(bal[a.id] || 0))]), ['Total Liabilities & Equity', fmt(liab + sum('Equity') * -1)]]"
    new_liab_pdf = "rows: [...[...by('Liabilities'), ...by('Equity')].map(a => [`${a.code} - ${a.name}`, fmt(-(bal[a.id] || 0))]), ['Total Liabilities & Equity', fmt(liab + sum('Equity') * -1)]]"
    content = content.replace(old_liab_pdf, new_liab_pdf)
    
    # 3. Wait, how is totalAssets computed in the UI?
    # Let's check where totalAssets and totalLiabilities are passed to AccountBlock.
    with open('src/pages/Reports.jsx', 'w') as f:
        f.write(content)
    print("Patched Reports.jsx")

patch_file()
