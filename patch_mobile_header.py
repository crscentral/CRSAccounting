with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

old_header = '<header className="md:hidden h-14 bg-white border-b border-slate-200 flex items-center justify-between px-4 sticky top-0 z-30">'
new_header = """<header className="md:hidden bg-white border-b border-slate-200 sticky top-0 z-30 flex flex-col">
          <div className="w-full shrink-0 bg-navy-700" style={{ height: 'env(safe-area-inset-top)' }} />
          <div className="h-14 w-full flex items-center justify-between px-4 shrink-0">"""
          
content = content.replace(old_header, new_header)

old_header_close = '          <div className="w-6" />\n        </header>'
new_header_close = '          <div className="w-6" />\n          </div>\n        </header>'
content = content.replace(old_header_close, new_header_close)

# What about the Desktop Sidebar?
old_aside = '<aside className={`hidden md:flex md:flex-col border-r border-slate-200 bg-white shrink-0 transition-all duration-300 ${sidebarExpanded ? \'w-20 lg:w-64\' : \'w-0 overflow-hidden border-r-0\'}`}>'
new_aside = old_aside + """\n        <div className="w-full shrink-0 bg-navy-700" style={{ height: 'env(safe-area-inset-top)' }} />"""
content = content.replace(old_aside, new_aside)

# What about the Mobile Drawer Sidebar?
old_drawer = '<div className="absolute left-0 top-0 bottom-0 w-72 bg-white shadow-xl flex flex-col">'
new_drawer = old_drawer + """\n            <div className="w-full shrink-0 bg-navy-700" style={{ height: 'env(safe-area-inset-top)' }} />"""
content = content.replace(old_drawer, new_drawer)


with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
