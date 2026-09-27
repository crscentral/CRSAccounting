with open('src/components/AppShell.jsx', 'r') as f:
    content = f.read()

old_end = """      <div className="flex items-center gap-3">
        <NavLink to="/tally-mode" className="text-[11px] text-navy-200 hover:text-white px-2 py-1 rounded bg-white/5 hover:bg-white/10 transition-colors font-medium tracking-wide">Switch to Tally View</NavLink>
        <ProductSwitcher activeProduct={activeProduct} availableProducts={availableProducts} switchProduct={switchProduct} />
        {activeRole && (
          <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-white/10 capitalize">{activeRole}</span>
        )}
      </div>
    </div>
  )
}"""

new_end = """      <div className="flex items-center gap-3">
        <NavLink to="/tally-mode" className="text-[11px] text-navy-200 hover:text-white px-2 py-1 rounded bg-white/5 hover:bg-white/10 transition-colors font-medium tracking-wide">Switch to Tally View</NavLink>
        <ProductSwitcher activeProduct={activeProduct} availableProducts={availableProducts} switchProduct={switchProduct} />
        {activeRole && (
          <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-white/10 capitalize">{activeRole}</span>
        )}
      </div>
    </div>
    </div>
  )
}"""

content = content.replace(old_end, new_end)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(content)
