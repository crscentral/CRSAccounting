import re

for file in ['src/pages/TallyMode/TallyMasterCreate.jsx', 'src/pages/TallyMode/TallyVouchers.jsx']:
    with open(file, 'r') as f:
        content = f.read()
    
    if "MasterCreate" in file:
        content = re.sub(
            r'<div className="tally-voucher-header">\s*<span>Ledger Alteration / Creation</span>',
            '<div className="tally-voucher-header items-center">\\n          <div className="flex items-center gap-4">\\n            <button onClick={() => navigate(\'/tally-mode\')} className="bg-slate-200 text-slate-800 px-2 py-0.5 border border-slate-400 text-xs hover:bg-slate-300">ESC: Quit</button>\\n            <span>Ledger Alteration / Creation</span>\\n          </div>',
            content
        )
    else:
        content = re.sub(
            r'<div className="tally-voucher-header">\s*<span>Accounting Voucher Creation</span>',
            '<div className="tally-voucher-header items-center">\\n          <div className="flex items-center gap-4">\\n            <button onClick={() => navigate(\'/tally-mode\')} className="bg-slate-200 text-slate-800 px-2 py-0.5 border border-slate-400 text-xs hover:bg-slate-300">ESC: Quit</button>\\n            <span>Accounting Voucher Creation</span>\\n          </div>',
            content
        )
        
    with open(file, 'w') as f:
        f.write(content)
