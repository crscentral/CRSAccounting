with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

content = content.replace("Receipt, Wallet,", "Receipt, Wallet, AlertTriangle,")

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
