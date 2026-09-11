import re

with open('src/components/InvoiceDownloadMenu.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    "import { Download, FileText, FileSpreadsheet, FileType, Loader2 } from 'lucide-react'",
    "import { Download, FileText, FileSpreadsheet, FileType, Loader2, Eye } from 'lucide-react'"
)

# Replace the single button return
content = content.replace(
    "    return (\n      <button onClick={() => run(exportInvoicePDF)} disabled={loading} className={triggerClassName || 'text-slate-400 hover:text-navy-600 disabled:opacity-50'} title=\"Download PDF\">\n        {loading ? <Loader2 size={15} className=\"animate-spin\" /> : <Download size={15} />}\n      </button>\n    )",
    """    return (
      <div className="flex items-center gap-2">
        <button onClick={() => run(async (args) => exportInvoicePDF({ ...args, preview: true }))} disabled={loading} className={triggerClassName || 'text-slate-400 hover:text-navy-600 disabled:opacity-50'} title="Preview Invoice">
          <Eye size={15} />
        </button>
        <button onClick={() => run(exportInvoicePDF)} disabled={loading} className={triggerClassName || 'text-slate-400 hover:text-navy-600 disabled:opacity-50'} title="Download PDF">
          {loading ? <Loader2 size={15} className="animate-spin" /> : <Download size={15} />}
        </button>
      </div>
    )"""
)

# Replace the dropdown return
content = content.replace(
    "    <div className=\"relative\" ref={ref}>\n      <button onClick={() => setOpen(o => !o)} disabled={loading} className={triggerClassName || 'text-slate-400 hover:text-navy-600 disabled:opacity-50'} title=\"Download\">",
    """    <div className="flex items-center gap-2">
      <button onClick={() => run(async (args) => exportInvoicePDF({ ...args, preview: true }))} disabled={loading} className={triggerClassName || 'text-slate-400 hover:text-navy-600 disabled:opacity-50'} title="Preview Invoice">
        <Eye size={15} />
      </button>
      <div className="relative" ref={ref}>
        <button onClick={() => setOpen(o => !o)} disabled={loading} className={triggerClassName || 'text-slate-400 hover:text-navy-600 disabled:opacity-50'} title="Download">"""
)

content = content.replace(
    "        </div>\n      )}\n    </div>\n  )",
    "        </div>\n      )}\n      </div>\n    </div>\n  )"
)

with open('src/components/InvoiceDownloadMenu.jsx', 'w') as f:
    f.write(content)
