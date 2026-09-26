import re

files_to_patch = [
    'src/pages/TallyMode/TallyMasterCreate.jsx',
    'src/pages/TallyMode/TallyVouchers.jsx',
    'src/pages/TallyMode/TallyPlaceholder.jsx'
]

for file in files_to_patch:
    with open(file, 'r') as f:
        content = f.read()
        
    old_header = """        <div className="tally-voucher-header">"""
    
    if "MasterCreate" in file:
        new_header = """        <div className="tally-voucher-header items-center">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/tally-mode')} className="bg-slate-200 text-slate-800 px-2 py-0.5 border border-slate-400 text-xs hover:bg-slate-300">ESC: Quit</button>
            <span>Ledger Alteration / Creation</span>
          </div>"""
        content = content.replace(old_header + '\\n          <span>Ledger Alteration / Creation</span>', new_header)
    elif "Vouchers" in file:
        new_header = """        <div className="tally-voucher-header items-center">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/tally-mode')} className="bg-slate-200 text-slate-800 px-2 py-0.5 border border-slate-400 text-xs hover:bg-slate-300">ESC: Quit</button>
            <span>Accounting Voucher Creation</span>
          </div>"""
        content = content.replace(old_header + '\\n          <span>Accounting Voucher Creation</span>', new_header)
    elif "Placeholder" in file:
        pass # Placeholder already has "Press ESC to return" which I will make clickable.
        
    with open(file, 'w') as f:
        f.write(content)

# Update placeholder to make the escape text clickable
with open('src/pages/TallyMode/TallyPlaceholder.jsx', 'r') as f:
    content = f.read()
    
old_esc = """          <div className="text-sm text-slate-500 font-bold">
            Press ESC to return to Gateway
          </div>"""
new_esc = """          <div 
            className="text-sm text-blue-600 font-bold cursor-pointer hover:underline"
            onClick={() => navigate('/tally-mode')}
          >
            Press ESC or Click Here to return to Gateway
          </div>"""
content = content.replace(old_esc, new_esc)

with open('src/pages/TallyMode/TallyPlaceholder.jsx', 'w') as f:
    f.write(content)
