import re

with open('src/pages/Companies.jsx', 'r') as f:
    code = f.read()

bad_func = """  function openEdit(company) {
    setEditingCompany(company)
    setForm({ ...company, fiscal_year_start_month: company.fiscal_year_start_month || 1, products: company.company_products?.map(p => p.product) || [] }).map(k => [k, company[k] ?? emptyForm[k]])) })
    setTab('General')
    setModalOpen(true)
  }"""

good_func = """  function openEdit(company) {
    setEditingCompany(company)
    setForm(Object.fromEntries(Object.keys(emptyForm).map(k => {
      if (k === 'products') return [k, company.company_products?.map(p => p.product) || []]
      if (k === 'fiscal_year_start_month') return [k, company[k] || 1]
      return [k, company[k] ?? emptyForm[k]]
    })))
    setTab('General')
    setModalOpen(true)
  }"""

code = code.replace(bad_func, good_func)

with open('src/pages/Companies.jsx', 'w') as f:
    f.write(code)
