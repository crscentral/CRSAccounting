import re

def patch():
    with open('src/pages/Ledger.jsx', 'r') as f:
        content = f.read()

    old_modal = """            { type: 'period', key: 'period', default: 'ALL_TIME' },"""
    new_modal = """            { type: 'period', key: 'period', default: cp.period, defaultFrom: cp.range.from, defaultTo: cp.range.to },"""
    content = content.replace(old_modal, new_modal)
    
    with open('src/pages/Ledger.jsx', 'w') as f:
        f.write(content)
        print("Patched Ledger.jsx")

patch()
