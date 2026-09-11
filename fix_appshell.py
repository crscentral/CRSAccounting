import re

with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

# Add state for sidebar expanded
content = content.replace(
    "const [drawerOpen, setDrawerOpen] = useState(false)",
    "const [drawerOpen, setDrawerOpen] = useState(false)\n  const [sidebarExpanded, setSidebarExpanded] = useState(true)"
)

# Modify sidebar container classes
content = content.replace(
    '<aside className="hidden md:flex md:flex-col w-20 lg:w-64 border-r border-slate-200 bg-white shrink-0">',
    '<aside className={`hidden md:flex md:flex-col border-r border-slate-200 bg-white shrink-0 transition-all duration-300 ${sidebarExpanded ? \'w-20 lg:w-64\' : \'w-0 overflow-hidden border-r-0\'}`}>'
)

# Add hamburger to top desktop nav
content = content.replace(
    '<div className="hidden md:flex items-center justify-between px-6 lg:px-8 h-11 bg-navy-700 text-white text-sm sticky top-0 z-20">',
    '<div className="hidden md:flex items-center justify-between px-6 lg:px-8 h-11 bg-navy-700 text-white text-sm sticky top-0 z-20">\n        <div className="flex items-center gap-4">\n          <button onClick={() => setSidebarExpanded(e => !e)} className="text-white hover:text-slate-300"><Menu size={18} /></button>'
)

# Update the ProductSwitcher block so it doesn't break
content = content.replace(
    '<ProductSwitcher />\n        <div className="flex items-center gap-5">',
    '<ProductSwitcher />\n        </div>\n        <div className="flex items-center gap-5">'
)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
