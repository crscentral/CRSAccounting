import re

with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

# Add link in ActiveCompanyBar
old_block = """      <div className="flex items-center gap-3">
        <ProductSwitcher activeProduct={activeProduct} availableProducts={availableProducts} switchProduct={switchProduct} />"""
new_block = """      <div className="flex items-center gap-3">
        <NavLink to="/tally-mode" className="text-[11px] text-navy-200 hover:text-white px-2 py-1 rounded bg-white/5 hover:bg-white/10 transition-colors font-medium tracking-wide">Switch to Tally View</NavLink>
        <ProductSwitcher activeProduct={activeProduct} availableProducts={availableProducts} switchProduct={switchProduct} />"""
content = content.replace(old_block, new_block)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
