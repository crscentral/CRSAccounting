import re

with open('src/components/AppShell.jsx', 'r') as f:
    code = f.read()

old_nav = "  const visibleNavItems = NAV_ITEMS.filter(item => !item.products || item.products.includes(activeProduct))"

new_nav = """  const HOTEL_NAV_ORDER = [
    '/overview',
    '/',
    '/companies',
    '/hotel-guest-invoices',
    '/hotel-revenue',
    '/hotel-expenses',
    '/hotel-stats',
    '/hotel-budget',
    '/contacts',
    '/accounts',
  ]
  const visibleNavItems = NAV_ITEMS.filter(item => !item.products || item.products.includes(activeProduct))
  if (activeProduct === 'hotel') {
    visibleNavItems.sort((a, b) => {
      let idxA = HOTEL_NAV_ORDER.indexOf(a.to)
      let idxB = HOTEL_NAV_ORDER.indexOf(b.to)
      if (idxA === -1) idxA = 999 + NAV_ITEMS.indexOf(a)
      if (idxB === -1) idxB = 999 + NAV_ITEMS.indexOf(b)
      return idxA - idxB
    })
  }"""
code = code.replace(old_nav, new_nav)

with open('src/components/AppShell.jsx', 'w') as f:
    f.write(code)
