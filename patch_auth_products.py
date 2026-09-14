import re

with open('src/lib/AuthContext.jsx', 'r') as f:
    code = f.read()

# I need to change:
# const availableProducts = (activeCompany?.company_products || []).map(p => p.product)
# To:
# const memberProducts = activeCompanyMember?.products || ['basic', 'hotel', 'restaurant']
# const availableProducts = (activeCompany?.company_products || []).map(p => p.product).filter(p => memberProducts.includes(p))

code = code.replace(
    'const availableProducts = (activeCompany?.company_products || []).map(p => p.product)',
    '''const memberProducts = activeCompanyMember?.products || ['basic', 'hotel', 'restaurant']
  const availableProducts = (activeCompany?.company_products || []).map(p => p.product).filter(p => memberProducts.includes(p))'''
)

# Wait, `company_members` is selected as:
# .select('role, company:companies(*, company_products(product))')
# I need to add `products` to the select:
code = code.replace(
    ".select('role, company:companies(*, company_products(product))')",
    ".select('role, products, company:companies(*, company_products(product))')"
)

with open('src/lib/AuthContext.jsx', 'w') as f:
    f.write(code)
