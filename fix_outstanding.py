import re

def fix_dashboard(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Dashboard outstanding KPI
    content = content.replace(
        "const outstanding = sales.reduce((sum, i) => sum + Number(i.balance_due), 0)",
        "const outstanding = sales.reduce((sum, i) => sum + (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd)), 0)"
    )

    # Dashboard monthly map
    content = content.replace(
        "monthlyMap[key].Outstanding += Number(i.balance_due)",
        "monthlyMap[key].Outstanding += (i.status === 'Paid' ? 0 : (Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd))"
    )
    
    # Dashboard report rows
    content = content.replace(
        "balanceLabel: cp.fmt(i.amount_usd)",
        "balanceLabel: cp.fmt((Number(i.balance_due) / (Number(i.amount) || 1)) * Number(i.amount_usd))"
    )

    with open(filepath, 'w') as f:
        f.write(content)

fix_dashboard('src/pages/Dashboard.jsx')
