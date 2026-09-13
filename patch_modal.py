import re

with open('src/components/ReportOptionsModal.jsx', 'r') as f:
    content = f.read()

old_buttons = """        <div className="p-5 border-t border-slate-100 grid grid-cols-4 gap-2 sticky bottom-0 bg-white">
          <button disabled={generating} onClick={() => handleGenerate('pdf')} className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg py-2.5 text-xs font-medium text-slate-600 hover:border-navy-400 disabled:opacity-50">
            <FileText size={18} className="text-red-500" /> PDF
          </button>
          <button disabled={generating} onClick={() => handleGenerate('excel')} className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg py-2.5 text-xs font-medium text-slate-600 hover:border-navy-400 disabled:opacity-50">
            <FileSpreadsheet size={18} className="text-emerald-600" /> Excel
          </button>
          <button disabled={generating} onClick={() => handleGenerate('word')} className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg py-2.5 text-xs font-medium text-slate-600 hover:border-navy-400 disabled:opacity-50">
            <FileType size={18} className="text-blue-600" /> Word
          </button>
        </div>"""

new_buttons = """        <div className="p-5 border-t border-slate-100 grid grid-cols-4 gap-2 sticky bottom-0 bg-white">
          <button disabled={generating} onClick={() => handleGenerate('preview')} className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg py-2.5 text-xs font-medium text-slate-600 hover:border-navy-400 disabled:opacity-50">
            <Eye size={18} className="text-slate-500" /> Preview
          </button>
          <button disabled={generating} onClick={() => handleGenerate('pdf')} className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg py-2.5 text-xs font-medium text-slate-600 hover:border-navy-400 disabled:opacity-50">
            <FileText size={18} className="text-red-500" /> PDF
          </button>
          <button disabled={generating} onClick={() => handleGenerate('excel')} className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg py-2.5 text-xs font-medium text-slate-600 hover:border-navy-400 disabled:opacity-50">
            <FileSpreadsheet size={18} className="text-emerald-600" /> Excel
          </button>
          <button disabled={generating} onClick={() => handleGenerate('word')} className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg py-2.5 text-xs font-medium text-slate-600 hover:border-navy-400 disabled:opacity-50">
            <FileType size={18} className="text-blue-600" /> Word
          </button>
        </div>"""

if old_buttons in content:
    content = content.replace(old_buttons, new_buttons)
    print("Success replacing buttons")
else:
    print("Failed replacing buttons")

# Ensure Eye is imported
if "import { X, FileText, FileSpreadsheet, FileType }" in content:
    content = content.replace("import { X, FileText, FileSpreadsheet, FileType }", "import { X, FileText, FileSpreadsheet, FileType, Eye }")
elif " Eye " not in content and "Eye," not in content:
    # try to append Eye to lucide-react imports
    content = re.sub(r'import\s+\{([^}]+)\}\s+from\s+[\'"]lucide-react[\'"]', r'import {\1, Eye} from "lucide-react"', content)
    print("Imported Eye")

with open('src/components/ReportOptionsModal.jsx', 'w') as f:
    f.write(content)
