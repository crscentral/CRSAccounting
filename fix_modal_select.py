import re

with open('src/components/ReportOptionsModal.jsx', 'r') as f:
    code = f.read()

# Add select field support
old_render = """          return (
            <div key={field.key} className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-500 uppercase">{field.label}</label>
              <div className="space-y-1 text-sm text-slate-700">
                {field.options.map(opt => (
                  <label key={opt} className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" checked={values[field.key] === opt} onChange={() => setValues(prev => ({ ...prev, [field.key]: opt }))} className="text-navy-600 focus:ring-navy-500" />
                    {opt}
                  </label>
                ))}
              </div>
            </div>
          )"""

new_render = """          return (
            <div key={field.key} className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-500 uppercase">{field.label}</label>
              <div className="space-y-1 text-sm text-slate-700">
                {field.options.map(opt => (
                  <label key={opt} className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" checked={values[field.key] === opt} onChange={() => setValues(prev => ({ ...prev, [field.key]: opt }))} className="text-navy-600 focus:ring-navy-500" />
                    {opt}
                  </label>
                ))}
              </div>
            </div>
          )
        }
        if (field.type === 'select') {
          return (
            <div key={field.key}>
              <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">{field.label}</label>
              <select value={values[field.key]} onChange={e => setValues(prev => ({ ...prev, [field.key]: e.target.value }))} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
                {field.options.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
          )"""
code = code.replace(old_render, new_render)

with open('src/components/ReportOptionsModal.jsx', 'w') as f:
    f.write(code)
