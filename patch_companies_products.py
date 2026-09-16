import re

with open('src/pages/Companies.jsx', 'r') as f:
    code = f.read()

# Add PRODUCT_LABELS and ALL_PRODUCTS
code = code.replace(
    "const emptyForm = {",
    "const PRODUCT_LABELS = { basic: 'CRS Basic Accounting', hotel: 'CRS Hotel Accounting', restaurant: 'CRS Restaurant Accounting' }\nconst ALL_PRODUCTS = ['basic', 'hotel', 'restaurant']\n\nconst emptyForm = {"
)

# Update emptyForm
code = code.replace(
    "lut_ack_number: '', lut_expiry_date: '',\n}",
    "lut_ack_number: '', lut_expiry_date: '', products: [],\n}"
)

# Add availableProductsToUser memo
code = code.replace(
    "const [error, setError] = useState('')",
    """const [error, setError] = useState('')

  const availableProductsToUser = useMemo(() => {
    const products = new Set()
    companies.forEach(member => {
      member.company.company_products?.forEach(p => products.add(p.product))
    })
    // If platform admin or no products found (new user), fallback to all
    if (products.size === 0) return ALL_PRODUCTS
    return Array.from(products)
  }, [companies])"""
)
code = code.replace("import { useState }", "import { useState, useMemo }")
code = code.replace("import React, { useState }", "import React, { useState, useMemo }")
if "useMemo" not in code:
    code = code.replace("import {", "import { useMemo,")

# Update openCreate
code = code.replace(
    "setForm(emptyForm)",
    "setForm({ ...emptyForm, products: availableProductsToUser })"
)

# Update openEdit
code = code.replace(
    "function openEdit(company) {\n    setEditingCompany(company)\n    setForm({ ...company, fiscal_year_start_month: company.fiscal_year_start_month || 1 })",
    "function openEdit(company) {\n    setEditingCompany(company)\n    setForm({ ...company, fiscal_year_start_month: company.fiscal_year_start_month || 1, products: company.company_products?.map(p => p.product) || [] })"
)
code = code.replace(
    "function openEdit(company) {\n    setEditingCompany(company)\n    setForm(company)",
    "function openEdit(company) {\n    setEditingCompany(company)\n    setForm({ ...company, products: company.company_products?.map(p => p.product) || [] })"
)
# Just in case the openEdit looks a bit different:
code = re.sub(
    r"function openEdit\(company\) \{\n\s*setEditingCompany\(company\)\n\s*setForm\([^)]+\)",
    "function openEdit(company) {\n    setEditingCompany(company)\n    setForm({ ...company, fiscal_year_start_month: company.fiscal_year_start_month || 1, products: company.company_products?.map(p => p.product) || [] })",
    code
)

# Replace handleSubmit
submit_search = """  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!form.name.trim()) { setError('Company name is required.'); return }
    setSaving(true)
    try {
      const payload = { ...form, lut_expiry_date: form.lut_expiry_date || null }
      if (editingCompany) {
        const { error: err } = await supabase.from('companies').update(payload).eq('id', editingCompany.id)
        if (err) throw err
      } else {
        const { data: newCompanyId, error: rpcError } = await supabase.rpc('create_company_with_owner', {
          p_name: form.name.trim(), p_legal_name: form.legal_name.trim() || null,
          p_address: form.address.trim() || null, p_city: form.city.trim() || null, p_country: form.country.trim() || null,
          p_email: form.email.trim() || null, p_website: form.website.trim() || null,
          p_base_currency: form.base_currency, p_fiscal_year_start_month: form.fiscal_year_start_month,
        })
        if (rpcError) throw rpcError
        await supabase.from('companies').update(payload).eq('id', newCompanyId)
        switchCompany(newCompanyId)
      }
      await refreshCompanies()
      setModalOpen(false)
    } catch (err) {
      setError(err.message || 'Something went wrong saving the company.')
    } finally {
      setSaving(false)
    }
  }"""

submit_replace = """  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!form.name.trim()) { setError('Company name is required.'); return }
    setSaving(true)
    try {
      const { products, company_products, ...companyFields } = form
      const payload = { ...companyFields, lut_expiry_date: companyFields.lut_expiry_date || null }
      
      let targetCompanyId = editingCompany?.id
      
      if (editingCompany) {
        const { error: err } = await supabase.from('companies').update(payload).eq('id', editingCompany.id)
        if (err) throw err
      } else {
        const { data: newCompanyId, error: rpcError } = await supabase.rpc('create_company_with_owner', {
          p_name: companyFields.name.trim(), p_legal_name: companyFields.legal_name.trim() || null,
          p_address: companyFields.address.trim() || null, p_city: companyFields.city.trim() || null, p_country: companyFields.country.trim() || null,
          p_email: companyFields.email.trim() || null, p_website: companyFields.website.trim() || null,
          p_base_currency: companyFields.base_currency, p_fiscal_year_start_month: companyFields.fiscal_year_start_month,
        })
        if (rpcError) throw rpcError
        await supabase.from('companies').update(payload).eq('id', newCompanyId)
        targetCompanyId = newCompanyId
        switchCompany(newCompanyId)
      }

      if (products) {
        const { data: currentProducts } = await supabase.from('company_products').select('product').eq('company_id', targetCompanyId)
        const currentArr = (currentProducts || []).map(p => p.product)
        
        const toAdd = products.filter(p => !currentArr.includes(p))
        const toRemove = currentArr.filter(p => !products.includes(p))
        
        if (toAdd.length > 0) {
          const insertPayload = toAdd.map(p => ({ company_id: targetCompanyId, product: p }))
          await supabase.from('company_products').insert(insertPayload)
        }
        if (toRemove.length > 0) {
          await supabase.from('company_products').delete().eq('company_id', targetCompanyId).in('product', toRemove)
        }
      }

      await refreshCompanies()
      setModalOpen(false)
    } catch (err) {
      setError(err.message || 'Something went wrong saving the company.')
    } finally {
      setSaving(false)
    }
  }"""

code = code.replace(submit_search, submit_replace)

# Render Checkboxes at the bottom of General tab
checkbox_html = """
                  <div className="pt-2 border-t border-slate-100 mt-4">
                    <p className="text-sm font-medium text-slate-700 mb-2">Accounting Modules</p>
                    <div className="flex flex-wrap gap-2">
                      {availableProductsToUser.map(product => (
                        <label key={product} className="flex items-center gap-2 border border-slate-200 rounded-lg px-3 py-2 cursor-pointer hover:bg-slate-50">
                          <input 
                            type="checkbox" 
                            checked={form.products?.includes(product) || false}
                            onChange={(e) => {
                              const curr = form.products || []
                              if (e.target.checked) update('products', [...curr, product])
                              else update('products', curr.filter(p => p !== product))
                            }}
                            className="rounded text-navy-600 focus:ring-navy-600"
                          />
                          <span className="text-sm text-slate-700">{PRODUCT_LABELS[product]}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </>
"""
code = code.replace('</Field>\n                </>', '</Field>\n' + checkbox_html)

with open('src/pages/Companies.jsx', 'w') as f:
    f.write(code)
