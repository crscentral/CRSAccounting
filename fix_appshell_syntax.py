import re

with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

content = content.replace(
    '''<div className="flex items-center gap-4">
          <button onClick={toggleSidebar} className="text-white hover:text-slate-300"><Menu size={18} /></button>
      <div className="relative">''',
    '''<div className="flex items-center gap-4">
          <button onClick={toggleSidebar} className="text-white hover:text-slate-300"><Menu size={18} /></button>
      </div>
      <div className="relative">'''
)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
