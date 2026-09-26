import re

with open('src/pages/TallyMode/TallyGateway.jsx', 'r') as f:
    content = f.read()

# Add Dashboard to Reports
old_reports = """  { section: 'Reports', items: [{ label: 'Balance Sheet', hotkey: 'B', path: '/tally-mode/balance-sheet' }, { label: 'Profit & Loss A/c', hotkey: 'P', path: '/tally-mode/pnl' }, { label: 'Ratio Analysis', hotkey: 'R', path: '/tally-mode/ratios' }, { label: 'Display More Reports', hotkey: 'D', path: '/tally-mode/display' }] }"""
new_reports = """  { section: 'Reports', items: [{ label: 'Financial Dashboard', hotkey: 'F', path: '/' }, { label: 'Balance Sheet', hotkey: 'B', path: '/tally-mode/balance-sheet' }, { label: 'Profit & Loss A/c', hotkey: 'P', path: '/tally-mode/pnl' }, { label: 'Ratio Analysis', hotkey: 'R', path: '/tally-mode/ratios' }, { label: 'Display More Reports', hotkey: 'D', path: '/tally-mode/display' }] }"""
content = content.replace(old_reports, new_reports)

with open('src/pages/TallyMode/TallyGateway.jsx', 'w') as f:
    f.write(content)
