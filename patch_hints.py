import re

for filename in ['src/components/SalesInvoiceFormModal.jsx', 'src/components/PurchaseInvoiceFormModal.jsx']:
    with open(filename, 'r') as f:
        code = f.read()

    # Find the Notes / Payment Terms labels and add a hint
    code = code.replace(
        '<label className="text-xs font-medium text-slate-500 mb-1.5 block">Notes</label>',
        '<label className="text-xs font-medium text-slate-500 mb-1.5 flex justify-between"><span>Notes</span><span className="text-slate-400 font-normal text-[10px]">Use **bold**, * bullets, or 1. numbers</span></label>'
    )
    code = code.replace(
        '<label className="text-xs font-medium text-slate-500 mb-1.5 block">Payment Terms & Conditions</label>',
        '<label className="text-xs font-medium text-slate-500 mb-1.5 flex justify-between"><span>Payment Terms & Conditions</span><span className="text-slate-400 font-normal text-[10px]">Use **bold**, * bullets, or 1. numbers</span></label>'
    )
    
    with open(filename, 'w') as f:
        f.write(code)
