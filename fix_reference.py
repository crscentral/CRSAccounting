def fix_dashboard():
    with open('src/pages/Dashboard.jsx', 'r') as f:
        content = f.read()
    
    old_block = """  const netProfit = totalBilled - totalExpenses
  const collected = totalBilled - outstanding
  const outstanding = sales.reduce((sum, i) => sum + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)"""
    new_block = """  const netProfit = totalBilled - totalExpenses
  const outstanding = sales.reduce((sum, i) => sum + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
  const collected = totalBilled - outstanding"""
    
    content = content.replace(old_block, new_block)
    with open('src/pages/Dashboard.jsx', 'w') as f:
        f.write(content)

def fix_analytics():
    with open('src/pages/Analytics.jsx', 'r') as f:
        content = f.read()

    # Block 1
    old_block1 = """    const totalInvoiced = sSel.reduce((s2, i) => s2 + Number(i.amount_usd), 0)
    const collected = totalInvoiced - outstanding
    const outstanding = sSel.reduce((s2, i) => s2 + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)"""
    new_block1 = """    const totalInvoiced = sSel.reduce((s2, i) => s2 + Number(i.amount_usd), 0)
    const outstanding = sSel.reduce((s2, i) => s2 + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
    const collected = totalInvoiced - outstanding"""
    
    content = content.replace(old_block1, new_block1)

    # Block 2
    old_block2 = """  const totalInvoiced = sales.reduce((s, i) => s + Number(i.amount_usd), 0)
  const collected = totalInvoiced - outstanding
  const outstanding = sales.reduce((s, i) => s + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)"""
    new_block2 = """  const totalInvoiced = sales.reduce((s, i) => s + Number(i.amount_usd), 0)
  const outstanding = sales.reduce((s, i) => s + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)
  const collected = totalInvoiced - outstanding"""

    content = content.replace(old_block2, new_block2)
    with open('src/pages/Analytics.jsx', 'w') as f:
        f.write(content)

fix_dashboard()
fix_analytics()
