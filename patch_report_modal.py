import re

with open('src/components/ReportOptionsModal.jsx', 'r') as f:
    content = f.read()

# Update grid-cols-3 to grid-cols-4
content = content.replace("grid grid-cols-3 gap-2 sticky bottom-0", "grid grid-cols-4 gap-2 sticky bottom-0")

# Add the preview button
old_buttons = """<button disabled={generating} onClick={() => handleGenerate('pdf')} className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg py-2.5 text-xs font-medium text-slate-600 hover:border-navy-400 disabled:opacity-50">
            <FileText size={18} /> PDF
          </button>"""
new_buttons = """<button disabled={generating} onClick={() => handleGenerate('preview')} className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg py-2.5 text-xs font-medium text-slate-600 hover:border-navy-400 disabled:opacity-50">
            <FileText size={18} /> Preview
          </button>
          <button disabled={generating} onClick={() => handleGenerate('pdf')} className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg py-2.5 text-xs font-medium text-slate-600 hover:border-navy-400 disabled:opacity-50">
            <FileText size={18} /> PDF
          </button>"""
content = content.replace(old_buttons, new_buttons)

with open('src/components/ReportOptionsModal.jsx', 'w') as f:
    f.write(content)
