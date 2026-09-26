import os
import re

files_to_check = [
    'src/pages/Reports.jsx',
    'src/pages/Comparison.jsx',
    'src/pages/Ledger.jsx',
    'src/pages/Analytics.jsx',
    'src/pages/FinancialPerformance.jsx',
    'src/pages/PortfolioDashboard.jsx',
    'src/pages/CapitalTransactions.jsx',
]

def safe_name(match):
    return f"(a.name || '').toLowerCase()"

for filename in files_to_check:
    if not os.path.exists(filename):
        continue
    with open(filename, 'r') as f:
        content = f.read()

    # Replace accs.find with (accs || []).find
    content = content.replace("accs.find(", "(accs || []).find(")
    # Replace accounts.find with (accounts || []).find
    content = content.replace("accounts.find(", "(accounts || []).find(")
    
    # Replace a.name.toLowerCase() with (a.name || '').toLowerCase()
    content = re.sub(r'a\.name\.toLowerCase\(\)', safe_name, content)
    # Replace selectedAccount.name.toLowerCase() with (selectedAccount.name || '').toLowerCase()
    content = content.replace("selectedAccount.name.toLowerCase()", "(selectedAccount.name || '').toLowerCase()")
    # Replace account.name.toLowerCase() with (account.name || '').toLowerCase()
    content = content.replace("account.name.toLowerCase()", "(account.name || '').toLowerCase()")

    with open(filename, 'w') as f:
        f.write(content)

