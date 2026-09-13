def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Dashboard line 127
    content = content.replace(
        "monthlyMap[k].out += Number(i.balance_due)",
        "monthlyMap[k].out += (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd))"
    )

    # Analytics lines 48 & 72
    content = content.replace(
        "const outstanding = sSel.reduce((s2, i) => s2 + Number(i.balance_due), 0)",
        "const outstanding = sSel.reduce((s2, i) => s2 + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)"
    )
    content = content.replace(
        "const outstanding = sales.reduce((s, i) => s + Number(i.balance_due), 0)",
        "const outstanding = sales.reduce((s, i) => s + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)"
    )

    # SalesInvoices line 101
    content = content.replace(
        "const pendingUsd = invoices.filter(i => i.status !== 'Paid').reduce((s, i) => s + Number(i.balance_due), 0)",
        "const pendingUsd = invoices.filter(i => i.status !== 'Paid').reduce((s, i) => s + ((Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)"
    )

    with open(filepath, 'w') as f:
        f.write(content)

fix_file('src/pages/Dashboard.jsx')
fix_file('src/pages/Analytics.jsx')
fix_file('src/pages/SalesInvoices.jsx')
