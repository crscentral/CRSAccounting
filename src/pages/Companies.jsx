import { useState, useMemo } from 'react'
import { Plus, Pencil, Trash2, Globe, Mail, MapPin, X, Upload, Search, Check } from 'lucide-react'
import { supabase } from '../lib/supabaseClient'
import { useAuth } from '../lib/AuthContext'
import { MONTH_NAMES } from '../lib/fiscalYear'
import { CURRENCY_LIST } from '../lib/currencies'
import PageHeader from '../components/PageHeader'

const PRODUCT_LABELS = { basic: 'CRS Basic Accounting', hotel: 'CRS Hotel Accounting', restaurant: 'CRS Restaurant Accounting' }
const ALL_PRODUCTS = ['basic', 'hotel', 'restaurant']

const emptyForm = {
  name: '', legal_name: '', industry: 'Revenue Management', address: '', city: '', country: '',
  email: '', website: '', phone: '', tax_id: '', logo_url: '',
  base_currency: 'USD', default_currency: 'USD', favorite_currencies: ['USD', 'THB', 'INR'], fiscal_year_start_month: 1,
  bank_name: '', bank_account_holder: '', bank_account_number: '', bank_branch: '', bank_swift_code: '', bank_ifsc_code: '',
  bank2_name: '', bank2_account_holder: '', bank2_account_number: '', bank2_branch: '', bank2_swift_code: '', bank2_ifsc_code: '',
  default_payment_terms: '', default_notes: '', default_thank_you_note: '',
  lut_ack_number: '', lut_expiry_date: '', products: [],
}

const TABS = ['General', 'Address', 'Bank Details', 'Invoice Settings']

export default function Companies() {
  const { companies, activeCompany, switchCompany, can, refreshCompanies } = useAuth()
  const [modalOpen, setModalOpen] = useState(false)
  const [editingCompany, setEditingCompany] = useState(null)
  const [tab, setTab] = useState('General')
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [uploadingLogo, setUploadingLogo] = useState(false)
  const [error, setError] = useState('')
  const [currencySearch, setCurrencySearch] = useState('')

  const filteredCurrencies = useMemo(() => {
    const q = currencySearch.trim().toLowerCase()
    if (!q) return CURRENCY_LIST
    return CURRENCY_LIST.filter(c => c.code.toLowerCase().includes(q) || c.name.toLowerCase().includes(q))
  }, [currencySearch])

  function toggleFavorite(code) {
    const currFavs = Array.isArray(form.favorite_currencies) ? form.favorite_currencies : ['USD', 'THB', 'INR']
    const updated = currFavs.includes(code)
      ? currFavs.filter(c => c !== code)
      : [...currFavs, code]
    update('favorite_currencies', updated)
  }

  const availableProductsToUser = useMemo(() => {
    const products = new Set()
    companies.forEach(member => {
      member.company.company_products?.forEach(p => products.add(p.product))
    })
    // If platform admin or no products found (new user), fallback to all
    if (products.size === 0) return ALL_PRODUCTS
    return Array.from(products)
  }, [companies])

  function update(field, value) { setForm(f => ({ ...f, [field]: value })) }

  function openCreate() {
    setEditingCompany(null)
    setForm({ ...emptyForm, products: availableProductsToUser })
    setCurrencySearch('')
    setTab('General')
    setModalOpen(true)
  }

  function openEdit(company) {
    setEditingCompany(company)
    setCurrencySearch('')
    setForm(Object.fromEntries(Object.keys(emptyForm).map(k => {
      if (k === 'products') return [k, company.company_products?.map(p => p.product) || []]
      if (k === 'fiscal_year_start_month') return [k, company[k] || 1]
      if (k === 'default_currency') return [k, company.default_currency || company.base_currency || 'USD']
      if (k === 'favorite_currencies') return [k, (Array.isArray(company.favorite_currencies) && company.favorite_currencies.length > 0) ? company.favorite_currencies : ['USD', 'THB', 'INR']]
      return [k, company[k] ?? emptyForm[k]]
    })))
    setTab('General')
    setModalOpen(true)
  }

  async function handleLogoUpload(file) {
    setUploadingLogo(true)
    try {
      const path = `logos/${Date.now()}-${file.name}`
      const { error: uploadErr } = await supabase.storage.from('invoice-attachments').upload(path, file)
      if (uploadErr) throw uploadErr
      const { data } = supabase.storage.from('invoice-attachments').getPublicUrl(path)
      update('logo_url', data.publicUrl)
    } catch (err) {
      setError('Logo upload failed: ' + err.message)
    } finally {
      setUploadingLogo(false)
    }
  }

  async function handleSubmit(e) {
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

      if (payload.favorite_currencies) {
        await supabase.from('company_settings').upsert({
          company_id: targetCompanyId,
          favorite_currencies: payload.favorite_currencies,
        }, { onConflict: 'company_id' })
      }

      await refreshCompanies()
      setModalOpen(false)
    } catch (err) {
      setError(err.message || 'Something went wrong saving the company.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <PageHeader
        title="Company Management"
        subtitle="Manage your business entities and accounting books"
        actions={can(['owner', 'admin']) && (
          <button onClick={openCreate} className="flex items-center gap-1.5 bg-navy-600 hover:bg-navy-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
            <Plus size={16} /> New Company
          </button>
        )}
      />

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {companies.map(({ company, role }) => (
          <div key={company.id} className={`bg-white rounded-xl border p-5 ${activeCompany?.id === company.id ? 'border-navy-400 ring-1 ring-navy-100' : 'border-slate-200'}`}>
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                {company.logo_url && <img src={company.logo_url} alt="" className="h-8 w-8 rounded object-contain border border-slate-100" />}
                <div>
                  <h3 className="font-semibold text-slate-800">{company.name}</h3>
                  <p className="text-xs text-slate-400">{company.legal_name}</p>
                </div>
              </div>
              <div className="flex flex-col items-end gap-1 shrink-0">
                <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200" title="Company Default Operational Currency">
                  Default: {company.default_currency || company.base_currency || 'USD'}
                </span>
                <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-gold-100 text-gold-700" title="Statutory Base Currency">
                  Base: {company.base_currency}
                </span>
                {company.favorite_currencies && company.favorite_currencies.length > 0 && (
                  <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-slate-100 text-slate-600" title="Favorite Currencies">
                    Favs: {company.favorite_currencies.join(', ')}
                  </span>
                )}
              </div>
            </div>
            <span className="inline-block text-[11px] font-medium px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 mb-3">{company.industry || 'Revenue Management'}</span>
            <div className="space-y-1 text-xs text-slate-500 mb-4">
              {company.city && <div className="flex items-center gap-1.5"><MapPin size={12} /> {company.city}, {company.country}</div>}
              {company.email && <div className="flex items-center gap-1.5"><Mail size={12} /> {company.email}</div>}
              {company.website && <div className="flex items-center gap-1.5"><Globe size={12} /> {company.website}</div>}
              {company.lut_ack_number && <div className="text-[11px] text-amber-600">LUT: {company.lut_ack_number}{company.lut_expiry_date ? ` (expires ${company.lut_expiry_date})` : ''}</div>}
            </div>
            <div className="flex gap-2">
              <button onClick={() => switchCompany(company.id)} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-700">
                {activeCompany?.id === company.id ? 'Active' : 'Switch To'}
              </button>
              {can(['owner', 'admin']) && (
                <button onClick={() => openEdit(company)} className="border border-slate-300 text-slate-600 rounded-lg px-3"><Pencil size={14} /></button>
              )}
              {can(['owner']) && (
                <button className="border border-red-200 text-red-500 rounded-lg px-3"><Trash2 size={14} /></button>
              )}
            </div>
            <div className="text-[11px] text-slate-400 mt-2 capitalize">Your role: {role}</div>
          </div>
        ))}
      </div>

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[92vh] overflow-y-auto">
            <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 sticky top-0 bg-white z-10">
              <h2 className="font-semibold text-slate-800">{editingCompany ? 'Edit Company' : 'New Company'}</h2>
              <button onClick={() => setModalOpen(false)} className="text-slate-400 hover:text-slate-600"><X size={20} /></button>
            </div>

            <div className="flex border-b border-slate-100 px-5 overflow-x-auto sticky top-[57px] bg-white z-10">
              {TABS.map(t => (
                <button key={t} type="button" onClick={() => setTab(t)}
                  className={`shrink-0 px-3 py-3 text-sm font-medium border-b-2 -mb-px ${tab === t ? 'border-navy-600 text-navy-700' : 'border-transparent text-slate-400'}`}>
                  {t}
                </button>
              ))}
            </div>

            <form onSubmit={handleSubmit} className="p-5 space-y-4">
              {tab === 'General' && (
                <>
                  <Field label="Company Logo">
                    <div className="flex items-center gap-3 border border-dashed border-slate-300 rounded-lg p-3">
                      {form.logo_url ? <img src={form.logo_url} alt="" className="h-12 w-12 object-contain rounded border border-slate-100" /> : <div className="h-12 w-12 rounded bg-slate-100" />}
                      <div>
                        <p className="text-xs text-slate-400 mb-1">Appears on all invoices by default</p>
                        <label className="flex items-center gap-1.5 text-xs font-medium text-navy-600 cursor-pointer">
                          <Upload size={13} /> {uploadingLogo ? 'Uploading…' : 'Upload Logo'}
                          <input type="file" accept="image/*" className="hidden" onChange={e => e.target.files[0] && handleLogoUpload(e.target.files[0])} />
                        </label>
                      </div>
                    </div>
                  </Field>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Company Name *"><input required value={form.name} onChange={e => update('name', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                    <Field label="Legal Name"><input value={form.legal_name} onChange={e => update('legal_name', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Industry"><input value={form.industry} onChange={e => update('industry', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                    <Field label="Tax ID / GSTIN"><input value={form.tax_id} onChange={e => update('tax_id', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Company Default Currency *">
                      <select value={form.default_currency || form.base_currency || 'USD'} onChange={e => update('default_currency', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm font-semibold text-navy-800 bg-white">
                        {CURRENCY_LIST.map(c => <option key={c.code} value={c.code}>{c.code} — {c.name}</option>)}
                      </select>
                      <p className="text-[11px] text-slate-500 mt-1">Default operational currency for all daily entries, pages, displays, and reports.</p>
                    </Field>
                    <Field label="Base Currency *">
                      <select value={form.base_currency} onChange={e => update('base_currency', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white">
                        {CURRENCY_LIST.map(c => <option key={c.code} value={c.code}>{c.code} — {c.name}</option>)}
                      </select>
                      <p className="text-[11px] text-slate-500 mt-1">Used for statutory legal currency & Base Currency pie chart on Dashboard.</p>
                    </Field>
                  </div>

                  <div className="border border-slate-200 rounded-xl p-3.5 bg-slate-50/50">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <label className="text-xs font-semibold text-slate-700">Favorite Currencies</label>
                          <span className="text-[11px] bg-navy-50 text-navy-700 font-medium px-2 py-0.5 rounded-full border border-navy-100">
                            {(form.favorite_currencies || []).length} selected
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-0.5">
                          Pinned at the top of currency switchers across all pages for this company.
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="relative">
                          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                          <input
                            type="text"
                            value={currencySearch}
                            onChange={e => setCurrencySearch(e.target.value)}
                            placeholder="Search currency..."
                            className="pl-8 pr-7 py-1 text-xs border border-slate-200 rounded-lg w-44 focus:outline-none focus:ring-1 focus:ring-navy-600 focus:border-navy-600 bg-white"
                          />
                          {currencySearch && (
                            <button
                              type="button"
                              onClick={() => setCurrencySearch('')}
                              className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                            >
                              <X size={12} />
                            </button>
                          )}
                        </div>
                        {(form.favorite_currencies || []).length > 0 && (
                          <button
                            type="button"
                            onClick={() => update('favorite_currencies', [])}
                            className="text-[11px] text-slate-400 hover:text-rose-600 transition-colors whitespace-nowrap px-1 py-1"
                          >
                            Clear
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="max-h-40 overflow-y-auto p-2 bg-white rounded-lg border border-slate-200">
                      {filteredCurrencies.length === 0 ? (
                        <div className="text-center py-4 text-xs text-slate-400">
                          No currencies match "{currencySearch}".
                        </div>
                      ) : (
                        <div className="flex flex-wrap gap-1">
                          {filteredCurrencies.map(c => {
                            const isFav = (form.favorite_currencies || []).includes(c.code)
                            return (
                              <button
                                key={c.code}
                                type="button"
                                onClick={() => toggleFavorite(c.code)}
                                title={`${c.code} — ${c.name}`}
                                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium transition-all ${
                                  isFav
                                    ? 'bg-navy-800 text-white shadow-xs border border-navy-800 font-semibold'
                                    : 'bg-slate-50 border border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-100'
                                }`}
                              >
                                {isFav && <Check size={11} className="stroke-[3]" />}
                                <span>{c.code}</span>
                              </button>
                            )
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Fiscal Year Start Month">
                      <select value={form.fiscal_year_start_month} onChange={e => update('fiscal_year_start_month', Number(e.target.value))} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                        {MONTH_NAMES.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
                      </select>
                    </Field>
                    <Field label="Website"><input value={form.website} onChange={e => update('website', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Phone"><input value={form.phone} onChange={e => update('phone', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                    <Field label="Email"><input type="email" value={form.email} onChange={e => update('email', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                  </div>

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

              )}

              {tab === 'Address' && (
                <>
                  <Field label="Address"><input value={form.address} onChange={e => update('address', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="City"><input value={form.city} onChange={e => update('city', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                    <Field label="Country"><input value={form.country} onChange={e => update('country', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                  </div>
                </>
              )}

              {tab === 'Bank Details' && (
                <>
                  <p className="text-xs text-slate-400 mb-2">You can add up to two bank accounts and choose which one appears on invoices.</p>
                  
                  <div className="bg-slate-50 border border-slate-100 p-3 rounded-lg mb-4">
                    <h3 className="font-semibold text-slate-700 text-sm mb-3">Primary Bank Account (Bank 1)</h3>
                    <Field label="Bank Name"><input value={form.bank_name} onChange={e => update('bank_name', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" /></Field>
                    <Field label="Account Holder"><input value={form.bank_account_holder} onChange={e => update('bank_account_holder', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" /></Field>
                    <div className="grid grid-cols-2 gap-3">
                      <Field label="Account Number"><input value={form.bank_account_number} onChange={e => update('bank_account_number', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" /></Field>
                      <Field label="SWIFT Code"><input value={form.bank_swift_code} onChange={e => update('bank_swift_code', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" /></Field>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <Field label="Branch"><input value={form.bank_branch} onChange={e => update('bank_branch', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" /></Field>
                      <Field label="IFSC Code (Optional)"><input value={form.bank_ifsc_code} onChange={e => update('bank_ifsc_code', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" /></Field>
                    </div>
                  </div>

                  <div className="bg-slate-50 border border-slate-100 p-3 rounded-lg">
                    <h3 className="font-semibold text-slate-700 text-sm mb-3">Secondary Bank Account (Bank 2)</h3>
                    <Field label="Bank Name"><input value={form.bank2_name} onChange={e => update('bank2_name', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" /></Field>
                    <Field label="Account Holder"><input value={form.bank2_account_holder} onChange={e => update('bank2_account_holder', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" /></Field>
                    <div className="grid grid-cols-2 gap-3">
                      <Field label="Account Number"><input value={form.bank2_account_number} onChange={e => update('bank2_account_number', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" /></Field>
                      <Field label="SWIFT Code"><input value={form.bank2_swift_code} onChange={e => update('bank2_swift_code', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" /></Field>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <Field label="Branch"><input value={form.bank2_branch} onChange={e => update('bank2_branch', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" /></Field>
                      <Field label="IFSC Code (Optional)"><input value={form.bank2_ifsc_code} onChange={e => update('bank2_ifsc_code', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white" /></Field>
                    </div>
                  </div>
                </>

              )}

              {tab === 'Invoice Settings' && (
                <>
                  <div className="bg-gold-50 border border-gold-100 rounded-lg p-3">
                    <p className="text-xs font-semibold text-slate-600 mb-2">LUT (Export Under Bond/LUT) Defaults</p>
                    <div className="grid grid-cols-2 gap-3">
                      <Field label="LUT Acknowledgement Number"><input value={form.lut_ack_number} onChange={e => update('lut_ack_number', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                      <Field label="LUT Expiry Date"><input type="date" value={form.lut_expiry_date} onChange={e => update('lut_expiry_date', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-2">Pre-fills onto every new sales invoice; can be toggled off per-invoice.</p>
                  </div>
                  <Field label="Default Payment Terms"><textarea value={form.default_payment_terms} onChange={e => update('default_payment_terms', e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                  <Field label="Default Notes"><textarea value={form.default_notes} onChange={e => update('default_notes', e.target.value)} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                  <Field label="Default Thank You Note"><input value={form.default_thank_you_note} onChange={e => update('default_thank_you_note', e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></Field>
                </>

              )}

              {error && <p className="text-xs text-red-600">{error}</p>}

              <div className="flex gap-2 pt-2 sticky bottom-0 bg-white pb-1">
                <button type="button" onClick={() => setModalOpen(false)} className="flex-1 border border-slate-300 rounded-lg py-2 text-sm font-medium text-slate-600">Cancel</button>
                <button type="submit" disabled={saving} className="flex-1 bg-navy-600 hover:bg-navy-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60">
                  {saving ? 'Saving…' : editingCompany ? 'Save Company' : 'Create Company'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

function Field({ label, children }) {
  return (
    <div>
      <label className="text-xs font-medium text-slate-500">{label}</label>
      <div className="mt-1">{children}</div>
    </div>
  )
}
